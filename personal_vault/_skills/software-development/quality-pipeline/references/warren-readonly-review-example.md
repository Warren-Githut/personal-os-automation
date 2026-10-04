# Warren Read-Only Code Review — Worked Example

Condensed from the 2026-07-27 review of `ops-grabfood-cron/scripts/guard.py` + `guard_test.py`.
Demonstrates the report format, Chesterton's Fence, and empirical verification before flagging.

## Confirmations (clean)
- No `compute_week_id` duplication: `grep -rn "def compute_week_id"` → only `guard.py:14`; the test imports it (`guard.compute_week_id`).
- Tests green: `python3 guard_test.py` → 4/4 PASS.
- No shared `RUN`/`SKIP`/week-id constant exists in the skill → "stringly-typed where a constant exists" does NOT apply.

## Findings (file:line -> problem -> cost -> fix | confidence | risk)

`guard.py:26` -> docstring example `'## 2026-W30 (example)'` claims it "does NOT false-match" but a standalone `## 2026-W30 (example)` header DOES match the regex and causes a false SKIP -> misleads a future maintainer into dropping the `^##\s+` anchor and reintroducing the substring bug -> reword docstring to state the real mechanism (`^##\s+` anchors week_id as first token after `## `; `\b` blocks prefix collisions `2026-W3` vs `2026-W30`) | confidence: high | risk: low

`guard.py:6-9` vs `:24` -> module docstring describes a 2-part rule (07:00 always runs + later ticks skip-if-present) but `should_run_pipeline` implements only the skip half; 07:00-always-run is the caller's job -> reader assumes the guard enforces both -> add one line clarifying the function covers only skip-if-present | confidence: high | risk: low

`guard.py:36` -> naming `wid` vs `week_id` (function param) inconsistent abbreviation -> minor confusion -> rename `wid` -> `week_id` | confidence: high | risk: low

`guard.py:29` -> `# empty log -> definitely run` restates `return True` (borderline AI-slop) -> tiny cost -> optional drop or expand to the rationale | confidence: low | risk: low

`guard.py:19` -> `(ref.weekday() + 1) % 7` opaque; docstring "yesterday-ish" imprecise -> readability -> add a precise comment or use `ref.isoweekday() % 7` | confidence: medium | risk: low

## Empirically verified before flagging
Ran the regex in `terminal`:
- `match("## 2026-W30 (example)", "2026-W30")` -> True  (docstring's "does NOT match" is WRONG)
- `match("## Template example: ## 2026-W30 ...", "2026-W30")` -> False  (the real `^##\s+` anchor protects)
- `match("## 2026-W30 | x", "2026-W3")` -> False  (`\b` blocks prefix collision)
=> the docstring reword is high-confidence.

## Chesterton's Fence applied
`git blame` on these files returned `no such path ... in HEAD` — the files are untracked (`?? ops-grabfood-cron/`). Per-line history was unavailable, so we did NOT recommend deleting ANY comment (the `regression:` / `# Monday` comments carry intent). Fixes were doc-only and conservative.
