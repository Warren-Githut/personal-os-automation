# Verification harness notes

Captured 2026-08-09. Companion to `scripts/verify_cycle.sh` and the **Verification**
section of `SKILL.md`. Purpose: stop re-authoring a throwaway harness every cycle.

`verify_cycle.sh` is the canonical cycle-wide checker (checks 1-6, read-only-Sleep_Log
invariant, duplicate-date scan). The 2026-08-09 cycle needed a **file-scoped** harness for
the single product file it changed (`_inbox/.last_process_notes`) and, in writing it,
produced assertions `verify_cycle.sh` does not yet make. Fold these in rather than
maintaining a second script.

---

## Assertions worth folding into `verify_cycle.sh`

Anchor everything to the cycle's own SHA (`SHA=$(git log --format=%H -1 -- "$PSPEC")`),
never `HEAD` — a concurrent `capture-sleep` commit re-targets `HEAD` mid-verification.

| # | Assertion | Why it earns its place |
|---|---|---|
| 0 | **Non-vacuity guard:** `git ls-files -- "$PSPEC" \| wc -l` == 1 | Catches the cwd-vs-repo-root pathspec bug *directly* instead of hoping a date-axis selftest trips it. A pathspec matching nothing makes every downstream `status --porcelain --` check silently pass. |
| 1c | Stamp matches `????-??-??T??:??:??+07:00` | Shape check. A truncated or TZ-less write still satisfies a date-prefix comparison. |
| 4 | `git show "HEAD:$RELP"` equals the disk bytes | Proves the commit captured what is on disk — not a stale blob from a partially-staged write. |
| 6 | `git show "${SHA}~1:$RELP"` is the **prior** cycle's date | Proves the file genuinely advanced rather than being re-committed unchanged. |
| 7 | Lexicographic `"$NEW" > "$OLD"` | Monotonic guard. ISO-8601 sorts correctly as a plain string, so this needs no date parsing. |
| 8 | `git merge-base --is-ancestor "$SHA" origin/master` | Pushed-state check that survives later commits, unlike comparing `HEAD` to `origin/master`. |
| 9 | `git show --name-only --format="" "$SHA" \| grep -c '051_Sleep_Log'` == 0 | Blast-radius guard for the read-only-Sleep_Log invariant, scoped to *this* commit. |

## The two path variables (never mix)

```
RELP=personal_vault/_inbox/.last_process_notes   # repo-root-relative: blob refs, --name-only TEXT
PSPEC=_inbox/.last_process_notes                 # cwd-relative: every git PATHSPEC arg
```

`git show SHA:path` is always repo-root-relative; `--` pathspecs are always cwd-relative.
They differ **inside the same command**. See SKILL.md for the full incident write-up.

## Negative control must vary more than one axis

- `--selftest` with a bogus **date/SHA** → on 2026-08-09 failed checks 1b, 5, 6. Good, but
  it leaves the tree clean, so every pathspec-based check still reads the same clean state
  and passes for the wrong reason.
- The **path** axis needs a throwaway repo under `%TEMP%` (recipe in SKILL.md). Confirmed
  2026-08-09: correct cwd-relative pathspec on a dirty file → `1` (can fail); repo-root
  form on the same dirty file → `0` (the vacuous bug, reproduced); `git ls-files` on the
  bad form → `0`, which is exactly what assertion 0 above is designed to catch.

Never dirty the vault to prove a check can fail. Throwaway repo, then `rm -rf` it.

## Evidence retention

Write the harness to a **stable** path and `tee` both runs into one log; do not delete
either until after the report is delivered. A deleted harness reads downstream as
"never verified" and forces a full rewrite-and-rerun.

```
S=/c/Users/khoans/AppData/Local/Temp/hermes-verify-<thing>.sh
E=/c/Users/khoans/AppData/Local/Temp/hermes-verify-<thing>.evidence.txt
```

Call the result **ad-hoc verification**, never "suite green" — there is no canonical test
suite in `Personal_OS` for a data-only cycle.

## 🚨 PROMOTED OUT OF %TEMP% — use `scripts/verify_last_process_notes.sh` (2026-08-14)

The section below described this harness as living at
`/c/Users/khoans/AppData/Local/Temp/hermes-verify-last-process-notes.sh`. **Do not put it
there.** `%TEMP%` is scratch: on 2026-08-14 a `write_file` to that exact name silently
clobbered the 10-check 08-11 version, which then had to be rebuilt from this document.
A harness meant for reuse *every* cycle belongs in the skill dir next to `verify_cycle.sh`:

⚠️ **"In the skill dir" does NOT mean git-tracked — verified 2026-08-14.** `personal_vault/.gitignore:63`
ignores **`scripts/`** (any depth), so the live SSOT mirror
`.scripts/skills/productivity/personal-process-notes/scripts/*.sh` **cannot be committed**;
`git add` refuses it and `git add -f` would fight the rule. `verify_cycle.sh` is in exactly the
same position — `git ls-files | grep verify_cycle` returns only **`_archives/skills/…`** copies,
never the live one. So:
- **Canonical live copy:** the AppData skill dir (persistent — this is the real fix over `%TEMP%`).
- **Versioned copy:** an archive under `_archives/skills/` (that path is not under a `scripts/`
  dir, so it is trackable). Flat naming: `personal-process-notes_verify_last_process_notes_backup_YYYY-MM-DD.sh`.

Re-archive after any edit to the script, or the only durable copy is an untracked file in AppData.

```
bash "$HOME/AppData/Local/hermes/profiles/personal_profile/skills/productivity/personal-process-notes/scripts/verify_last_process_notes.sh"
bash "…/scripts/verify_last_process_notes.sh" --selftest    # date-axis control
```

11 checks, **no per-cycle hand-editing** — the old `MINE` + `WANT_DATE` chore is gone.
`WANT_DATE` defaults to `date +%Y-%m-%d`, and the cycle commit self-resolves via
`git log -1 --format=%H -- "$PSPEC"` (the commit that last touched *this* file). That is
immune to the 2026-08-05 concurrent-writer problem by construction: `capture-sleep` never
touches `.last_process_notes`, so it cannot re-target the assertions the way `HEAD` did.

Adds over the 08-11 version: `3b` exactly-one-line, `6` the commit genuinely touches the
file, `7` timestamp **strictly advanced** (catches a no-op rewrite reported as success), and
`1c` as an **always-on** path-axis control rather than an opt-in mode.

Result 2026-08-14: real run **11/11 PASS**; `--selftest` 1 FAIL (check 2) → live.

### Meta-verified 2026-08-14 — every assertion proven able to FAIL (9/9)

A date-flip `--selftest` leaves **10 of 11 checks PASS "by design"**, which is a lot of
unexercised logic to call verified. Each assertion was therefore driven red in a throwaway
repo under `%TEMP%` mirroring the vault layout (`<root>/wc/personal_vault/_inbox/…`, so the
`RELP`/`PSPEC` pair behaves exactly as it does for real). The real vault was never touched.
This is why the script reads `VAULT=${HERMES_PPN_VAULT:-…}` — injectable purely so the
checker can be checked; the default is still the real vault.

| Scenario | Check driven red |
|---|---|
| baseline correct cycle | none — 11/11 PASS (else every FAIL below is meaningless) |
| file modified after commit | `4` uncommitted remainder, `5` disk == blob |
| timestamp written backwards | `7` strictly advanced |
| second line appended | `3b` exactly one line |
| `14/08/2026 09:21` instead of ISO | `3a` ISO8601 +07:00 |
| commit not pushed | `8` ancestor of origin/master |
| decoy `personal_vault/personal_vault/_inbox/` created | `1c` path-axis control |
| stamp never committed (`MINE` empty) | `6` commit touches file |

**Check `6` is genuinely narrow — know what it does and does not buy.** Because `MINE` is
resolved *by* `$PSPEC` (`git log -1 --format=%H -- "$PSPEC"`), a commit that does not touch
the file can never be selected, so `6` cannot fail the way it appears to promise. Note
`git rm --cached` does **not** expose this: history still holds a commit touching the path,
`MINE` resolves to it, and `6` passes. Its one real failure mode is `MINE` never resolving at
all (file never committed → empty). Keep it as a resolution guard, not as evidence the right
commit was chosen.

Reusable recipe if you extend the harness: mirror the vault's directory shape inside the
throwaway repo rather than parameterising `RELP`/`PSPEC` — it keeps the code under test
byte-identical to production, so the meta-test cannot pass for the wrong reason.

### Why `1c` is not optional — the vacuous pass, caught live
Running the harness with the wrong repo-root pathspec on 2026-08-14 produced this:

```
FAIL | 1a. file exists on disk            got=[missing]
FAIL | 1b. pathspec binds to tracked file got=[unmatched]
PASS | 4. no uncommitted remainder        <-- WRONG, and silent
```

Check `4` **passed on a pathspec matching nothing** — `git status --porcelain -- <bad>`
returns zero lines, which is indistinguishable from "clean". A dirty-check is therefore only
sound when paired with a *binding* assertion. Never ship a `git status --porcelain --` or
`git diff --` check without a `ls-files --error-unmatch` beside it.

## Ready-made harness for the `.last_process_notes` write (2026-08-11, superseded — see above)

The post-turn coding gate fires on `_inbox/.last_process_notes` as a "changed path" even
when `verify_cycle.sh` already ran green — the cycle harness verifies the *cycle*, the gate
wants the *file*. Don't re-author it: reuse
`/c/Users/khoans/AppData/Local/Temp/hermes-verify-last-process-notes.sh` (10 checks; update
`MINE` + `WANT_DATE` at the top each cycle). It asserts existence, single-line ISO8601 with
`+07:00`, date == cycle, **timestamp strictly advanced** vs `MINE~1` blob, presence in this
cycle's commit, no uncommitted remainder, and on-disk == committed blob.

Its check `2b` is the cheap **path-axis control** worth copying into any new harness — it
proves the two path variables are not interchangeable, which a date-flip `--selftest` can
never catch (a wrong pathspec passes *vacuously*, it does not fail loudly):

```
git ls-files --error-unmatch -- "$PSPEC" ; # want exit 0 — cwd-relative form binds
git ls-files --error-unmatch -- "$RELP"  ; # want exit 1 — repo-root form must NOT bind
```

Real run 10/10 PASS; `--selftest` 4 FAIL (checks 4, 5, 6, 8) → live. Note checks 1, 2a, 2b,
3a, 3b, 7 stay PASS under selftest **by design** — they are invariants of the file, not of
the date/commit being varied, so a partial-fail selftest is the correct signal here, not a
weak one.
