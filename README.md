# scratch-vd-4319-approval-record

Fixture repo for the VD-4319 manual runbook
(`tests/evals/VD-4319-APPROVAL-RECORD-MANUAL-RUNBOOK.md` in
`vibedata-data-engineering`).

VD-4319 is the defect where an Intent's `## Approvals` box recorded an approval
the user never gave. The fix is prose in the intent template — nothing refuses a
bad write — so a manual run is the only detector, and a run is only as good as
what it runs against. Earlier attempts used an unrelated repo with no Salesforce
data and no source document, which made the interview ungrounded and the
sign-off check vacuous. This repo removes both excuses.

## What it provides

| Path | Why the runbook needs it |
| --- | --- |
| `docs/REV-2026-014-…​.docx` | The uploaded requirements document. Its header says `Status: Approved for build` and its final page is a Sign-off table naming a VP, Revenue Operations and a CFO — the exact text that leaked into the Intent's own Approvals section in the original defect. Attach this to test AC4. |
| `docs/REV-2026-014-…​.md` | The readable source for that document. Edit this, then regenerate the `.docx`. |
| `seed/salesforce.sql` | `account`, `opportunity`, `opportunity_line_item` carrying every awkward condition the document promises, so the interview's decision branches have data behind them. |
| `CONTEXT.md` | What `capturing-intent` reads first. Describes the domain and says nothing about approvals — the agent must get the approval behaviour right on its own, not because the fixture hinted at it. |
| `scripts/reset.sh` | Returns the repo to this baseline between runs. |

## Deliberately absent

No secrets. The document this replaces could not be committed — an appendix held
a live session token, which a blocking secret scan would reject, and a fixture
that trips the secret gate is not a fixture. Nothing here is a real credential,
a real customer, or a real figure.

No hint about the defect. No file mentions approvals, the Approvals box, or what
the agent is supposed to do about them. A fixture that primes the behaviour it is
testing produces a pass that means nothing.

## Setup

```bash
git clone git@github.com:trang-acceleratedata/scratch-vd-4319-approval-record.git
cd scratch-vd-4319-approval-record

# Seed the Studio Domain's DuckDB file. Stop the dev server first — DuckDB takes
# a write lock and a running backend holds it.
python3 scripts/seed-duckdb.py --db ~/vd-studio/data/duckdb/<domain-slug>.duckdb
```

Then bind a **DuckDB-backed** Domain to this repo and create a **Build** Intent.
`vibedata-data-engineering` needs no marketplace install: the `build` persona
declares it in `defaultPlugins`, so it loads automatically. Confirm the run is
real by checking that **SKILLS USED** lists `capturing-intent` — an Intent whose
agent never enters that skill produces a meaningless pass.

## The data conditions

`scripts/seed-duckdb.py` verifies all of these after loading and fails loudly if
one is missing, because a silently-absent condition turns its interview branch
into a question with nothing behind it.

| Condition | Rows | Interview branch it feeds |
| --- | --- | --- |
| Closed-won opportunities | 21 | what counts as revenue |
| …of which actually reportable | 17 | the figure after every exclusion |
| Orphaned line items | 2 | line items whose parent is missing |
| Closed-won with no close date | 2 | attribution when the month is unknown |
| Foreign currency, no conversion rate | 1 | unconvertible amounts |
| Amended after its month closed | 1 | restatement of a reported month |
| Subsidiary accounts (`parent_id`) | 1 | hierarchy roll-up |
| Internal test accounts | 1 | exclusions |

## Between runs

```bash
./scripts/reset.sh --push --db ~/vd-studio/data/duckdb/<domain-slug>.duckdb
```

This deletes agent output, prunes `intent/*` branches locally and remotely, and
re-seeds the database. Then delete the Studio Intent and create a new one — an
Intent picks up its plugin set and its workspace at spawn, so it has to be
created after the reset, not before.

## Regenerating the document

```bash
python3 scripts/make-requirements-docx.py          # rewrite the .docx from the .md
python3 scripts/make-requirements-docx.py --check  # validate without writing
```

The generator refuses to write if the render lost `Status: Approved for build`,
the VP line, or the CFO line — those three strings are the whole point of the
document, and losing one would make AC4 pass for the wrong reason.
