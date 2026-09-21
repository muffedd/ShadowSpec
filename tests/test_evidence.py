from __future__ import annotations

import json
from dataclasses import replace

from shadowspec.evidence import EvidenceInput, render_json, render_markdown
from shadowspec.validator import ValidationRun


def sample_input() -> EvidenceInput:
    return EvidenceInput(
        request="Accept surrounding whitespace in discount codes.",
        changed_files=("legacy_orders.py",),
        intended_delta="Trim surrounding whitespace only.",
        preserved_behavior=("Case sensitivity", "Pricing", "SQLite audit write"),
        risks=("Named fixtures do not prove semantic equivalence.",),
        reviewer_checklist=("Confirm lowercase codes remain invalid.",),
        rollback_notes="Restore the baseline variant and rerun validation.",
        analysis={"functions": ["process_order"], "limitations": ["dynamic dispatch is not resolved"]},
        validation=ValidationRun(
            run_id="run123", candidate="narrow", verdict="accepted",
            characterization_passed=True, acceptance_passed=True, failed_checks=(),
            source_sha256="a" * 64, output='{"exit_code": 0}',
        ),
    )


def test_markdown_contains_reviewer_ready_sections():
    text = render_markdown(sample_input())
    for heading in (
        "# ShadowSpec evidence pack", "## Intended behavior delta",
        "## Preserved behavior", "## Changed files", "## Risks",
        "## Reviewer checklist", "## Rollback notes", "## Raw validation summary",
    ):
        assert heading in text
    assert "run123" in text
    assert "a" * 64 in text


def test_baseline_markdown_explains_empty_changed_files():
    payload = sample_input()
    baseline = replace(
        payload,
        changed_files=(),
        validation=replace(payload.validation, candidate="baseline", verdict="rejected"),
    )

    text = render_markdown(baseline)

    changed_files_section = text.split("## Changed files", 1)[1].split("## Static analysis", 1)[0]
    assert "_None — this is the unchanged baseline._" in changed_files_section


def test_json_is_stable_and_machine_readable():
    first = render_json(sample_input())
    second = render_json(sample_input())
    assert first == second
    parsed = json.loads(first)
    assert parsed["schema_version"] == "1.0"
    assert parsed["validation"]["verdict"] == "accepted"
    assert parsed["changed_files"] == ["legacy_orders.py"]


def test_exports_do_not_include_absolute_paths_or_environment(monkeypatch):
    monkeypatch.setenv("SHADOWSPEC_SECRET", "do-not-leak")
    payload = sample_input()
    combined = render_markdown(payload) + render_json(payload)
    assert "do-not-leak" not in combined
    assert "/workspace/" not in combined
    assert "SHADOWSPEC_SECRET" not in combined
