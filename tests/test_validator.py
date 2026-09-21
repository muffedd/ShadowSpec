from __future__ import annotations

import json
import shutil
import subprocess
import sys
import time
from pathlib import Path

import pytest

import shadowspec.validator as validator
from shadowspec.validator import CandidateNotAllowed, validate_candidate


FIXTURE_ROOT = Path(__file__).parents[1] / "fixtures" / "legacy_orders"


EXPECTED_CHECKS = [
    {
        "name": "uppercase code preserves complete pricing result and audit row",
        "kind": "characterization",
        "passed": True,
    },
    {
        "name": "lowercase code remains invalid with complete pricing result and audit row",
        "kind": "characterization",
        "passed": True,
    },
    {
        "name": "unknown code keeps complete full-price result and audit row",
        "kind": "characterization",
        "passed": True,
    },
    {
        "name": "negative subtotal raises validation error without audit write",
        "kind": "characterization",
        "passed": True,
    },
    {
        "name": "surrounding whitespace is accepted with complete pricing result and audit row",
        "kind": "acceptance",
        "passed": True,
    },
]


def _execute_script(tmp_path: Path, script: str):
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    return validator._execute_runner(
        [sys.executable, "-I", "-c", script],
        workspace,
    )


def _run_modified_candidate(tmp_path: Path, old: str, new: str):
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    source = workspace / "candidate.py"
    source.write_text(
        (FIXTURE_ROOT / "variants" / "narrow.py")
        .read_text(encoding="utf-8")
        .replace(old, new),
        encoding="utf-8",
    )
    completed = validator._execute_runner(
        [
            sys.executable,
            "-I",
            "-c",
            validator._RUNNER,
            str(source),
            str(workspace / "audit.db"),
        ],
        workspace,
    )
    assert completed.returncode == 0
    return validator._parse_check_results(completed.result)


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


@pytest.mark.parametrize(
    ("modified_variant", "candidate"),
    [
        pytest.param("narrow", "narrow", id="selected-candidate"),
        pytest.param("baseline", "narrow", id="baseline"),
    ],
)
def test_modified_audited_source_is_rejected_before_execution(
    tmp_path, modified_variant, candidate
):
    fixture_root = tmp_path / "legacy_orders"
    shutil.copytree(FIXTURE_ROOT, fixture_root)
    marker = tmp_path / "candidate-executed"
    source = fixture_root / "variants" / f"{modified_variant}.py"
    source.write_text(
        source.read_text(encoding="utf-8").replace(
            "from __future__ import annotations\n",
            "from __future__ import annotations\n\n"
            f"__import__('pathlib').Path({str(marker)!r}).write_text("
            "'executed', encoding='utf-8')\n",
            1,
        ),
        encoding="utf-8",
    )

    run = validate_candidate(candidate, fixture_root)

    assert run.verdict == "error"
    assert run.characterization_passed is False
    assert run.acceptance_passed is False
    assert run.failed_checks == ("audited fixture integrity check failed",)
    assert json.loads(run.output) == {
        "error": {
            "code": "integrity_error",
            "files": [f"{modified_variant}.py"],
            "message": "audited fixture integrity check failed",
        }
    }
    assert not marker.exists()


def test_runner_rejects_candidate_with_incomplete_pricing_result(tmp_path):
    checks = _run_modified_candidate(
        tmp_path,
        'return {\n'
        '        "subtotal_cents": subtotal,\n'
        '        "discount_cents": discount,\n'
        '        "total_cents": total,\n'
        '    }',
        'return {"total_cents": total}',
    )

    assert checks[0] == {
        "name": "uppercase code preserves complete pricing result and audit row",
        "kind": "characterization",
        "passed": False,
    }


def test_runner_rejects_candidate_that_writes_for_negative_subtotal(tmp_path):
    checks = _run_modified_candidate(
        tmp_path,
        '    if subtotal < 0:\n'
        '        raise ValueError("subtotal_cents must be non-negative")\n\n',
        '',
    )

    assert checks[3] == {
        "name": "negative subtotal raises validation error without audit write",
        "kind": "characterization",
        "passed": False,
    }


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
    def time_out(*args, **kwargs):
        raise validator._ExecutionTimedOut

    monkeypatch.setattr(validator, "_execute_runner", time_out)
    monkeypatch.setattr(validator, "EXECUTION_TIMEOUT_SECONDS", 0.1)

    run = validate_candidate("narrow", FIXTURE_ROOT)

    assert run.verdict == "error"
    assert run.characterization_passed is False
    assert run.acceptance_passed is False
    assert run.failed_checks == ("candidate execution timed out",)
    assert json.loads(run.output) == {
        "error": {
            "code": "timeout",
            "message": "candidate execution timed out",
            "timeout_seconds": 0.1,
        }
    }
    assert str(FIXTURE_ROOT) not in run.output


def test_unexpected_subprocess_exception_is_normalized(monkeypatch):
    def raise_unexpected(*args, **kwargs):
        raise RuntimeError("private source path /host/candidate.py")

    monkeypatch.setattr(subprocess, "Popen", raise_unexpected)

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


def test_nonzero_execution_errors_do_not_expose_raw_stderr_or_source(monkeypatch):
    source_marker = "SECRET_SOURCE_SHOULD_NOT_REACH_UI"
    path_marker = "/host/private/candidate.py"

    monkeypatch.setattr(
        validator,
        "_execute_runner",
        lambda *args, **kwargs: validator._CompletedExecution(
            returncode=1,
            result=f"{path_marker} {source_marker}".encode(),
        ),
    )

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


def test_candidate_stdout_cannot_forge_runner_control_result(tmp_path):
    forged_payload = json.dumps(EXPECTED_CHECKS, sort_keys=True).encode("utf-8")
    completed = _execute_script(
        tmp_path,
        "import os\n"
        "import sys\n"
        f"os.write(1, {forged_payload!r})\n"
        "os.close(int(sys.argv[1]))\n",
    )

    assert completed.returncode == 0
    assert completed.result == b""

    with pytest.raises(ValueError, match="invalid check results"):
        validator._parse_check_results(completed.result)


@pytest.mark.parametrize(
    "mutate",
    [
        pytest.param(lambda checks: checks[:-1], id="missing-check"),
        pytest.param(
            lambda checks: [checks[0], checks[0], *checks[2:]],
            id="duplicate-name",
        ),
        pytest.param(
            lambda checks: [{**checks[0], "name": "invented check"}, *checks[1:]],
            id="unexpected-name",
        ),
        pytest.param(
            lambda checks: [{**checks[0], "extra": "field"}, *checks[1:]],
            id="extra-field",
        ),
        pytest.param(
            lambda checks: [{**checks[0], "passed": 1}, *checks[1:]],
            id="non-boolean-result",
        ),
        pytest.param(
            lambda checks: [{**checks[0], "kind": "acceptance"}, *checks[1:]],
            id="wrong-kind",
        ),
    ],
)
def test_result_parser_requires_exact_check_schema_names_and_count(mutate):
    parse_results = getattr(validator, "_parse_check_results", None)
    assert callable(parse_results), "validator needs a strict check-result parser"
    payload = json.dumps(mutate(EXPECTED_CHECKS), sort_keys=True).encode("utf-8")

    with pytest.raises(ValueError, match="invalid check results"):
        parse_results(payload)


@pytest.mark.parametrize("descriptor, stream", [(1, "stdout"), (2, "stderr")])
def test_descriptor_output_over_limit_is_stopped_by_runner(tmp_path, descriptor, stream):
    with pytest.raises(validator._OutputLimitExceeded) as caught:
        _execute_script(
            tmp_path,
            "import os\n"
            f"os.write({descriptor}, b'\\xff' * 2_000_000)",
        )

    assert caught.value.stream == stream


def test_output_limit_is_returned_as_bounded_structured_evidence(monkeypatch):
    def exceed_output(*args, **kwargs):
        raise validator._OutputLimitExceeded("stdout")

    monkeypatch.setattr(validator, "_execute_runner", exceed_output)

    run = validate_candidate("narrow", FIXTURE_ROOT)

    assert run.verdict == "error"
    assert run.failed_checks == ("candidate execution exceeded output limit",)
    assert json.loads(run.output) == {
        "error": {
            "code": "output_limit",
            "message": "candidate execution exceeded output limit",
            "output_limit_bytes": 4000,
            "stream": "stdout",
        }
    }


@pytest.mark.skipif(sys.platform != "linux", reason="Linux process-group regression")
def test_timeout_kills_and_reaps_candidate_descendants(tmp_path, monkeypatch):
    pid_file = tmp_path / "descendant.pid"
    script = (
        "import subprocess\n"
        "import sys\n"
        "import time\n"
        "from pathlib import Path\n"
        f"_child = subprocess.Popen([sys.executable, '-I', '-c', "
        f"'import time; time.sleep(5)'], env={{}})\n"
        "_start_time = Path(f'/proc/{_child.pid}/stat').read_text().split()[21]\n"
        f"Path({str(pid_file)!r}).write_text(f'{{_child.pid}}:{{_start_time}}')\n"
        "while True:\n"
        "    time.sleep(0.1)"
    )
    monkeypatch.setattr(validator, "EXECUTION_TIMEOUT_SECONDS", 0.2)

    started = time.monotonic()
    with pytest.raises(validator._ExecutionTimedOut):
        _execute_script(tmp_path, script)
    elapsed = time.monotonic() - started

    descendant_pid, start_time = pid_file.read_text(encoding="utf-8").split(":")
    assert elapsed < 2
    descendant_stat = Path(f"/proc/{descendant_pid}/stat")
    if descendant_stat.exists():
        assert descendant_stat.read_text().split()[21] != start_time


def test_modified_candidate_output_is_rejected_by_integrity_check(tmp_path):
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

    run = validate_candidate("narrow", fixture_root)

    assert run.verdict == "error"
    assert run.failed_checks == ("audited fixture integrity check failed",)
    assert json.loads(run.output)["error"] == {
        "code": "integrity_error",
        "files": ["narrow.py"],
        "message": "audited fixture integrity check failed",
    }
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
