from __future__ import annotations

import importlib.util
import sqlite3
from pathlib import Path

import pytest


FIXTURE_ROOT = Path(__file__).parents[1] / "fixtures" / "legacy_orders"


def load_variant(name: str):
    module_path = FIXTURE_ROOT / "variants" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(f"legacy_orders_{name}", module_path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def audit_rows(db_path: Path) -> list[tuple[str, int]]:
    with sqlite3.connect(db_path) as connection:
        return connection.execute(
            "select code, total_cents from discount_audit order by rowid"
        ).fetchall()


@pytest.mark.parametrize(
    ("variant", "code", "expected_total"),
    [
        ("baseline", "SAVE10", 9000),
        ("baseline", "save10", 10000),
        ("bad", "save10", 9000),
        ("narrow", "save10", 10000),
    ],
)
def test_existing_case_sensitive_behavior(variant, code, expected_total, tmp_path):
    result = load_variant(variant).process_order(
        {"subtotal_cents": 10000, "discount_code": code}, tmp_path / "audit.db"
    )
    assert result["total_cents"] == expected_total


@pytest.mark.parametrize(
    ("variant", "expected_total"),
    [("baseline", 10000), ("bad", 9000), ("narrow", 9000)],
)
def test_requested_whitespace_behavior(variant, expected_total, tmp_path):
    result = load_variant(variant).process_order(
        {"subtotal_cents": 10000, "discount_code": " SAVE10 "},
        tmp_path / "audit.db",
    )
    assert result["total_cents"] == expected_total


@pytest.mark.parametrize("variant", ["baseline", "bad", "narrow"])
def test_audit_side_effect_matches_observed_code_and_total(variant, tmp_path):
    db_path = tmp_path / "audit.db"
    result = load_variant(variant).process_order(
        {"subtotal_cents": 5000, "discount_code": "NONE"}, db_path
    )
    assert result == {"subtotal_cents": 5000, "discount_cents": 0, "total_cents": 5000}
    assert audit_rows(db_path) == [("NONE", 5000)]


@pytest.mark.parametrize("variant", ["baseline", "bad", "narrow"])
def test_negative_subtotal_is_rejected_without_audit_write(variant, tmp_path):
    db_path = tmp_path / "audit.db"
    with pytest.raises(ValueError, match="subtotal_cents must be non-negative"):
        load_variant(variant).process_order(
            {"subtotal_cents": -1, "discount_code": "SAVE10"}, db_path
        )
    assert not db_path.exists()

