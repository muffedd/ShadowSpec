"""Plausible but over-broad candidate: trims and normalizes case."""

from __future__ import annotations

import sqlite3
from pathlib import Path


def process_order(order: dict[str, object], db_path: Path) -> dict[str, int]:
    subtotal = int(order["subtotal_cents"])
    if subtotal < 0:
        raise ValueError("subtotal_cents must be non-negative")

    code = str(order.get("discount_code", ""))
    discount = subtotal // 10 if code.strip().upper() == "SAVE10" else 0
    total = subtotal - discount

    with sqlite3.connect(db_path) as connection:
        connection.execute(
            "create table if not exists discount_audit "
            "(code text not null, total_cents integer not null)"
        )
        connection.execute(
            "insert into discount_audit(code, total_cents) values (?, ?)",
            (code, total),
        )

    return {"subtotal_cents": subtotal, "discount_cents": discount, "total_cents": total}

