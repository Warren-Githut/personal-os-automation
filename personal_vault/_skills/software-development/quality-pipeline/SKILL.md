---
name: quality-pipeline
description: "Warren code-quality chain. Trigger: 'quality pipeline'."
type: skill
version: 1.0.0
status: active
applies_to: [Hermes Desktop]
---

# Quality Pipeline (Warren code-quality chain)

> Bố's dictated sequence for any parser/script/dashboard work. Run in ORDER.
> Each step is a real skill — load it, follow it, don't skip. This skill is the
> ORCHESTRATOR + the Warren-specific pitfall bank the individual skills don't carry.

## The chain (verbatim from Bố, 2026-07-27)

**Build phase:**
1. `using-agent-skills` — discover/invoke the right agent skill for the task class
2. `incremental-implementation` — slice-by-slice, ship each slice before next
3. `writing-great-skills` — make the skill predictable (if a new/updated skill resulted)
4. `test-driven-development` — RED before GREEN; write the test that will catch the bug

**Quality phase (after build, before commit):**
5. `improve-codebase-architecture` — audit shallow→deep (YAGNI scope; delete dead code)
6. `ab-test` — baseline vs simplified, assert OUTPUT IDENTICAL (behavior preserve)
7. `debugging-and-error-recovery` — reproduce hypotheses; if a bug surfaces, fix at seam
8. `code-simplification` — inline single-pass cleanup (default, cheap)
9. `simplify-code` — parallel 4-agent review (Reuse/Quality/Efficiency/Altitude)

## Hard rules (Warren-specific, learned 2026-07-27)

### R1 — Tracker ordering = SORT-DESC BY ISO WEEK, never positional arithmetic
`upsert_week`-style "move-up / insert-at-top" logic via index scanning is a **silent bug class**.
Reviewer (execution-verified) caught: re-running an OLD week via `--live` put it ABOVE the
newest week, corrupting newest-on-top. The verify gate only checked `count==1`, not ordering.
**Fix pattern (proven):** parse all `## YYYY-Wxx` blocks → dict-upsert by week_id →
**sort blocks DESC by ISO week** (`wk_key = lambda w: tuple(map(int, w.split('-W')))`) →
rebuild. Ordering correct BY CONSTRUCTION. See `col_weekly_parser.sort_week_blocks_on_top()`
which already does this (has HARD-ASSERT). Reference: `references/item-sales-case.md`.

### R2 — Dashboard template/built separation (avoid stale silent writes)
- `*.template.html` = has `__PAYLOADS__` (or `__PAYLOAD__`) placeholder, source of truth.
- `*.html` (built) = data inlined, this is the link target Bố opens.
- `--emit-html` MUST guard: if target lacks the placeholder → **ERR + refuse**, don't
  silently overwrite built-with-stale. Restore template from `_archives/dashboards/`.
- After any `--emit-html`, sync built → link-target file (or make template = built output).

### R3 — node absent → verify-parser-output runtime check falls back to struct-check
This machine has NO `node`. `verify-parser-output`'s "run the JS in a headless runtime" step
CANNOT run. Per the skill, flag "JS runtime unchecked" — do NOT claim green on runtime.
**Fallback that IS acceptable:** (a) struct-check the generated HTML — placeholder replaced,
`PAYLOADS` array valid JSON, canvas element present, correct week count; (b) independent
recompute the numbers from the raw source (SQL query direct, not via the parser) and assert
Δ=0.0%. Both together = sufficient evidence without node.

### R4 — Commit-Push Self-Gate (zone 🟡) runs BEFORE push
Print Q1 (SSOT simplify — no dup/junk?) + Q2 (automation readiness — manual parsers stay manual?)
and WAIT for Bố "commit push" / "approved". Never auto-push. Secret-scan: grep for
token/password before `git add -A`; `.private/` is gitignored — confirm.

### R5 — Reviewer-node (A10) is a SEPARATE pass, run in parallel with simplify-code batch
Spawn `reviewer-node` (independent PASS/FAIL + bug list) AND the 4 simplify-code reviewers
concurrently. Aggregate: apply SAFE/CAREFUL auto, FLAG RISKY (shared-constant promotion,
cross-parser refactor, new `--backfill` mode) as own tasks — don't inline RISKY.

## Warren corrections this session (embedded as rules)
- "nhé con ha" + batch command = Bố pre-approved autonomous execution; don't re-ask per slice.
- Quality pipeline is a CHAIN, not optional — run all 9 steps for parser/script work.
- After push, write a HANDOFF for the next chat (pending tasks, memory proposals, RISKY flags).

## Read-Only Code Review (Warren audit format)

When Bố asks for a **read-only code-quality review** ("do NOT modify"), use this report spec — distinct from the build-phase gates above. Full worked example: `references/warren-readonly-review-example.md`.

**One line per finding:**
```
file:line -> problem -> cost -> suggested fix | confidence | risk
```
- **confidence** = high|medium|low (how sure the finding is correct)
- **risk** = low|medium|high (blast radius of applying the fix)
Open with a **Confirmations** block (no duplication / tests green / no dead refs) so clean areas aren't silently assumed.

**Checklist (skill Python):** redundant state · copy-paste (verify `grep -rn "def <helper>"` for a helper redefined in the test instead of imported) · deeply nested conditionals · AI-slop comments (restate obvious code) · leaky abstractions (docstring promises behavior the function doesn't implement) · stringly-typed where a constant exists (grep FIRST; if none exists, the finding does NOT apply — don't invent a constant to flag) · naming (`wid` vs `week_id`).

**Chesterton's Fence — blame before removing:** run `git blame -w -- <file>` before recommending any deletion, especially comments. If blame returns `no such path ... in HEAD` the file is **untracked** → be conservative; do NOT flag removal of intent-carrying comments (cited rule `Warren §3a`, `regression: substring bug`, `# Monday`). These are intent, not slop.

**Verify empirically before flagging:** a docstring/behavior claim that's testable must be reproduced (run the function/regex/CLI in `terminal`) before you call it wrong. Worked example: a docstring claimed `## 2026-W30 (example)` "does NOT false-match"; running the regex proved a *standalone* `## 2026-W30 (example)` header **does** match (false SKIP) — real protection was the `^##\s+` anchor, `\b` actually guards prefix collisions (`2026-W3` vs `2026-W30`). High-confidence doc fix.

**Skip nits** (Bố: "skip nits") — omit borderline restate-comments / cosmetic naming unless they carry real cost; when unsure, mark confidence low.

## When NOT to run the full chain
- Trivial one-file tweak (<30 lines, no new logic) → `code-simplification` inline only.
- Pure vault .md edit → `vault-simplify-ssot` instead.

## Reference
- `references/item-sales-case.md` — full 2026-07-27 session: upsert_week sort-desc bug fix,
  template/built separation, reviewer-4 FINDING 2 (shared `_tracker_writer` task), RISKY flags.
