"""Behavior-gate negative and positive control tests.

These tests demonstrate the gate FAILING on the known-bad patch
(strip().upper()) and PASSING on the narrow one.  They run against the
live validator — no mocking — so they prove the full engine chain.

Run them directly:

    pytest tests/test_behavior_gate.py -v

Expected output
---------------
PASSED  test_bad_patch_fails_gate_characterization_check
PASSED  test_bad_patch_passes_acceptance_check
PASSED  test_bad_patch_verdict_is_rejected
PASSED  test_narrow_patch_passes_gate_characterization_checks
PASSED  test_narrow_patch_passes_acceptance_check
PASSED  test_narrow_patch_verdict_is_accepted
PASSED  test_gate_logic_raises_for_bad_characterization
PASSED  test_gate_logic_passes_for_narrow

The first four tests confirm that "the gate bites" on the bad patch:
  - characterization_passed is False
  - the 'lowercase code remains invalid' check is in failed_checks
  - acceptance_passed is still True (the new feature works)
  - verdict is 'rejected'

The remaining tests confirm the narrow patch clears the gate cleanly.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

from shadowspec.validator import validate_candidate

FIXTURE_ROOT = Path(__file__).parents[1] / "fixtures" / "legacy_orders"

# The preserved-behavior check that strip().upper() breaks:
_LOWERCASE_CHECK = (
    "lowercase code remains invalid with complete pricing result and audit row"
)


# ---------------------------------------------------------------------------
# Negative control — bad patch (strip().upper())
# ---------------------------------------------------------------------------

class TestBadPatchFailsGate:
    """The gate MUST reject the bad patch.

    strip().upper() normalises case, so 'save10' now gives a discount.
    That silently changes a preserved characterization observation.
    The gate must surface this and block the merge.
    """

    @pytest.fixture(scope="class")
    def bad_run(self):
        return validate_candidate("bad", FIXTURE_ROOT)

    def test_characterization_failed(self, bad_run):
        """Gate condition: characterization_passed is False for bad patch."""
        assert bad_run.characterization_passed is False, (
            "Expected characterization_passed=False for the bad patch "
            "(strip().upper() changes lowercase behavior)"
        )

    def test_lowercase_check_is_the_failing_one(self, bad_run):
        """The specific check that strip().upper() breaks is named in failed_checks."""
        assert _LOWERCASE_CHECK in bad_run.failed_checks, (
            f"Expected '{_LOWERCASE_CHECK}' in failed_checks; "
            f"got: {bad_run.failed_checks}"
        )

    def test_acceptance_still_passes(self, bad_run):
        """The bad patch satisfies the new whitespace request — only characterization fails."""
        assert bad_run.acceptance_passed is True, (
            "Expected acceptance_passed=True: bad patch does trim whitespace, "
            "but it goes too far"
        )

    def test_verdict_is_rejected(self, bad_run):
        """Final verdict must be 'rejected' — gate blocks the merge."""
        assert bad_run.verdict == "rejected", (
            f"Expected verdict='rejected', got {bad_run.verdict!r}"
        )

    def test_gate_logic_raises(self, bad_run):
        """Simulate the gate step: raise SystemExit when characterization fails."""
        with pytest.raises(SystemExit) as exc_info:
            _run_gate_logic(bad_run)
        assert exc_info.value.code == 1, (
            "Gate must exit with code 1 when characterization_passed=False"
        )


# ---------------------------------------------------------------------------
# Positive control — narrow patch (strip() only)
# ---------------------------------------------------------------------------

class TestNarrowPatchPassesGate:
    """The gate MUST accept the narrow patch.

    strip() only trims surrounding whitespace without changing case.
    All four preserved characterization checks still pass, and the new
    acceptance check passes too.
    """

    @pytest.fixture(scope="class")
    def narrow_run(self):
        return validate_candidate("narrow", FIXTURE_ROOT)

    def test_characterization_passed(self, narrow_run):
        """Gate condition: characterization_passed is True for narrow patch."""
        assert narrow_run.characterization_passed is True, (
            "Expected characterization_passed=True for the narrow patch "
            "(strip() only does not change existing behavior)"
        )

    def test_no_failed_checks(self, narrow_run):
        """All named checks pass — nothing in failed_checks."""
        assert narrow_run.failed_checks == (), (
            f"Expected no failed checks; got: {narrow_run.failed_checks}"
        )

    def test_acceptance_passed(self, narrow_run):
        """The narrow patch satisfies the whitespace acceptance check."""
        assert narrow_run.acceptance_passed is True

    def test_verdict_is_accepted(self, narrow_run):
        """Final verdict must be 'accepted' — gate lets the merge through."""
        assert narrow_run.verdict == "accepted", (
            f"Expected verdict='accepted', got {narrow_run.verdict!r}"
        )

    def test_gate_logic_does_not_raise(self, narrow_run):
        """Simulate the gate step: must not raise SystemExit for a clean patch."""
        _run_gate_logic(narrow_run)  # must not raise


# ---------------------------------------------------------------------------
# Side-by-side comparison
# ---------------------------------------------------------------------------

def test_separation_rule_bad_vs_narrow():
    """One call confirms the full separation rule in one assertion block.

    strip().upper() → characterization fails, verdict=rejected
    strip() only    → all checks pass, verdict=accepted
    """
    bad    = validate_candidate("bad",    FIXTURE_ROOT)
    narrow = validate_candidate("narrow", FIXTURE_ROOT)

    # bad: acceptance works, characterization does not
    assert bad.acceptance_passed      is True
    assert bad.characterization_passed is False
    assert bad.verdict                == "rejected"

    # narrow: both work
    assert narrow.acceptance_passed      is True
    assert narrow.characterization_passed is True
    assert narrow.verdict                == "accepted"

    # The specific check that distinguishes them
    assert _LOWERCASE_CHECK in bad.failed_checks
    assert _LOWERCASE_CHECK not in narrow.failed_checks


# ---------------------------------------------------------------------------
# Gate logic helper (mirrors the workflow step)
# ---------------------------------------------------------------------------

def _run_gate_logic(run) -> None:
    """Replicate the 'Characterization gate' workflow step in Python.

    Raises SystemExit(1) when the gate would fail, matching the workflow's
    ``sys.exit(1)`` call so tests can assert on it with pytest.raises.
    """
    if not run.characterization_passed:
        failed = run.failed_checks
        lines = ["GATE FAILED: preserved characterization behavior was changed."]
        lines.append("Failed checks:")
        for check in failed:
            lines.append(f"  - {check}")
        print("\n".join(lines), file=sys.stderr)
        sys.exit(1)

    if not run.acceptance_passed:
        print(
            "GATE FAILED: acceptance check did not pass.",
            file=sys.stderr,
        )
        sys.exit(1)
