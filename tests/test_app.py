from __future__ import annotations

import re

import pytest
from streamlit.testing.v1 import AppTest

from shadowspec.service import DemoResult
from shadowspec.validator import ValidationRun


@pytest.fixture(scope="module")
def loaded_app():
    return AppTest.from_file("app.py").run(timeout=10)


def _rendered_html(app, marker: str) -> str:
    return next(item.value for item in app.markdown if marker in item.value)


def _relative_luminance(color: str) -> float:
    channels = [int(color[index:index + 2], 16) / 255 for index in (1, 3, 5)]
    linear = [
        channel / 12.92
        if channel <= 0.04045
        else ((channel + 0.055) / 1.055) ** 2.4
        for channel in channels
    ]
    return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]


def test_judge_ui_loads_and_runs_narrow_candidate():
    app = AppTest.from_file("app.py").run(timeout=10)
    assert not app.exception
    assert "ShadowSpec" in app.title[0].value
    assert app.radio[0].value == "Narrow candidate"
    app.button[0].click().run(timeout=10)
    assert not app.exception
    assert any("ACCEPTED" in item.value for item in app.success)


def test_proof_sequence_uses_ordered_list_semantics(loaded_app):
    proof = _rendered_html(loaded_app, "Judge proof sequence")

    assert "<ol" in proof
    assert proof.count("<li") == 3


def test_contract_labels_are_headings_and_whitespace_is_visible(loaded_app):
    contract = _rendered_html(loaded_app, "Requested delta")

    assert '<h4 class="contract-heading">Requested delta</h4>' in contract
    assert '<h4 class="contract-heading">Frozen observations</h4>' in contract
    assert "␠SAVE10␠" in contract
    assert "␠ = space" in contract


def test_card_borders_have_three_to_one_non_text_contrast(loaded_app):
    styles = _rendered_html(loaded_app, "--surface:")
    surface = re.search(r"--surface:\s*(#[0-9a-fA-F]{6})", styles).group(1)
    border = re.search(r"--border:\s*(#[0-9a-fA-F]{6})", styles).group(1)
    lighter, darker = sorted(
        (_relative_luminance(surface), _relative_luminance(border)),
        reverse=True,
    )

    assert (lighter + 0.05) / (darker + 0.05) >= 3


def test_rejected_verdict_lists_every_check_with_text_status():
    app = AppTest.from_file("app.py").run(timeout=10)
    app.radio[0].set_value("Plausible bad candidate")
    app.button[0].click().run(timeout=10)

    assert any("REJECTED" in item.value for item in app.error)
    check_results = _rendered_html(app, "lowercase code remains invalid")
    assert check_results.count("**PASS**") == 4
    assert check_results.count("**FAIL**") == 1
    assert "surrounding whitespace is accepted" in check_results


def test_error_verdict_is_not_presented_as_rejected_or_as_failed_checks(monkeypatch):
    import shadowspec.service as service

    validation = ValidationRun(
        run_id="run-error",
        candidate="narrow",
        verdict="error",
        characterization_passed=False,
        acceptance_passed=False,
        failed_checks=("candidate execution timed out",),
        source_sha256="a" * 64,
        output='{"error": {"code": "timeout", "message": "candidate execution timed out"}}',
    )
    result = DemoResult(
        candidate="narrow",
        changed_files=("fixtures/legacy_orders/variants/narrow.py",),
        analysis={
            "file_count": 1,
            "functions": ["process_order"],
            "side_effects": ["sqlite"],
            "limitations": ["Dynamic dispatch is not resolved."],
        },
        validation=validation,
        evidence_markdown="# error evidence",
        evidence_json="{}",
    )
    monkeypatch.setattr(service, "run_demo", lambda candidate: result)

    app = AppTest.from_file("app.py").run(timeout=10)
    app.button[0].click().run(timeout=10)

    assert not app.exception
    assert any("ERROR" in item.value for item in app.error)
    assert not any("REJECTED" in item.value for item in app.error)
    assert [metric.value for metric in app.metric[:2]] == ["NOT RUN", "NOT RUN"]


def test_unexpected_exception_is_logged_but_public_copy_is_generic(monkeypatch):
    import shadowspec.service as service

    private_detail = "/workspace/private/customer.py"

    def fail_demo(candidate):
        raise RuntimeError(private_detail)

    monkeypatch.setattr(service, "run_demo", fail_demo)
    app = AppTest.from_file("app.py").run(timeout=10)
    app.button[0].click().run(timeout=10)

    assert not app.exception
    assert app.error[0].value == (
        "ERROR · Validation could not complete. Please retry or use the local CLI."
    )
    assert private_detail not in app.error[0].value
