#!/usr/bin/env bash
# Return this repo to the state a VD-4319 runbook run expects.
#
# A run leaves behind whatever the agent produced — `intent/`, `design.md`,
# scaffolding, an intent branch. A second run starting from that state cannot
# test what the first one did: an unticked Approvals box is much harder to read
# when a previous run's box is sitting next to it, and the agent may resume the
# old intent instead of capturing a new one.
#
# Destructive on purpose: it deletes agent output and force-pushes the default
# branch back to the fixture baseline. Only ever point it at the scratch repo.
#
#   ./scripts/reset.sh              # clean the working tree, keep history
#   ./scripts/reset.sh --push       # also force the remote default branch back
#   ./scripts/reset.sh --db <path>  # re-seed the Domain database too

set -euo pipefail

BASELINE_PATHS=(README.md CONTEXT.md docs seed scripts .gitignore)
DEFAULT_BRANCH="${DEFAULT_BRANCH:-main}"
PUSH=0
DB=""

while [ $# -gt 0 ]; do
  case "$1" in
    --push) PUSH=1; shift ;;
    --db) DB="${2:?--db needs a path}"; shift 2 ;;
    -h|--help) sed -n '2,18p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) echo "unknown argument: $1" >&2; exit 2 ;;
  esac
done

cd "$(dirname "$0")/.."

# Identify the repo by its remote, not by its directory name: a clone can live in
# any directory, and a directory name is trivially wrong in both directions — it
# would refuse a legitimate clone and accept a renamed one. This script deletes
# files and force-pushes, so the check has to mean something.
FIXTURE_REPO="scratch-vd-4319-approval-record"
origin="$(git remote get-url origin 2>/dev/null || true)"
if [ -z "$origin" ]; then
  echo "refusing to run: no 'origin' remote, so this cannot be confirmed as $FIXTURE_REPO" >&2
  exit 1
fi
case "$origin" in
  *"$FIXTURE_REPO"*) ;;
  *)
    echo "refusing to run: origin is $origin, not $FIXTURE_REPO" >&2
    exit 1
    ;;
esac

echo "==> removing agent output"
# Everything that is not a baseline path, tracked or not.
git ls-files -z --others --cached --exclude-standard \
  | tr '\0' '\n' \
  | awk -F/ '{print $1}' \
  | sort -u \
  | while read -r top; do
      [ -n "$top" ] || continue
      keep=0
      for b in "${BASELINE_PATHS[@]}"; do [ "$top" = "$b" ] && keep=1; done
      [ "$keep" = 1 ] && continue
      echo "    rm -rf $top"
      rm -rf -- "$top"
    done

echo "==> restoring baseline files"
git checkout -- "${BASELINE_PATHS[@]}" 2>/dev/null || true

echo "==> pruning intent branches"
git checkout -q "$DEFAULT_BRANCH" 2>/dev/null || git checkout -q -B "$DEFAULT_BRANCH"
git branch --list 'intent/*' --format='%(refname:short)' | while read -r b; do
  [ -n "$b" ] && git branch -D "$b" >/dev/null && echo "    deleted local $b"
done

if [ "$PUSH" = 1 ]; then
  echo "==> forcing remote $DEFAULT_BRANCH back to the baseline"
  git push --force origin "$DEFAULT_BRANCH"
  git ls-remote --heads origin 'intent/*' | awk '{print $2}' | sed 's|refs/heads/||' | while read -r b; do
    [ -n "$b" ] && git push origin --delete "$b" && echo "    deleted remote $b"
  done
fi

if [ -n "$DB" ]; then
  echo "==> re-seeding $DB"
  python3 scripts/seed-duckdb.py --db "$DB"
fi

echo
echo "Reset complete. Next:"
echo "  1. Delete the Studio Intent and create a new one (it must spawn against this state)."
echo "  2. Attach docs/REV-2026-014-Revenue-Reporting-Requirement.docx for the sign-off checks."
git status --short || true
