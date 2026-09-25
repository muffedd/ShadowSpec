"""Deterministic validation for server-owned fixture variants only.

Event-window implementation (bob-2.0-build-2026-09-25).

Architecture
------------
* Characterization runner   – captures named behavioral observations from the
  bundled legacy_orders fixture (4 preservation checks).
* Acceptance checker        – tests the requested delta (whitespace tolerance
  in SAVE10) as a separate named check.
* Differential validator    – runs both via a sandboxed subprocess, parses the
  result, and returns a reject/accept verdict with named check results.

Separation rule
---------------
A patch that passes the acceptance check but silently changes a preserved
characterization check MUST be rejected.  strip().upper() changes the lowercase
case-sensitivity check → rejected.  strip() only → accepted.

Cross-platform execution
------------------------
The runner writes JSON results to a dedicated temp file (``result_path``)
rather than an inherited file-descriptor pipe, so the same code runs on
Windows (which does not support ``pass_fds``) and Linux/macOS.
"""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import tempfile
import threading
import time
import uuid
from dataclasses import dataclass
from pathlib import Path


# ---------------------------------------------------------------------------
# Allowlist and integrity manifest
# ---------------------------------------------------------------------------

ALLOWED_CANDIDATES = frozenset({"baseline", "bad", "narrow"})

# SHA-256 of the server-owned, audited fixture variants.
# These are the integrity boundary: if the file on disk does not match,
# execution is refused before any subprocess is spawned.
AUDITED_VARIANT_SHA256 = {
    "baseline.py": "7f14c9b5e8d821b5c00fd2ab67a6c97ffb40a22c2f5b30a5d2633a1fa0c1e95f",
    "bad.py": "99164a7188f9d44db17d8f48e3ffa364cc9b410c286fc8a762c6f74685ad3d0a",
    "narrow.py": "ef9ad8a069dbc9427702613c04fafb03fa6ed2dd2173f20b822dbaff0a02e307",
}

OUTPUT_LIMIT = 4000
EXECUTION_TIMEOUT_SECONDS = 3
_RESULT_LIMIT = OUTPUT_LIMIT

# Ordered declaration of all expected checks: (name, kind).
# The runner produces them in this exact order; the parser enforces it.
_EXPECTED_CHECKS = (
    ("uppercase code preserves complete pricing result and audit row", "characterization"),
    ("lowercase code remains invalid with complete pricing result and audit row", "characterization"),
    ("unknown code keeps complete full-price result and audit row", "characterization"),
    ("negative subtotal raises validation error without audit write", "characterization"),
    ("surrounding whitespace is accepted with complete pricing result and audit row", "acceptance"),
)

_SUBPROCESS_LOCK = threading.Lock()


# ---------------------------------------------------------------------------
# Exception hierarchy
# ---------------------------------------------------------------------------

class CandidateNotAllowed(ValueError):
    """Raised when a candidate is outside the server-owned allowlist."""


class _ExecutionTimedOut(Exception):
    """Internal signal for a bounded execution timeout."""


class _OutputLimitExceeded(Exception):
    """Internal signal for a child output stream exceeding its byte cap."""

    def __init__(self, stream: str) -> None:
        super().__init__(stream)
        self.stream = stream


class _ResultLimitExceeded(Exception):
    """Internal signal for an oversized control result."""


# ---------------------------------------------------------------------------
# ValidationRun dataclass
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class ValidationRun:
    run_id: str
    candidate: str
    verdict: str
    characterization_passed: bool
    acceptance_passed: bool
    failed_checks: tuple[str, ...]
    source_sha256: str
    output: str
    baseline_sha256: str = ""
    validator_sha256: str = ""
    runner_sha256: str = ""

    @property
    def candidate_sha256(self) -> str:
        """Hash of the selected candidate source (legacy alias included)."""
        return self.source_sha256

    @property
    def provenance(self) -> dict[str, str]:
        """Stable inputs that identify the validator's verdict."""
        return {
            "candidate": self.candidate,
            "candidate_sha256": self.candidate_sha256,
            "baseline": "baseline",
            "baseline_sha256": self.baseline_sha256,
            "validator_sha256": self.validator_sha256,
            "runner_sha256": self.runner_sha256,
        }


# ---------------------------------------------------------------------------
# Embedded runner script
#
# The runner is executed in a subprocess with -I (isolated mode).  It writes
# check results as JSON to ``result_path`` (sys.argv[3]), which the parent
# process reads back.  Stdout and stderr from the candidate are captured and
# discarded within the OUTPUT_LIMIT; they cannot forge the result channel.
# ---------------------------------------------------------------------------

_RUNNER = r'''import importlib.util, json, os, sqlite3, sys
from pathlib import Path

_json_dumps = json.dumps
_os_exit = os._exit
source, work_dir, result_path = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
spec = importlib.util.spec_from_file_location("candidate", source)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
cases = [
  {"name":"uppercase code preserves complete pricing result and audit row", "kind":"characterization", "order":{"subtotal_cents":10000,"discount_code":"SAVE10"}, "result":{"subtotal_cents":10000,"discount_cents":1000,"total_cents":9000}, "audit": ("SAVE10",9000)},
  {"name":"lowercase code remains invalid with complete pricing result and audit row", "kind":"characterization", "order":{"subtotal_cents":10000,"discount_code":"save10"}, "result":{"subtotal_cents":10000,"discount_cents":0,"total_cents":10000}, "audit": ("save10",10000)},
  {"name":"unknown code keeps complete full-price result and audit row", "kind":"characterization", "order":{"subtotal_cents":5000,"discount_code":"NONE"}, "result":{"subtotal_cents":5000,"discount_cents":0,"total_cents":5000}, "audit": ("NONE",5000)},
  {"name":"negative subtotal raises validation error without audit write", "kind":"characterization", "order":{"subtotal_cents":-1,"discount_code":"SAVE10"}, "error":"ValueError", "message":"subtotal_cents must be non-negative"},
  {"name":"surrounding whitespace is accepted with complete pricing result and audit row", "kind":"acceptance", "order":{"subtotal_cents":10000,"discount_code":" SAVE10 "}, "result":{"subtotal_cents":10000,"discount_cents":1000,"total_cents":9000}, "audit": (" SAVE10 ",9000)},
]
checks=[]
for index,case in enumerate(cases):
    db_path=work_dir/f"audit_{index}.db"
    passed=False
    if "error" in case:
        try:
            module.process_order(case["order"], db_path)
        except Exception as error:
            passed=(type(error).__name__==case["error"] and str(error)==case["message"] and not db_path.exists())
    else:
        try:
            result=module.process_order(case["order"], db_path)
            connection=sqlite3.connect(db_path)
            try:
                row=connection.execute("select code,total_cents from discount_audit").fetchone()
            finally:
                connection.close()
            passed=(result==case["result"] and row==tuple(case["audit"]))
        except Exception:
            passed=False
    checks.append({"name":case["name"],"kind":case["kind"],"passed":passed})
payload = _json_dumps(checks, sort_keys=True).encode("utf-8")
result_path.write_bytes(payload)
_os_exit(0)
'''


# ---------------------------------------------------------------------------
# Subprocess execution
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class _CompletedExecution:
    returncode: int
    result: bytes


def _drain_stream(
    stream: "subprocess.IO[bytes] | None",
    counts: dict[str, int],
    key: str,
    limit: int,
    exception_holder: list[Exception],
    kill_event: "threading.Event",
) -> None:
    """Read a subprocess stream in a thread, enforcing a byte cap.

    When the limit is exceeded, adds an :class:`_OutputLimitExceeded` to
    ``exception_holder`` and sets ``kill_event`` so the parent can terminate
    the subprocess promptly.
    """
    if stream is None:
        return
    try:
        while not kill_event.is_set():
            chunk = stream.read(65536)
            if not chunk:
                break
            counts[key] += len(chunk)
            if counts[key] > limit:
                exception_holder.append(_OutputLimitExceeded(key))
                kill_event.set()
                return
    except OSError:
        pass


def _execute_runner(arguments: list[str], workspace: Path) -> _CompletedExecution:
    """Run ``arguments`` in a subprocess and capture the result file.

    The result is written by the runner to ``workspace/result.json``.
    Stdout and stderr are drained concurrently and discarded (subject to
    OUTPUT_LIMIT); they cannot forge the result channel.
    """
    result_path = workspace / "result.json"
    full_arguments = [*arguments, str(result_path)]

    counts: dict[str, int] = {"stdout": 0, "stderr": 0}
    exception_holder: list[Exception] = []
    kill_event = threading.Event()

    popen_kwargs: dict[str, object] = {
        "cwd": workspace,
        "stdout": subprocess.PIPE,
        "stderr": subprocess.PIPE,
        "env": {},
    }
    # Use start_new_session on POSIX for process-group isolation.
    if os.name == "posix":
        popen_kwargs["start_new_session"] = True

    with _SUBPROCESS_LOCK:
        try:
            process = subprocess.Popen(full_arguments, **popen_kwargs)  # type: ignore[arg-type]
        except (OSError, subprocess.SubprocessError) as exc:
            raise exc

        stdout_thread = threading.Thread(
            target=_drain_stream,
            args=(process.stdout, counts, "stdout", OUTPUT_LIMIT, exception_holder, kill_event),
            daemon=True,
        )
        stderr_thread = threading.Thread(
            target=_drain_stream,
            args=(process.stderr, counts, "stderr", OUTPUT_LIMIT, exception_holder, kill_event),
            daemon=True,
        )
        stdout_thread.start()
        stderr_thread.start()

        deadline = time.monotonic() + EXECUTION_TIMEOUT_SECONDS
        timed_out = False
        try:
            # Poll so we can react to output-limit signals without waiting the
            # full timeout when a stream exceeds its byte cap.
            while True:
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    timed_out = True
                    break
                if kill_event.is_set():
                    break
                try:
                    process.wait(timeout=min(0.05, remaining))
                    break  # process exited normally
                except subprocess.TimeoutExpired:
                    continue
        finally:
            _terminate_process(process)
            if process.stdout is not None:
                process.stdout.close()
            if process.stderr is not None:
                process.stderr.close()

        stdout_thread.join(timeout=1)
        stderr_thread.join(timeout=1)

    if timed_out and not exception_holder:
        raise _ExecutionTimedOut

    if exception_holder:
        exc = exception_holder[0]
        if isinstance(exc, _OutputLimitExceeded):
            raise exc
        raise exc

    if timed_out:
        raise _ExecutionTimedOut

    # Read the result file written by the runner.
    if result_path.exists():
        result_bytes = result_path.read_bytes()
        if len(result_bytes) > _RESULT_LIMIT:
            raise _ResultLimitExceeded
    else:
        result_bytes = b""

    return _CompletedExecution(returncode=process.returncode, result=result_bytes)


def _terminate_process(process: "subprocess.Popen[bytes]") -> None:
    """Terminate the process and its group if possible."""
    if os.name == "posix":
        import signal
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except (ProcessLookupError, OSError):
            pass
    else:
        try:
            process.kill()
        except OSError:
            pass
    try:
        process.wait(timeout=1)
    except subprocess.TimeoutExpired:
        pass


# ---------------------------------------------------------------------------
# Check-result parser
# ---------------------------------------------------------------------------

def _parse_check_results(payload: bytes) -> list[dict[str, object]]:
    """Parse and strictly validate the JSON check results from the runner."""

    def reject_duplicate_keys(pairs: list[tuple[str, object]]) -> dict[str, object]:
        result: dict[str, object] = {}
        for key, value in pairs:
            if key in result:
                raise ValueError("invalid check results")
            result[key] = value
        return result

    def reject_non_json_constant(_: str) -> object:
        raise ValueError("invalid check results")

    try:
        checks = json.loads(
            payload.decode("utf-8"),
            object_pairs_hook=reject_duplicate_keys,
            parse_constant=reject_non_json_constant,
        )
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError):
        raise ValueError("invalid check results") from None

    if type(checks) is not list or len(checks) != len(_EXPECTED_CHECKS):
        raise ValueError("invalid check results")
    for item, (expected_name, expected_kind) in zip(checks, _EXPECTED_CHECKS):
        if (
            type(item) is not dict
            or set(item) != {"name", "kind", "passed"}
            or item["name"] != expected_name
            or item["kind"] != expected_kind
            or type(item["passed"]) is not bool
        ):
            raise ValueError("invalid check results")
    return checks


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def validate_candidate(candidate: str, fixture_root: Path) -> ValidationRun:
    """Validate a server-owned candidate against characterization and acceptance checks.

    Returns a :class:`ValidationRun` whose verdict is:

    * ``"accepted"``  – all characterization checks passed *and* the
      acceptance check passed (narrow: strip() only).
    * ``"rejected"``  – execution completed but at least one check failed
      (bad: strip().upper() breaks the lowercase case-sensitivity check;
      baseline: acceptance check fails because whitespace is not trimmed).
    * ``"error"``     – execution could not complete (integrity failure,
      timeout, output-limit, or subprocess error).
    """
    if candidate not in ALLOWED_CANDIDATES:
        raise CandidateNotAllowed(f"Unsupported candidate: {candidate}")

    fixture_root = Path(fixture_root)
    variants = fixture_root / "variants"
    source = variants / f"{candidate}.py"
    baseline = variants / "baseline.py"

    if (
        not variants.is_dir()
        or variants.is_symlink()
        or not source.is_file()
        or not baseline.is_file()
    ):
        raise ValueError("fixture root is invalid: expected audited variants")

    variants_root = variants.resolve(strict=True)
    if source.is_symlink() or baseline.is_symlink():
        raise ValueError("candidate source is outside allowlisted variants")
    try:
        canonical_source = source.resolve(strict=True)
        canonical_source.relative_to(variants_root)
        canonical_baseline = baseline.resolve(strict=True)
        canonical_baseline.relative_to(variants_root)
    except (OSError, ValueError):
        raise ValueError("candidate source is outside allowlisted variants") from None
    if not canonical_source.is_file() or not canonical_baseline.is_file():
        raise ValueError("fixture root is invalid: expected audited variants")

    try:
        source_bytes = canonical_source.read_bytes()
        baseline_bytes = canonical_baseline.read_bytes()
    except OSError:
        raise ValueError("fixture root is invalid: expected audited variants") from None

    source_hash = hashlib.sha256(source_bytes).hexdigest()
    baseline_hash = hashlib.sha256(baseline_bytes).hexdigest()
    validator_hash = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    runner_hash = hashlib.sha256(_RUNNER.encode("utf-8")).hexdigest()

    provenance = {
        "baseline_sha256": baseline_hash,
        "validator_sha256": validator_hash,
        "runner_sha256": runner_hash,
    }

    # Integrity check: refuse to execute if any audited file was modified.
    checked_hashes = {
        "baseline.py": baseline_hash,
        f"{candidate}.py": source_hash,
    }
    mismatched_files = sorted(
        filename
        for filename, actual_hash in checked_hashes.items()
        if actual_hash != AUDITED_VARIANT_SHA256[filename]
    )
    if mismatched_files:
        return _error_run(
            candidate,
            source_hash,
            provenance,
            failed_check="audited fixture integrity check failed",
            code="integrity_error",
            message="audited fixture integrity check failed",
            details={"files": mismatched_files},
        )

    with tempfile.TemporaryDirectory(prefix="shadowspec-") as temporary:
        workspace = Path(temporary)
        copied_source = workspace / "candidate.py"
        try:
            copied_source.write_bytes(source_bytes)
            completed = _execute_runner(
                [
                    sys.executable,
                    "-I",
                    "-c",
                    _RUNNER,
                    str(copied_source),
                    str(workspace),
                ],
                workspace,
            )
        except _ExecutionTimedOut:
            return _error_run(
                candidate, source_hash, provenance,
                failed_check="candidate execution timed out",
                code="timeout", message="candidate execution timed out",
                details={"timeout_seconds": EXECUTION_TIMEOUT_SECONDS},
            )
        except _OutputLimitExceeded as error:
            return _error_run(
                candidate, source_hash, provenance,
                failed_check="candidate execution exceeded output limit",
                code="output_limit",
                message="candidate execution exceeded output limit",
                details={"output_limit_bytes": OUTPUT_LIMIT, "stream": error.stream},
            )
        except _ResultLimitExceeded:
            return _error_run(
                candidate, source_hash, provenance,
                failed_check="candidate execution returned invalid results",
                code="invalid_output", message="candidate execution returned invalid results",
            )
        except (OSError, subprocess.SubprocessError):
            return _error_run(
                candidate, source_hash, provenance,
                failed_check="candidate execution failed",
                code="execution_error", message="candidate execution failed",
            )
        except Exception:
            return _error_run(
                candidate, source_hash, provenance,
                failed_check="candidate execution failed",
                code="execution_error", message="candidate execution failed",
            )

    if completed.returncode != 0:
        return _error_run(
            candidate, source_hash, provenance,
            failed_check="candidate execution failed",
            code="execution_failed", message="candidate execution failed",
            details={"exit_code": completed.returncode},
        )

    try:
        checks = _parse_check_results(completed.result)
        preserved = [item for item in checks if item["kind"] == "characterization"]
        acceptance = [item for item in checks if item["kind"] == "acceptance"]
        failed = tuple(item["name"] for item in checks if not item["passed"])
    except (TypeError, ValueError, KeyError, IndexError):
        return _error_run(
            candidate, source_hash, provenance,
            failed_check="candidate execution returned invalid results",
            code="invalid_output", message="candidate execution returned invalid results",
        )

    characterization_passed = all(item["passed"] for item in preserved)
    acceptance_passed = bool(acceptance) and all(item["passed"] for item in acceptance)
    verdict = "accepted" if characterization_passed and acceptance_passed else "rejected"
    summary = json.dumps({"checks": checks, "exit_code": completed.returncode}, sort_keys=True)
    return ValidationRun(
        run_id=uuid.uuid4().hex[:12], candidate=candidate, verdict=verdict,
        characterization_passed=characterization_passed,
        acceptance_passed=acceptance_passed, failed_checks=failed,
        source_sha256=source_hash, output=summary[:OUTPUT_LIMIT], **provenance,
    )


def _error_run(
    candidate: str,
    source_hash: str,
    provenance: dict[str, str],
    *,
    failed_check: str,
    code: str,
    message: str,
    details: dict[str, object] | None = None,
) -> ValidationRun:
    error: dict[str, object] = {"code": code, "message": message}
    if details:
        error.update(details)
    output = json.dumps({"error": error}, sort_keys=True)[:OUTPUT_LIMIT]
    return ValidationRun(
        run_id=uuid.uuid4().hex[:12], candidate=candidate, verdict="error",
        characterization_passed=False, acceptance_passed=False,
        failed_checks=(failed_check,), source_sha256=source_hash,
        output=output, **provenance,
    )
