#!/usr/bin/env bash
# hermes-verify-harness-meta.sh — META-verification of verify_last_process_notes.sh.
#
# The harness's own --selftest only varies the DATE, leaving 10/11 checks PASS "by design".
# This proves the other assertions are NOT vacuous by building throwaway git repos under
# %TEMP% that violate one condition each, and asserting the matching check flips to FAIL.
# The real vault is never touched (DEBUG RULE: never dirty vault/GSheet/Telegram to debug).
H="$HOME/AppData/Local/hermes/profiles/personal_profile/skills/productivity/personal-process-notes/scripts/verify_last_process_notes.sh"
TMPROOT=/c/Users/khoans/AppData/Local/Temp
GOOD_TS=2026-08-14T09:21:29+07:00
SEED_TS=2026-08-12T08:02:20+07:00
P=0; F=0
ok(){ printf 'PASS | %s\n' "$1"; P=$((P+1)); }
no(){ printf 'FAIL | %s\n       %s\n' "$1" "$2"; F=$((F+1)); }

# Build a synthetic repo mirroring the vault layout: <root>/wc/personal_vault/_inbox/...
# so the harness's RELP/PSPEC pair behaves exactly as it does for real, unmodified.
setup(){
  R=$(mktemp -d "$TMPROOT/hermes-verify-metarepo-XXXXXX")
  git init -q --bare "$R/remote.git"
  mkdir -p "$R/wc/personal_vault/_inbox"
  ( cd "$R/wc" \
    && git init -q -b master . \
    && git config user.email t@t && git config user.name t \
    && printf '%s' "$SEED_TS" > personal_vault/_inbox/.last_process_notes \
    && git add -A && git commit -qm seed \
    && git remote add origin "$R/remote.git" && git push -q origin master ) >/dev/null 2>&1
  echo "$R"
}
# write $2 into the stamp, commit, and push unless $3 = nopush
commit_stamp(){
  ( cd "$1/wc" && printf '%s' "$2" > personal_vault/_inbox/.last_process_notes \
    && git add -A && git commit -qm cycle \
    && { [ "$3" = nopush ] || git push -q origin master; } ) >/dev/null 2>&1
}
run(){ HERMES_PPN_VAULT="$1/wc/personal_vault" bash "$H" "$2" 2>&1; }
cleanup(){ cd "$TMPROOT" && rm -rf "$1"; }

# expect a specific check to FAIL in $3 (the harness output)
want_fail(){ if printf '%s' "$3" | grep -q "FAIL | $2"; then ok "$1"; else no "$1" "check $2 did NOT fail — assertion is vacuous"; fi; }

echo "=== META: can verify_last_process_notes.sh assertions actually FAIL? ==="

# --- baseline: a correct cycle must be fully green, or every FAIL below is meaningless ---
R=$(setup); commit_stamp "$R" "$GOOD_TS"; OUT=$(run "$R" 2026-08-14)
if printf '%s' "$OUT" | grep -q 'PASSED=11 FAILED=0'; then ok "0. baseline correct cycle -> 11/11 PASS"
else no "0. baseline correct cycle -> 11/11 PASS" "$(printf '%s' "$OUT" | grep -E 'FAIL|PASSED=')"; fi
cleanup "$R"

# --- 4/5: uncommitted remainder + disk-vs-blob divergence ---
R=$(setup); commit_stamp "$R" "$GOOD_TS"
printf '%s' "2026-08-99T00:00:00+07:00" > "$R/wc/personal_vault/_inbox/.last_process_notes"
OUT=$(run "$R" 2026-08-14)
want_fail "4. dirty file -> 'no uncommitted remainder' FAILS" "4\. no uncommitted" "$OUT"
want_fail "5. dirty file -> 'disk == blob' FAILS"             "5\. disk == blob"  "$OUT"
cleanup "$R"

# --- 7: timestamp must strictly advance (guards a no-op / backwards rewrite) ---
R=$(setup); commit_stamp "$R" "2026-08-11T07:00:00+07:00"; OUT=$(run "$R" 2026-08-11)
want_fail "7. backwards timestamp -> 'strictly ADVANCED' FAILS" "7\. timestamp strictly" "$OUT"
cleanup "$R"

# --- 3a/3b: format + single-line ---
R=$(setup); commit_stamp "$R" "$GOOD_TS
stray second line"; OUT=$(run "$R" 2026-08-14)
want_fail "3b. multi-line file -> 'exactly one line' FAILS" "3b\. exactly one line" "$OUT"
cleanup "$R"

R=$(setup); commit_stamp "$R" "14/08/2026 09:21"; OUT=$(run "$R" 2026-08-14)
want_fail "3a. wrong format -> 'ISO8601 +07:00' FAILS" "3a\. ISO8601" "$OUT"
cleanup "$R"

# --- 8: unpushed commit ---
R=$(setup); commit_stamp "$R" "$GOOD_TS" nopush; OUT=$(run "$R" 2026-08-14)
want_fail "8. unpushed commit -> 'ancestor of origin/master' FAILS" "8\. commit is an ancestor" "$OUT"
cleanup "$R"

# --- 1c: the path-axis control must itself be able to fail ---
# Mirror the trap's inverse: if the repo-root-shaped path DID bind, 1c must go red.
R=$(setup)
mkdir -p "$R/wc/personal_vault/personal_vault/_inbox"
( cd "$R/wc" && printf '%s' "$GOOD_TS" > personal_vault/personal_vault/_inbox/.last_process_notes \
  && printf '%s' "$GOOD_TS" > personal_vault/_inbox/.last_process_notes \
  && git add -A && git commit -qm decoy && git push -q origin master ) >/dev/null 2>&1
OUT=$(run "$R" 2026-08-14)
want_fail "1c. decoy nested path binds -> path-axis control FAILS" "1c\. path-axis" "$OUT"
cleanup "$R"

# --- 6: is it a real check or a tautology? MINE is resolved BY $PSPEC, so a commit that
# does not touch the file can never be selected. `git rm --cached` does NOT expose this —
# history still contains a commit that touched the path, so MINE resolves to it and 6 passes.
# The ONLY failure mode left is MINE never resolving: the file was never committed at all.
R=$(mktemp -d "$TMPROOT/hermes-verify-metarepo-XXXXXX")
git init -q --bare "$R/remote.git"
mkdir -p "$R/wc/personal_vault/_inbox"
( cd "$R/wc" && git init -q -b master . \
  && git config user.email t@t && git config user.name t \
  && printf 'x\n' > personal_vault/other.txt && git add -A && git commit -qm seed \
  && git remote add origin "$R/remote.git" && git push -q origin master \
  && printf '%s' "$GOOD_TS" > personal_vault/_inbox/.last_process_notes ) >/dev/null 2>&1
OUT=$(run "$R" 2026-08-14)
want_fail "6. stamp never committed (MINE empty) -> 'commit touches file' FAILS" "6\. cycle commit actually" "$OUT"
cleanup "$R"

echo "-----"
echo "meta-verification: PASSED=$P FAILED=$F"
[ "$F" -eq 0 ]
