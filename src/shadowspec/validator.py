"""Deterministic validation for server-owned fixture variants only."""

from __future__ import annotations

import hashlib
import json
import os
import selectors
import signal
import subprocess
import sys
import tempfile
import threading
import time
import uuid
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator


ALLOWED_CANDIDATES = frozenset({"baseline", "bad", "narrow"})
AUDITED_VARIANT_SHA256 = {
    "baseline.py": "8060c930143deb28599c84bfb3257324ff3de01620b509ada8b0028558ee3f3a",
    "bad.py": "bb87bac06fb61f7fe5b9d2f64cae41d6f4b792b36ebe4e86bb3a748d69db61a4",
    "narrow.py": "0dcf67131a0282d30a6cfa18bbae8be7fdbc0bd6b5e2dd16c50c37ba5a98d5b0",
}
OUTPUT_LIMIT = 4000
EXECUTION_TIMEOUT_SECONDS = 3
_RESULT_LIMIT = OUTPUT_LIMIT
_EXPECTED_CHECKS = (
    ("uppercase code preserves complete pricing result and audit row", "characterization"),
    ("lowercase code remains invalid with complete pricing result and audit row", "characterization"),
    ("unknown code keeps complete full-price result and audit row", "characterization"),
    ("negative subtotal raises validation error without audit write", "characterization"),
    ("surrounding whitespace is accepted with complete pricing result and audit row", "acceptance"),
)
_SUBPROCESS_LOCK = threading.Lock()


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


_RUNNER = r'''import importlib.util, json, os, sqlite3, sys
from pathlib import Path

_json_dumps = json.dumps
_os_close = os.close
_os_exit = os._exit
_os_write = os.write
source, db_path, result_fd = Path(sys.argv[1]), Path(sys.argv[2]), int(sys.argv[3])
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
for case in cases:
    if db_path.exists(): db_path.unlink()
    passed=False
    if "error" in case:
        try:
            module.process_order(case["order"], db_path)
        except Exception as error:
            passed=(type(error).__name__==case["error"] and str(error)==case["message"] and not db_path.exists())
    else:
        try:
            result=module.process_order(case["order"], db_path)
            with sqlite3.connect(db_path) as connection:
                row=connection.execute("select code,total_cents from discount_audit").fetchone()
            passed=(result==case["result"] and row==case["audit"])
        except Exception:
            passed=False
    checks.append({"name":case["name"],"kind":case["kind"],"passed":passed})
payload = _json_dumps(checks, sort_keys=True).encode("utf-8")
while payload:
    written = _os_write(result_fd, payload)
    payload = payload[written:]
_os_close(result_fd)
_os_exit(0)
'''


@dataclass(frozen=True)
class _CompletedExecution:
    returncode: int
    result: bytes


@contextmanager
def _linux_subreaper() -> Iterator[None]:
    """Temporarily adopt same-group descendants so they can be reaped."""

    if sys.platform != "linux":
        yield
        return

    # prctl is Linux-specific. Failure only removes the explicit orphan-reaping
    # enhancement; process-group termination remains in force.
    libc = None
    changed = False
    try:
        import ctypes

        libc = ctypes.CDLL(None, use_errno=True)
        previous = ctypes.c_int()
        available = libc.prctl(37, ctypes.byref(previous), 0, 0, 0) == 0
        changed = available and previous.value == 0
        if changed:
            available = libc.prctl(36, 1, 0, 0, 0) == 0
    except Exception:
        available = False

    if not available:
        yield
        return

    try:
        yield
    finally:
        if changed and libc is not None:
            libc.prctl(36, 0, 0, 0, 0)


def _kill_and_reap_process_group(process: subprocess.Popen[bytes]) -> int:
    """Stop the isolated process group and reap adopted Linux descendants."""

    if os.name == "posix":
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        except OSError:
            if process.returncode is None:
                process.kill()
    elif process.returncode is None:
        process.kill()

    try:
        returncode = process.wait(timeout=1)
    except subprocess.TimeoutExpired:
        process.kill()
        returncode = process.wait()

    if sys.platform == "linux":
        deadline = time.monotonic() + 1
        while True:
            try:
                descendant, _ = os.waitpid(-process.pid, os.WNOHANG)
            except ChildProcessError:
                break
            if descendant:
                continue
            if time.monotonic() >= deadline:
                break
            time.sleep(0.005)
    return returncode


def _read_bounded_process(
    process: subprocess.Popen[bytes], result_fd: int, timeout: float
) -> bytes:
    selector = selectors.DefaultSelector()
    streams = {
        "stdout": process.stdout,
        "stderr": process.stderr,
        "result": result_fd,
    }
    counts = {"stdout": 0, "stderr": 0, "result": 0}
    result = bytearray()
    deadline = time.monotonic() + timeout
    try:
        for name, stream in streams.items():
            if stream is None:
                continue
            selector.register(stream, selectors.EVENT_READ, name)

        while selector.get_map():
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise _ExecutionTimedOut
            events = selector.select(remaining)
            if not events:
                raise _ExecutionTimedOut
            for key, _ in events:
                name = key.data
                limit = _RESULT_LIMIT if name == "result" else OUTPUT_LIMIT
                read_size = min(65536, limit - counts[name] + 1)
                try:
                    chunk = os.read(key.fd, read_size)
                except BlockingIOError:
                    continue
                if not chunk:
                    selector.unregister(key.fileobj)
                    continue
                counts[name] += len(chunk)
                if counts[name] > limit:
                    if name == "result":
                        raise _ResultLimitExceeded
                    raise _OutputLimitExceeded(name)
                if name == "result":
                    result.extend(chunk)
        return bytes(result)
    finally:
        selector.close()


def _execute_runner(arguments: list[str], workspace: Path) -> _CompletedExecution:
    result_read, result_write = os.pipe()
    try:
        with _SUBPROCESS_LOCK:
            with _linux_subreaper():
                try:
                    process = subprocess.Popen(
                        [*arguments, str(result_write)],
                        cwd=workspace,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        env={},
                        start_new_session=True,
                        pass_fds=(result_write,),
                    )
                finally:
                    os.close(result_write)

                try:
                    result = _read_bounded_process(
                        process, result_read, EXECUTION_TIMEOUT_SECONDS
                    )
                finally:
                    try:
                        returncode = _kill_and_reap_process_group(process)
                    finally:
                        if process.stdout is not None:
                            process.stdout.close()
                        if process.stderr is not None:
                            process.stderr.close()
    finally:
        os.close(result_read)
    return _CompletedExecution(returncode=returncode, result=result)


def _parse_check_results(payload: bytes) -> list[dict[str, object]]:
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


def validate_candidate(candidate: str, fixture_root: Path) -> ValidationRun:
    if candidate not in ALLOWED_CANDIDATES:
        raise CandidateNotAllowed(f"Unsupported candidate: {candidate}")

    fixture_root = Path(fixture_root)
    variants = fixture_root / "variants"
    source = variants / f"{candidate}.py"
    baseline = variants / "baseline.py"
    if not variants.is_dir() or variants.is_symlink() or not source.is_file() or not baseline.is_file():
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
                    str(workspace / "audit.db"),
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
