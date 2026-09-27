"""The optional Bob MCP adapter returns the real fixture verdicts."""
from __future__ import annotations

import pytest

pytest.importorskip("mcp")
from shadowspec.bob_mcp import validate_fixture


def test_bob_mcp_rejects_broad_patch_and_accepts_narrow_patch():
    bad = validate_fixture("bad")
    narrow = validate_fixture("narrow")
    assert bad["verdict"] == "rejected"
    assert bad["characterization_passed"] is False
    assert bad["acceptance_passed"] is True
    assert any("lowercase" in check for check in bad["failed_checks"])
    assert narrow["verdict"] == "accepted"
    assert narrow["characterization_passed"] is True
    assert narrow["acceptance_passed"] is True
    assert bad["provenance"]["source_sha256"] != narrow["provenance"]["source_sha256"]
    assert len(bad["provenance"]["validator_sha256"]) == 64


def test_bob_mcp_rejects_unapproved_candidate():
    assert "error" in validate_fixture("../secrets")
