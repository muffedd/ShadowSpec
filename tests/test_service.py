from __future__ import annotations

import json

from shadowspec.service import FIXTURE_ROOT, run_demo


def test_bad_demo_explains_rejection_and_exports_evidence():
    result = run_demo("bad")
    assert result.validation.verdict == "rejected"
    assert result.validation.acceptance_passed is True
    assert "lowercase code remains invalid with complete pricing result and audit row" in result.validation.failed_checks
    assert result.analysis["file_count"] == 1
    assert "process_order" in result.analysis["functions"]
    assert "## Risks" in result.evidence_markdown
    assert json.loads(result.evidence_json)["validation"]["verdict"] == "rejected"


def test_narrow_demo_is_accepted_with_review_boundary():
    result = run_demo("narrow")
    assert result.validation.verdict == "accepted"
    assert result.changed_files == ("fixtures/legacy_orders/variants/narrow.py",)
    assert "named fixtures" in result.evidence_markdown.lower()
    assert FIXTURE_ROOT.name == "legacy_orders"


def test_selected_candidate_analysis_excludes_other_variants_and_has_diff():
    result = run_demo("narrow")

    assert result.analysis["files"] == ["variants/narrow.py"]
    assert all("baseline" not in edge and "bad" not in edge for edge in result.analysis["call_edges"])
    assert "--- baseline.py" in result.analysis["diff"]
    assert "+++ narrow.py" in result.analysis["diff"]
    assert result.analysis["blast_radius"] == []


def test_evidence_binds_selected_candidate_to_baseline_and_runner():
    result = run_demo("narrow")

    validation = result.validation
    assert validation.source_sha256 == validation.candidate_sha256
    assert len(validation.baseline_sha256) == 64
    assert len(validation.validator_sha256) == 64
    assert len(validation.runner_sha256) == 64
    payload = json.loads(result.evidence_json)
    assert payload["provenance"]["candidate_sha256"] == validation.source_sha256
    assert payload["provenance"]["baseline_sha256"] == validation.baseline_sha256
    assert payload["provenance"]["runner_sha256"] == validation.runner_sha256
