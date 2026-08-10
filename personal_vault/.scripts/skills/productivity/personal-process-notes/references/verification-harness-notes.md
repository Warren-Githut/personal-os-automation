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
