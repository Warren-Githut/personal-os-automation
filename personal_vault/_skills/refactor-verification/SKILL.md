---
name: refactor-verification
description: "Use when refactoring existing code. Prove behavior held."
version: 1.0.0
status: active
applies_to: [Hermes Desktop]
tags: [refactor, verification, golden-diff, testing, vault-code]
related_skills: [code-simplification, verify-parser-output, warren-code-quality-gates, qa-gate]
---

# Refactor Verification — prove behavior didn't change

> **Core rule:** "It still runs" is NOT proof of behavior preservation. Code can run clean and emit a wrong number. Proof is a **byte-level diff of outputs captured before and after**.
>
> **Second core rule:** when a verify step fails, the code is **not** the default suspect. Most failing cases are a wrong test assertion. Fixing code to satisfy a bad assertion silently breaks a correct fix.

Applies to any refactor of an existing Warren script: parsers, cron runners, insight/summary generators, vault tooling. All profiles.

## When to use

- Removing dead code, collapsing branches, deduplicating helpers, renaming, inlining
- Any change to logic that produces output Bố reads (numbers, insights, log lines)
- NOT for adding a feature or fixing a confirmed bug — those are behavior *changes*; verify them differently (assert the new expected output directly).

## Step 1 — Capture the golden output BEFORE touching anything

Write a probe that runs a **case matrix** through the real call path and dumps output to a file. The matrix must cover boundaries, not just the happy path:

- Every `if` / `elif` branch, and both sides of every threshold
- Edge inputs: missing/None fields, empty list, single-element, decimals, zero
- History/state of varying depth: none, below-threshold, at-threshold, far above, unsorted, with future-dated entries

```bash
python3 probe.py > golden-before.txt
```

Include at least one case that pins the *exact string* the consumer sees (log line, insight sentence) — those are what regress silently.

## Step 2 — Refactor ONE change at a time

Apply a single simplification, then re-run. Never batch several and test once — if it breaks you won't know which.

```bash
python3 probe.py > golden-after.txt
diff golden-before.txt golden-after.txt    # empty == proven identical
```

Non-empty diff → revert **that one** change and debug it. Do not proceed until clean.

## Step 3 — Triage failures: is the TEST wrong, or the CODE wrong?

Do this **before** editing product code. In practice most failures are test bugs — a case that never reached the branch you assumed, or an expectation of a feature that never existed.

1. **Print the real output** and determine which branch actually fired. A case designed for branch X frequently lands in branch Y because a precondition (delta, spread, count) wasn't actually met.
2. **Prove whether the behavior is pre-existing.** Run the same probe against the already-committed code:
   ```bash
   git show <sha>:<repo>/<path>:<file>   # copy to temp, import, re-run
   # or: git stash && python3 probe.py && git stash pop
   ```
   Identical result → the bug is **not** from your patch. Do not "fix" it here.
3. Only change product code once step 2 shows the code is genuinely wrong.
4. **Comment the test** explaining *why* the case lands in that branch and what precondition it needs. Without that, the next person repeats the identical mistake.

## Step 4 — Time-dependent logic: pin the clock, test multiple "todays"

Module-level `NOW = datetime.now()` / `CURRENT_YEAR` / `CURRENT_MONTH` and any `month > CURRENT_MONTH`-style heuristic are silent-bug hot spots: a single-date test can never reach the failing branch.

- Monkeypatch the constants per scenario, restore in `finally`
- Run **multiple simulated "today" values**: same day, next day, previous day, month/year wrap, the originally-reported case
- Exercise the threshold boundary at ±1

A heuristic written to handle one exception (e.g. year wrap) will usually fire for ordinary cases too. Prefer gating on a *semantic* condition (is this date impossibly far ahead?) over a proxy (is the month later?).

## Step 5 — Sanity checks must not read `HEAD`

`git show HEAD:<file>` as proof "the old code had the bug" **inverts the moment you commit the fix** → spurious failure. Pin the specific SHA that still contains the bug.

## Step 6 — Separate refactor from bugfix commits

A refactor commit and a bugfix commit in one diff cannot be reviewed or reverted independently, and the golden-diff proof for the refactor is worthless once behavior also changed. Commit them separately; state the split before starting so the user can veto it.

## Pitfalls

- **Asserting the test's own words back at it.** If a test greps for a literal that the current code emits, it passes while the underlying behavior is wrong. Assert the *semantic* fact, not the current string.
- **Floats.** `5/60` is `0.0833…`; `== 8.083` fails. Use `abs(a - b) < 1e-9`.
- **Proving behavior on a copy, never production.** For any write-path test, copy the data tree to a temp dir, redirect the module's path constants at it, and assert production is unchanged afterwards.
- **Report the honest result.** If a case is ambiguous in a way that needs a product decision, say so and leave it — don't silently pick a reading.
- **`git add -f` for gitignored-but-tracked paths.** Some vault `scripts/` dirs are gitignored yet tracked; plain `git add` refuses. Gate scripts that read staged-only content need staging first or they report "nothing staged".
- **Newest-on-top logs break naive block extraction.** A log that prepends newest entries means the block *after* a date is the next-newest one, not an older date; splitting on a specific neighbouring date returns the wrong block or raises IndexError. Split on a marker instead: `re.search(rf"### {date}\n(.*?)(?=\n### |\Z)", text, re.DOTALL)`.
- **Non-blocking diffs.** Piping a command into a truncating utility (`head`, `tail`, `grep -m`) masks the earlier command's real exit code — re-run without the pipe before trusting a result.

## Cross-links

- `code-simplification` — the how-to for the cleanup itself
- `verify-parser-output` — fact-check gate for parser *output data* (user-owned)
- `warren-code-quality-gates` — the pre-commit gate checklist (user-owned)

## References

- `references/golden-diff-harness.md` — reusable probe template + worked triage examples
