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
    ("accounts", "SELECT count(*) FROM account", 9),
    ("opportunities", "SELECT count(*) FROM opportunity", 24),
    ("line items", "SELECT count(*) FROM opportunity_line_item", 17),
    (
        "closed-won rows",
        "SELECT count(*) FROM opportunity WHERE stage_name = 'Closed Won'",
        21,
    ),
    (
        "orphaned line items",
        """SELECT count(*) FROM opportunity_line_item li
           LEFT JOIN opportunity o ON o.id = li.opportunity_id
           WHERE o.id IS NULL""",
        2,
    ),
    (
        "closed-won rows with no close date",
        "SELECT count(*) FROM opportunity WHERE stage_name = 'Closed Won' AND close_date IS NULL",
        2,
    ),
    (
        "foreign-currency rows with no conversion rate",
        """SELECT count(*) FROM opportunity
           WHERE currency_iso_code <> 'USD' AND conversion_rate IS NULL""",
        1,
    ),
    (
        "amended-after-close rows",
        """SELECT count(*) FROM opportunity
           WHERE stage_name = 'Closed Won'
             AND close_date IS NOT NULL
             AND date_trunc('month', last_modified_date) > date_trunc('month', close_date)""",
        1,
    ),
    (
        # 21 closed-won, minus 2 with no month, 1 unconvertible, 1 internal.
        "closed-won rows that are actually reportable",
        """SELECT count(*) FROM opportunity o
           JOIN account a ON a.id = o.account_id
           WHERE o.stage_name = 'Closed Won'
             AND o.close_date IS NOT NULL
             AND NOT (o.currency_iso_code <> 'USD' AND o.conversion_rate IS NULL)
             AND a.industry <> 'Internal'""",
        17,
    ),
    (
        "subsidiary accounts",
        "SELECT count(*) FROM account WHERE parent_id IS NOT NULL",
        1,
    ),
    (
        "internal test accounts",
        "SELECT count(*) FROM account WHERE industry = 'Internal'",
        1,
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
