#!/usr/bin/env bash
# verify_last_process_notes.sh — file-level harness for _inbox/.last_process_notes
#
# WHY THIS LIVES HERE (2026-08-14): the post-turn coding gate fires on
# `_inbox/.last_process_notes` as a changed path even when verify_cycle.sh is green
# (that one verifies the CYCLE, the gate wants the FILE). Two prior cycles kept this
# harness in %TEMP%, where it is scratch: a same-name write_file clobbers it and the
# 10-check 08-11 version was lost that way. Keep it in the skill dir, SSOT-synced.
#
# Usage:  bash verify_last_process_notes.sh [YYYY-MM-DD]   # default: today
#         bash verify_last_process_notes.sh --selftest      # date-axis control, MUST fail
#
# Self-resolving: the cycle commit is found via `git log -1 -- <pathspec>` (the commit that
# last touched THIS file), never HEAD — so a concurrent capture-sleep commit cannot
# re-target the assertions (2026-08-05 lesson).
VAULT=/c/Users/khoans/Documents/Personal_OS/personal_vault
RELP=personal_vault/_inbox/.last_process_notes   # repo-root-relative: blob refs, --name-only TEXT
PSPEC=_inbox/.last_process_notes                 # cwd-relative: every git PATHSPEC arg

cd "$VAULT" || { echo "cannot cd $VAULT"; exit 9; }

WANT_DATE=$(date +%Y-%m-%d)
[ -n "$1" ] && [ "$1" != "--selftest" ] && WANT_DATE=$1
[ "$1" = "--selftest" ] && WANT_DATE=1999-01-01

MINE=$(git log -1 --format=%H -- "$PSPEC")
P=0; F=0
pass(){ printf 'PASS | %s\n' "$1"; P=$((P+1)); }
fail(){ printf 'FAIL | %s\n       got  = [%s]\n       want = [%s]\n' "$1" "$2" "$3"; F=$((F+1)); }
cmp_(){ if [ "$2" = "$3" ]; then pass "$1"; else fail "$1" "$2" "$3"; fi; }

echo "=== .last_process_notes verification — date: $WANT_DATE | commit: ${MINE:0:7} ==="

# --- 1. the file is real, and the two path variables are NOT interchangeable ---
if [ -f "$PSPEC" ]; then pass "1a. file exists on disk"; else fail "1a. file exists on disk" "missing" "present"; fi
if git ls-files --error-unmatch -- "$PSPEC" >/dev/null 2>&1; then
  pass "1b. cwd-relative pathspec BINDS to a tracked file"
else
  fail "1b. cwd-relative pathspec BINDS to a tracked file" "unmatched" "tracked"
fi
# always-on path-axis control: repo-root form must NOT bind from inside the vault.
# Without this, check 4 below passes VACUOUSLY on a wrong pathspec (2026-08-08 trap,
# reproduced live 2026-08-14: wrong pathspec -> 0 dirty lines -> silent PASS).
if git ls-files --error-unmatch -- "$RELP" >/dev/null 2>&1; then
  fail "1c. path-axis control: repo-root form must not bind" "bound" "unmatched"
else
  pass "1c. path-axis control: repo-root form correctly does NOT bind"
fi

# --- 2/3. content shape ---
TS=$(cat "$PSPEC" 2>/dev/null)
cmp_ "2. timestamp dated this cycle" "${TS:0:10}" "$WANT_DATE"
if printf '%s' "$TS" | grep -Eq '^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}\+07:00$'; then
  pass "3a. ISO8601 +07:00, single line ($TS)"
else
  fail "3a. ISO8601 +07:00, single line" "$TS" "YYYY-MM-DDTHH:MM:SS+07:00"
fi
cmp_ "3b. exactly one line" "$(wc -l < "$PSPEC" | tr -d ' ')" "0"

# --- 4-7. git state, all anchored to $MINE (never HEAD) ---
cmp_ "4. no uncommitted remainder" "$(git status --porcelain -- "$PSPEC" | wc -l | tr -d ' ')" "0"
cmp_ "5. disk == blob committed in ${MINE:0:7}" "$(git show "$MINE:$RELP" 2>/dev/null)" "$TS"
if git show --name-only --format='' "$MINE" | grep -qx "$RELP"; then
  pass "6. cycle commit actually touches this file"
else
  fail "6. cycle commit actually touches this file" "absent" "$RELP"
fi
PREV=$(git show "$MINE~1:$RELP" 2>/dev/null)
if [[ -n "$PREV" && "$TS" > "$PREV" ]]; then
  pass "7. timestamp strictly ADVANCED (prev: ${PREV:0:10})"
else
  fail "7. timestamp strictly ADVANCED" "prev=[$PREV] now=[$TS]" "now > prev"
fi
if git merge-base --is-ancestor "$MINE" origin/master 2>/dev/null; then
  pass "8. commit is an ancestor of origin/master (pushed)"
else
  fail "8. commit is an ancestor of origin/master (pushed)" "unpushed" "pushed"
fi

echo "-----"
echo "ad-hoc verification: PASSED=$P FAILED=$F"
if [ "$1" = "--selftest" ]; then
  if [ "$F" -gt 0 ]; then
    echo "SELFTEST OK — checks are live (failed against a bogus date, as intended)."
    echo "  Note: 1a/1b/1c/3a/3b/4/5/6/7/8 stay PASS by design — they are invariants of the"
    echo "  FILE, not of the date being varied. Partial fail is the correct signal here."
    exit 0
  fi
  echo "SELFTEST BROKEN — bogus date still passed everything; assertions are vacuous."; exit 1
fi
[ "$F" -eq 0 ]
