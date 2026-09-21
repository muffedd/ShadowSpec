from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

import pytest

from shadowspec.validator import CandidateNotAllowed, validate_candidate


FIXTURE_ROOT = Path(__file__).parents[1] / "fixtures" / "legacy_orders"


def test_bad_candidate_is_rejected_for_preserved_case_behavior():
    run = validate_candidate("bad", FIXTURE_ROOT)
    assert run.verdict == "rejected"
    assert run.characterization_passed is False
    assert "lowercase code remains invalid with complete pricing result and audit row" in run.failed_checks
    assert run.acceptance_passed is True


def test_narrow_candidate_preserves_contract_and_meets_request():
    run = validate_candidate("narrow", FIXTURE_ROOT)
    assert run.verdict == "accepted"
    assert run.characterization_passed is True
    assert run.acceptance_passed is True
    assert run.failed_checks == ()

    checks = json.loads(run.output)["checks"]
    assert [check["name"] for check in checks] == [
        "uppercase code preserves complete pricing result and audit row",
        "lowercase code remains invalid with complete pricing result and audit row",
        "unknown code keeps complete full-price result and audit row",
        "negative subtotal raises validation error without audit write",
        "surrounding whitespace is accepted with complete pricing result and audit row",
    ]


def test_validator_rejects_candidate_with_incomplete_pricing_result(tmp_path):
    fixture_root = tmp_path / "legacy_orders"
    shutil.copytree(FIXTURE_ROOT, fixture_root)
    source = fixture_root / "variants" / "narrow.py"
    source.write_text(
        source.read_text().replace(
            'return {\n'
            '        "subtotal_cents": subtotal,\n'
            '        "discount_cents": discount,\n'
            '        "total_cents": total,\n'
            '    }',
            'return {"total_cents": total}',
        )
    )

    run = validate_candidate("narrow", fixture_root)

    assert run.verdict == "rejected"
    assert run.characterization_passed is False
    assert "uppercase code preserves complete pricing result and audit row" in run.failed_checks


def test_validator_rejects_candidate_that_writes_for_negative_subtotal(tmp_path):
    fixture_root = tmp_path / "legacy_orders"
    shutil.copytree(FIXTURE_ROOT, fixture_root)
    source = fixture_root / "variants" / "narrow.py"
    source.write_text(
        source.read_text().replace(
            '    if subtotal < 0:\n        raise ValueError("subtotal_cents must be non-negative")\n\n',
            '',
        )
    )

    run = validate_candidate("narrow", fixture_root)

    assert run.verdict == "rejected"
    assert run.characterization_passed is False
    assert "negative subtotal raises validation error without audit write" in run.failed_checks


def test_baseline_preserves_contract_but_does_not_meet_request():
    run = validate_candidate("baseline", FIXTURE_ROOT)
    assert run.verdict == "rejected"
    assert run.characterization_passed is True
    assert run.acceptance_passed is False
    assert "surrounding whitespace is accepted with complete pricing result and audit row" in run.failed_checks


def test_run_has_stable_evidence_without_host_paths():
    first = validate_candidate("narrow", FIXTURE_ROOT)
    second = validate_candidate("narrow", FIXTURE_ROOT)
    assert first.source_sha256 == second.source_sha256
    assert first.baseline_sha256 == second.baseline_sha256
    assert first.validator_sha256 == second.validator_sha256
    assert first.runner_sha256 == second.runner_sha256
    assert len(first.source_sha256) == 64
    assert first.run_id != second.run_id
    assert str(FIXTURE_ROOT.parent) not in first.output
    assert len(first.output) <= 4000


def test_run_exposes_candidate_baseline_and_execution_provenance():
    run = validate_candidate("narrow", FIXTURE_ROOT)

    assert run.candidate == "narrow"
    assert run.candidate_sha256 == run.source_sha256
    assert run.baseline_sha256 != run.source_sha256
    assert all(len(value) == 64 for value in (
        run.baseline_sha256,
        run.validator_sha256,
        run.runner_sha256,
    ))


def test_unknown_candidate_is_rejected_before_file_access():
    with pytest.raises(CandidateNotAllowed, match="Unsupported candidate"):
        validate_candidate("../../secret", FIXTURE_ROOT)


def test_fixture_root_must_contain_expected_variants(tmp_path):
    with pytest.raises(ValueError, match="fixture root is invalid"):
        validate_candidate("narrow", tmp_path)


def test_timeout_is_returned_as_bounded_structured_evidence(monkeypatch):
    def raise_timeout(*args, **kwargs):
        raise subprocess.TimeoutExpired(kwargs.get("args", args[0]), kwargs["timeout"])

    monkeypatch.setattr(subprocess, "run", raise_timeout)

    run = validate_candidate("narrow", FIXTURE_ROOT)

    assert run.verdict == "error"
    assert run.characterization_passed is False
    assert run.acceptance_passed is False
    assert run.failed_checks == ("candidate execution timed out",)
    assert json.loads(run.output) == {
        "error": {
            "code": "timeout",
            "message": "candidate execution timed out",
            "timeout_seconds": 3,
        }
    }
    assert str(FIXTURE_ROOT) not in run.output


def test_unexpected_subprocess_exception_is_normalized(monkeypatch):
    def raise_unexpected(*args, **kwargs):
        raise RuntimeError("private source path /host/candidate.py")

    monkeypatch.setattr(subprocess, "run", raise_unexpected)

    run = validate_candidate("narrow", FIXTURE_ROOT)

    assert run.verdict == "error"
    assert run.failed_checks == ("candidate execution failed",)
    assert json.loads(run.output) == {
        "error": {
            "code": "execution_error",
            "message": "candidate execution failed",
        }
    }
    assert "/host/candidate.py" not in run.output


def test_execution_errors_do_not_expose_raw_stderr_or_source(monkeypatch):
    source_marker = "SECRET_SOURCE_SHOULD_NOT_REACH_UI"
    path_marker = "/host/private/candidate.py"

    def failed_process(*args, **kwargs):
        return subprocess.CompletedProcess(
            args=args[0],
            returncode=1,
            stdout="",
            stderr=f"Traceback: {path_marker} {source_marker}",
        )

    monkeypatch.setattr(subprocess, "run", failed_process)

    run = validate_candidate("narrow", FIXTURE_ROOT)

    assert run.verdict == "error"
    assert run.failed_checks == ("candidate execution failed",)
    assert json.loads(run.output) == {
        "error": {
            "code": "execution_failed",
            "message": "candidate execution failed",
            "exit_code": 1,
        }
    }
    assert source_marker not in run.output
    assert path_marker not in run.output


def test_runner_bounds_candidate_output_before_result_parsing(tmp_path, monkeypatch):
    fixture_root = tmp_path / "legacy_orders"
    shutil.copytree(FIXTURE_ROOT, fixture_root)
    source = fixture_root / "variants" / "narrow.py"
    source.write_text(
        source.read_text(encoding="utf-8").replace(
            "from __future__ import annotations\n",
            "from __future__ import annotations\n\nprint(\"candidate output that must be bounded\" * 10000)\n",
        ),
        encoding="utf-8",
    )

    real_run = subprocess.run
    observed = {}

    def run_and_record(*args, **kwargs):
        completed = real_run(*args, **kwargs)
        observed["stdout_bytes"] = len(completed.stdout.encode("utf-8"))
        observed["stderr_bytes"] = len(completed.stderr.encode("utf-8"))
        return completed

    monkeypatch.setattr(subprocess, "run", run_and_record)

    run = validate_candidate("narrow", fixture_root)

    assert run.verdict == "error"
    assert run.failed_checks == ("candidate execution returned invalid results",)
    assert observed["stdout_bytes"] <= 4000
    assert observed["stderr_bytes"] <= 4000
    assert len(run.output) <= 4000
    assert "candidate output that must be bounded" not in run.output


def test_candidate_symlink_must_remain_under_variants_root(tmp_path):
    fixture_root = tmp_path / "fixture"
    variants = fixture_root / "variants"
    variants.mkdir(parents=True)
    outside = tmp_path / "outside.py"
    outside.write_text("SECRET_SOURCE_SHOULD_NOT_BE_EXECUTED\n", encoding="utf-8")
    (variants / "baseline.py").write_text("pass\n", encoding="utf-8")
    (variants / "narrow.py").symlink_to(outside)

    with pytest.raises(ValueError, match="candidate source is outside allowlisted variants"):
        validate_candidate("narrow", fixture_root)
