#!/usr/bin/env bash
# verify_cycle.sh — ad-hoc verification for ONE /process-notes cycle.
#
# Usage:
#   bash verify_cycle.sh                 # verify today's cycle
#   bash verify_cycle.sh 2026-08-05      # verify a specific cycle date
#   bash verify_cycle.sh --selftest      # negative control: prove the checks can FAIL
#
# This is a purpose-built cycle checker, NOT a project test suite. Personal_OS has
# no tests/ dir, no package.json and no pytest config — do not claim "suite green".
#
# WHY A --selftest FLAG EXISTS (2026-08-05 lesson):
#   A verification script that cannot fail proves nothing. Running --selftest re-runs
#   every check against a deliberately wrong date; if it does NOT produce failures,
#   the checks are vacuous and the green run is worthless. Always run it once per cycle.
set -u

V="/c/Users/khoans/Documents/Personal_OS/personal_vault"
LOG="30_KNOWLEDGE_BASE/wiki/log.md"
TS="_inbox/.last_process_notes"
SLEEP="10_PULSE/051_Sleep_Log.md"
CASE_CLOSED="_cases/closed/legal_divorce_court_GG_access.md"
CASE_ACTIVE="_cases/active/legal_quyen_tham_nom_GG.md"

SELFTEST=0
[ "${1:-}" = "--selftest" ] && SELFTEST=1 && shift
DATE="${1:-$(date +%Y-%m-%d)}"
[ "$SELFTEST" = "1" ] && DATE="1999-01-01"   # a date that cannot possibly match

P=0; F=0
cd "$V" || { echo "FATAL: vault not found at $V"; exit 2; }

chk() { # chk <label> <got> <want>
  if [ "$2" = "$3" ]; then
    printf 'PASS | %s\n' "$1"; P=$((P+1))
  else
    printf 'FAIL | %s\n       got  = [%s]\n       want = [%s]\n' "$1" "$2" "$3"; F=$((F+1))
  fi
}

echo "=== /process-notes cycle verification — date: $DATE ==="

echo "--- inbox drained ---"
chk "1. _inbox/01_unprocessed empty" \
    "$(ls -A _inbox/01_unprocessed/ 2>/dev/null | wc -l | tr -d ' ')" "0"
chk "2. stock_pending/ absent or empty" \
    "$(ls -A _inbox/01_unprocessed/stock_pending/ 2>/dev/null | wc -l | tr -d ' ')" "0"

echo "--- log.md (scoped to this cycle only) ---"
# Scope tightly: log.md has pre-existing ordering drift (2026-06-22 before 2026-06-23),
# so asserting whole-file newest-on-top fails on history you did not touch.
chk "3a. newest entry is this cycle's date" \
    "$(grep -m1 '^## ' "$LOG" | tr -d '\r')" "## $DATE"
chk "3b. frontmatter last_updated bumped" \
    "$(grep -m1 '^last_updated:' "$LOG" | tr -d '\r')" "last_updated: $DATE"

# Body of today's entry = lines after "## DATE" up to the next "## " header.
BLOCK=$(awk -v d="## $DATE" '$0==d{f=1;next} f&&/^## /{exit} f' "$LOG" | tr -d '\r')
chk "3c. entry has a non-empty body" \
    "$([ -n "$BLOCK" ] && echo yes || echo no)" "yes"
chk "3d. entry records the PROCESSED line" \
    "$(printf '%s\n' "$BLOCK" | grep -c 'PROCESSED' | tr -d ' ')" "1"
# A blank line directly BEFORE a bullet orphans the list. A trailing blank before the
# next "## " header is correct markdown separation and must NOT be flagged.
# NR>1 guard (added 2026-08-06): BLOCK is built with `next` on the header, so its first
# line is the first bullet. awk's uninitialized `p` is "" and matches the blank regex,
# so without NR>1 EVERY well-formed entry scored 1. Repro of the old bug:
#   printf -- '- one\n- two\n' | awk 'p ~ /^[[:space:]]*$/ && /^- /{c++} {p=$0} END{print c+0}'  -> 1
# `seen` guard (added 2026-08-10): a cycle section may legitimately open with a TABLE
# (e.g. /personal-weekly-connections writes `|| Time | Action |…` rows) and only THEN
# carry this cycle's bullets. Markdown REQUIRES a blank line between a table and a
# following list, so the first bullet is legally blank-preceded. Counting it flagged a
# correct file (2026-08-10 false positive). Only count blanks AFTER a bullet already
# opened the list — that still catches a genuinely orphaned blank between two bullets.
#   table,blank,'- one','- two'   -> 0  (legal separator)
#   '- one',blank,'- two'         -> 1  (real orphan, still caught)
chk "3e. no blank line orphaned inside the bullet list" \
    "$(printf '%s\n' "$BLOCK" | awk 'NR>1 && seen && p ~ /^[[:space:]]*$/ && /^- / {c++} /^- /{seen=1} {p=$0} END{print c+0}')" "0"

echo "--- timestamp + cases ---"
chk "4. .last_process_notes dated this cycle" \
    "$(cut -c1-10 "$TS" 2>/dev/null | tr -d '\r\n')" "$DATE"
chk "5a. divorce case filed under closed/" \
    "$([ -f "$CASE_CLOSED" ] && echo yes || echo no)" "yes"
# Closed case must have no follow_up to reset; active case currently has none either,
# so nothing auto-resets. If a follow_up ever appears, this flips and demands attention.
chk "5b. active case follow_up count (0 = nothing to auto-reset)" \
    "$(grep -c 'follow_up' "$CASE_ACTIVE" 2>/dev/null | tr -d ' ')" "0"

echo "--- git hygiene ---"
# MYCOMMITS resolved HERE (moved up 2026-08-10) so 6a can scope dirt to this cycle's files.
MYCOMMITS="$(git log --since="$DATE 00:00" --until="$DATE 23:59" --format='%h %s' 2>/dev/null \
             | grep -Ei 'process-notes|docs\(log\)' | awk '{print $1}' | tr '\n' ' ')"
# 6a REWRITTEN 2026-08-10. The old check demanded a GLOBALLY clean tree, which contradicts
# this skill's own "leave unrelated noise unstaged" rule: concurrent crons (capture-sleep,
# weekly-connections) routinely leave files modified mid-cycle, and /process-notes is
# REQUIRED not to stage them. A correct cycle therefore always failed. Scope the assertion
# to files THIS cycle committed; report foreign dirt as INFO, never FAIL.
# PATHSPEC TRAP (2026-08-08 lesson): `git show --name-only` prints REPO-ROOT-relative paths
# (personal_vault/…) while `git status --` pathspecs are CWD-relative (cwd IS personal_vault).
# Strip the prefix or the pathspec matches nothing and passes VACUOUSLY.
if [ -n "${MYCOMMITS// /}" ]; then
  MYFILES="$(git show --name-only --format='' $MYCOMMITS 2>/dev/null \
             | sed 's#^personal_vault/##' | grep -v '^$' | sort -u | tr '\n' ' ')"
  if [ -n "${MYFILES// /}" ]; then
    chk "6a. no uncommitted remainder in THIS cycle's own files" \
        "$(git status --porcelain -- $MYFILES 2>/dev/null | wc -l | tr -d ' ')" "0"
  else
    echo "SKIP | 6a. cycle commits touched no resolvable files"
  fi
else
  echo "SKIP | 6a. no cycle commits found for $DATE"
fi
FOREIGN="$(git status --porcelain | wc -l | tr -d ' ')"
if [ "$FOREIGN" != "0" ]; then
  echo "INFO | $FOREIGN file(s) dirty from OTHER processes — correctly left unstaged:"
  git status --porcelain | sed 's/^/       /'
fi
UNPUSHED="$(git rev-list --count @{u}..HEAD 2>/dev/null || echo NO_UPSTREAM)"
chk "6b. nothing left unpushed" "$UNPUSHED" "0"

echo "--- read-only-Sleep_Log invariant (2026-08-04 + 2026-08-05 lessons) ---"
# capture-sleep OWNS Sleep_Log and uses a revert-then-rewrite pattern. /process-notes
# must never write or `git add` it. It also commits CONCURRENTLY (afeee47 landed 4 min
# after a cycle commit on 2026-08-05), so never assert against HEAD — resolve the
# specific commits this cycle made and assert against those.
echo "     (this cycle's commits: ${MYCOMMITS:-none})"
if [ -n "${MYCOMMITS// /}" ]; then
  chk "7a. Sleep_Log absent from ALL of this cycle's commits" \
      "$(git show --name-only --format='' $MYCOMMITS 2>/dev/null | grep -c '051_Sleep_Log' | tr -d ' ')" "0"
else
  echo "SKIP | 7a. no cycle commits found for $DATE"
fi
chk "7b. Sleep_Log unmodified on disk vs HEAD" \
    "$(git diff --name-only HEAD -- "$SLEEP" | wc -l | tr -d ' ')" "0"

echo "--- duplicate scan on Sleep_Log (report only — never auto-fix) ---"
DUPS="$(grep '^### ' "$SLEEP" | sort | uniq -d | tr -d '\r' | tr '\n' ' ')"
if [ -n "${DUPS// /}" ]; then
  echo "WARN | duplicate Sleep_Log dates present: $DUPS"
  echo "       capture-sleep owns this file — FLAG for Warren, do NOT edit it here."
else
  echo "INFO | no duplicate Sleep_Log dates"
fi

printf -- '-----\nad-hoc verification: PASSED=%d FAILED=%d\n' "$P" "$F"
if [ "$SELFTEST" = "1" ]; then
  if [ "$F" -gt 0 ]; then
    echo "SELFTEST OK — checks are live (they failed against a bogus date, as intended)."
    exit 0
  fi
  echo "SELFTEST BROKEN — checks passed against a bogus date; they are vacuous. Fix them."
  exit 1
fi
[ "$F" -eq 0 ] || exit 1
