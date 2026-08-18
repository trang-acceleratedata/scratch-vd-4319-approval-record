#!/usr/bin/env python3
"""Load the Salesforce-shaped fixture into a Studio Domain's DuckDB file.

The tables have to live in the Domain's own database, not in this repo — Studio
owns that path (`data/duckdb/<domain-slug>.duckdb` in host-dev) and the agent
reaches it through the Domain binding. So this takes the target as an argument
rather than writing a database into the working tree.

Usage:
    python3 scripts/seed-duckdb.py --db ~/vd-studio/data/duckdb/<slug>.duckdb
    python3 scripts/seed-duckdb.py --db <path> --verify-only

Stop the Studio dev server first if the file is already open: DuckDB takes a
write lock, and a running backend holds it.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

SEED = Path(__file__).resolve().parent.parent / "seed" / "salesforce.sql"

# The conditions REV-2026-014 section 4 promises. Verified after load, because a
# fixture that silently lost one of them turns the matching interview branch into
# a question with nothing behind it.
EXPECTATIONS: list[tuple[str, str, int]] = [
    # Every figure traces to REV-2026-014, so a drifting fixture fails loudly rather
    # than quietly producing an interview about a world the document does not describe.
    ("products", "SELECT count(*) FROM product", 18),
    ("product families (doc Appendix C: 9)", "SELECT count(DISTINCT product_family) FROM product", 9),
    ("opportunities", "SELECT count(*) FROM opportunity", 50),
    ("line items", "SELECT count(*) FROM opportunity_line_item", 100),
    (
        "Sales Ops closed-won deals (stage_name)",
        "SELECT count(*) FROM opportunity WHERE stage_name = 'Closed Won'",
        50,
    ),
    (
        "Finance won deals (is_won) — doc Appendix A gap",
        "SELECT count(*) FROM opportunity WHERE is_won",
        39,
    ),
    (
        "stage/flag disagreements = 22% of 50 (Appendix A)",
        "SELECT count(*) FROM opportunity WHERE stage_name = 'Closed Won' AND NOT is_won",
        11,
    ),
    (
        "closed-won opportunities with no line items = 8% (Appendix C)",
        """SELECT count(*) FROM opportunity o
           WHERE o.stage_name = 'Closed Won'
             AND NOT EXISTS (SELECT 1 FROM opportunity_line_item li WHERE li.opportunity_id = o.id)""",
        4,
    ),
    (
        "line items that cannot resolve to a family = 22% (Appendix C)",
        """SELECT count(*) FROM opportunity_line_item li
           LEFT JOIN product p ON p.id = li.product_id
           WHERE p.id IS NULL""",
        22,
    ),
    (
        "line items where quantity * unit_price <> total_price (Appendix C)",
        "SELECT count(*) FROM opportunity_line_item WHERE quantity * unit_price <> total_price",
        6,
    ),
    (
        "single-currency: no currency column exists (doc s8)",
        """SELECT count(*) FROM information_schema.columns
           WHERE table_name IN ('opportunity','opportunity_line_item')
             AND lower(column_name) LIKE '%currenc%'""",
        0,
    ),
    (
        "load lineage present on both loaded tables (R1.5)",
        """SELECT count(DISTINCT table_name) FROM information_schema.columns
           WHERE table_name IN ('opportunity','opportunity_line_item')
             AND column_name = 'load_batch_id'""",
        2,
    ),
]


def verify(con) -> list[str]:
    failures = []
    for label, sql, expected in EXPECTATIONS:
        actual = con.execute(sql).fetchone()[0]
        mark = "ok " if actual == expected else "BAD"
        print(f"  [{mark}] {label}: {actual} (expected {expected})")
        if actual != expected:
            failures.append(f"{label}: got {actual}, expected {expected}")
    return failures


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", required=True, help="path to the Domain's .duckdb file")
    ap.add_argument("--schema", default="main", help="target schema (default: main)")
    ap.add_argument(
        "--verify-only",
        action="store_true",
        help="check an already-seeded database without rewriting it",
    )
    args = ap.parse_args()

    try:
        import duckdb
    except ImportError:
        print("duckdb is required: pip install duckdb", file=sys.stderr)
        return 1

    db = Path(args.db).expanduser()
    if args.verify_only and not db.exists():
        print(f"no database at {db}", file=sys.stderr)
        return 1
    db.parent.mkdir(parents=True, exist_ok=True)

    try:
        con = duckdb.connect(str(db))
    except duckdb.IOException as exc:
        print(f"cannot open {db}: {exc}", file=sys.stderr)
        print("Is the Studio dev server running? It holds a write lock.", file=sys.stderr)
        return 1

    with con:
        con.execute(f'CREATE SCHEMA IF NOT EXISTS "{args.schema}"')
        # SET schema takes a string literal, not a quoted identifier.
        con.execute("SET schema = ?", [args.schema])

        if not args.verify_only:
            con.execute(SEED.read_text(encoding="utf-8"))
            print(f"seeded {db} (schema {args.schema}) from {SEED.name}")

        print("fixture conditions:")
        failures = verify(con)

    if failures:
        print("\nfixture is not in the expected state:", file=sys.stderr)
        for f in failures:
            print(f"  - {f}", file=sys.stderr)
        return 1

    print("\nall fixture conditions present")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
