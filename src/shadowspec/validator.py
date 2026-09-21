"""Deterministic validation for server-owned fixture variants only."""

from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import uuid
from dataclasses import dataclass
from pathlib import Path


ALLOWED_CANDIDATES = frozenset({"baseline", "bad", "narrow"})
OUTPUT_LIMIT = 4000
EXECUTION_TIMEOUT_SECONDS = 3


class CandidateNotAllowed(ValueError):
    """Raised when a candidate is outside the server-owned allowlist."""


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


_RUNNER = r'''import importlib.util, json, sqlite3, sys
from pathlib import Path

class _BoundedTextIO:
    def __init__(self, stream, limit=4000):
        self._stream = stream
        self._limit = limit
        self._written = 0

    def write(self, value):
        encoded = value.encode("utf-8", "replace")
        remaining = max(0, self._limit - self._written)
        if remaining:
            self._stream.write(encoded[:remaining].decode("utf-8", "ignore"))
        self._written += len(encoded)
        return len(value)

    def flush(self):
        self._stream.flush()

sys.stdout = _BoundedTextIO(sys.stdout)
sys.stderr = _BoundedTextIO(sys.stderr)
source, db_path = Path(sys.argv[1]), Path(sys.argv[2])
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
print(json.dumps(checks, sort_keys=True))
'''


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

    with tempfile.TemporaryDirectory(prefix="shadowspec-") as temporary:
        workspace = Path(temporary)
        copied_source = workspace / "candidate.py"
        try:
            shutil.copyfile(canonical_source, copied_source)
            completed = subprocess.run(
                [sys.executable, "-I", "-c", _RUNNER, str(copied_source), str(workspace / "audit.db")],
                cwd=workspace,
                capture_output=True,
                text=True,
                timeout=EXECUTION_TIMEOUT_SECONDS,
                check=False,
                env={},
            )
        except subprocess.TimeoutExpired:
            return _error_run(
                candidate, source_hash, provenance,
                failed_check="candidate execution timed out",
                code="timeout", message="candidate execution timed out",
                details={"timeout_seconds": EXECUTION_TIMEOUT_SECONDS},
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
        checks = json.loads(completed.stdout)
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
