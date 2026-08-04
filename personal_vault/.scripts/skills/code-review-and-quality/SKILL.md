---
name: code-review-and-quality
description: Conducts multi-axis code review. Use before merging any change. Use when reviewing code written by yourself, another agent, or a human. Use when you need to assess code quality across multiple dimensions before it enters the main branch.
---

# Code Review and Quality

## Overview

Multi-dimensional code review with quality gates. Every change gets reviewed before merge — no exceptions. Review covers five axes: correctness, readability, architecture, security, and performance.

**The approval standard:** Approve a change when it definitely improves overall code health, even if it isn't perfect. Perfect code doesn't exist — the goal is continuous improvement. Don't block a change because it isn't exactly how you would have written it. If it improves the codebase and follows the project's conventions, approve it.

## When to Use

- Before merging any PR or change
- After completing a feature implementation
- When another agent or model produced code you need to evaluate
- When refactoring existing code
- After any bug fix (review both the fix and the regression test)
- **After file operations (deletions, renames, config changes) that affect system integrity** — even without code, changes like profile-skill deletions, path updates, or frontmatter normalizations need correctness review

## Reviewing Non-Code Changes (Configs, File Ops, Markdown)

When the deliverable is NOT code but file operations (deletions, sed patches, markdown edits, config updates), adapt the 5-axis review:

| Axis | File-Op Equivalent | Check |
|------|-------------------|-------|
| Correctness | Do sed/regex patterns match ALL targets? | `grep -r 'old_pattern'` → zero remaining |
| Readability | Are commit messages descriptive? | Message explains *why*, not just *what* |
| Architecture | Do paths/references still resolve? | Check hardcoded paths, symlinks, imports |
| Security | Are old files gone without side effects? | Scan for remaining references to deleted paths |
| Performance | No issue (markdown edits are 0-cost) | Skip unless relevant |

### Prompt-Based Skills (Hermes SKILL.md)

When reviewing a Hermes skill (pure prompt, no Python code):

| Axis | What to Check |
|------|---------------|
| Correctness | Do steps cover all expected scenarios? Boundaries defined (Always/Ask/Never)? Output format specified? |
| Readability | Non-IT friendly language? Scannable structure (tables, emoji markers)? Example flow included? |
| Architecture | Trigger = skill name? `--all` flag for multi-profile? Cron schedule appropriate? |
| Security | "Never" rules clear? External actions gated behind approval? Zone 🔴 tasks protected? |
| Performance | Cron frequency reasonable? Prompt-only = zero runtime cost. |

#### Script-Backed Skills (Hermes SKILL.md + Python runner)

When the skill ships a `scripts/*.py` runner invoked via documented commands, the review MUST verify the documented CLI against the actual argparse surface — doc/code drift here produces commands that `argparse`-error at runtime:

| Check | How | Failure class |
|-------|-----|---------------|
| Documented flags exist in runner | `grep -nE "add_argument" scripts/*.py` → compare `--scope`/`--type` choices vs SKILL.md Commands block | Doc lists a flag the runner rejects → crash on invocation |
| `choices=[...]` matches docs | Read `parser.add_argument("--x", choices=[...])` → every choice in SKILL.md must be in the list (and vice versa) | SKILL.md documents `--type memory` but runner only accepts `parser/prompt/vault` → command fails |
| Dead `references/*.md` links | `grep -nE "references/.*\.md" SKILL.md` → every cited file must `ls` under `references/` | Cites a checklist that was never written → broken link, self-contradicts "stale refs are bugs" |
| Stale tool/cron names | Grep SKILL.md for names of tools/crons the user later deprecated | References a retired cron (`ops-lint`) after it was merged into `ops-index-sync` |

**Pitfall (2026-07-13):** A skill's SKILL.md can document commands the runner does NOT accept. In this session, `ab-test` documented `--type memory`/`--type model` (with full methodology) but `ab_test_runner.py` only accepted `parser/prompt/vault` — passing those flags would `argparse`-error. Same for `battle-test --scope memory` (runner accepted `all/parser/scripts/vault/skills`, no `memory`). Fix: after editing a skill's docs, grep the runner's `add_argument` lines and confirm every documented flag/choice is accepted. Treat documented-but-unsupported commands as a Critical doc bug. Keep methodology-only variants (no script backing) in `references/` and explicitly note "runner supports X only" so the user doesn't hit an argparse error.

When assessing whether code-simplification is applicable: if zero code was written or modified (only file operations + config edits), simplification is **not applicable** — mark as "skipped" and document why.

## The Five-Axis Review

Every review evaluates code across these dimensions:

### 1. Correctness

Does the code do what it claims to do?

- Does it match the spec or task requirements?
- Are edge cases handled (null, empty, boundary values)?
- Are error paths handled (not just the happy path)?
- Does it pass all tests? Are the tests actually testing the right things?
- Are there off-by-one errors, race conditions, or state inconsistencies?

#### Python Data Pipeline Anti-Patterns (Check Explicitly)

| Anti-Pattern | Why It's Wrong | Fix |
|---|---|---|
| `max(aggs, key=...)` / `min(aggs, ...)` before checking `aggs` is non-empty | `ValueError` on empty list (filtered data, all-None rows) | `if not aggs: return []` early guard |
| Aggregation chain where intermediate step produces `None` but later step assumes `dict` | `None` propagates silently to crash | Filter Nones at each step: `aggs = [a for a in aggs if a]` |
| `value == recompute(value)` verify check | Compare `abs(computed - computed) < eps` always passes — gate catches nothing | Replace with CROSS-SOURCE assertion: `ot >= 0`, `ot <= total`, `covers > 0`, `hc > 0`, `regular+ot ≈ total` using independent inputs. Require sources (exit if all-zero), don't silent-zero-fill |
| Verify/assertion block compares a computed value to its own re-computation (e.g. `abs(round(x*100,1) - round(x*100,1)) < eps`) | Always `0 < eps` → check is a **no-op**; mis-parsed data (ot=0, covers=0, None) sails through the "safety gate" and gets written | Use **CROSS-SOURCE assertions**: independent inputs must agree — `ot>=0`, `ot<=total`, `covers>0`, `hc>0`, `regular+ot≈total` from SEPARATE inputs. Count only real checks; a gate that always passes is worse than no gate (false assurance). |

#### String & Regex Pitfalls (Check Explicitly)

| Anti-Pattern | Why It's Wrong | Fix |
|---|---|---|
| Raw f-string with `\\\` line continuation intended as `\n` | `\\` is literal backslash in raw strings, not newline escape. Continuation produces `\` + LF (0x5C 0x0A); `re` treats `\` before non-special char as a no-op. Works by accident, fragile. | Use single-line: `rf"... .*?\n(.*?)(?=\n## |\Z)"` |
| Unicode em dash `—` (U+2014) in markdown output | Some parsers treat it inconsistently; vault constraint may prohibit it. | Use hyphen `-` (U+002D) |
| Nested quotes in f-string using same quote type | `f"outer {d[\"key\"]}"` is SyntaxError before Python 3.12 | Use opposite quotes: `f"outer {d['key']}"` |

### 2. Readability & Simplicity

Can another engineer (or agent) understand this code without the author explaining it?

- Are names descriptive and consistent with project conventions? (No `temp`, `data`, `result` without context)
- Is the control flow straightforward (avoid nested ternaries, deep callbacks)?
- Is the code organized logically (related code grouped, clear module boundaries)?
- Are there any "clever" tricks that should be simplified?
- **Could this be done in fewer lines?** (1000 lines where 100 suffice is a failure)
- **Are abstractions earning their complexity?** (Don't generalize until the third use case)
- Would comments help clarify non-obvious intent? (But don't comment obvious code.)
- Are there dead code artifacts: no-op variables (`_unused`), backwards-compat shims, or `// removed` comments?

### 3. Architecture

Does the change fit the system's design?

- Does it follow existing patterns or introduce a new one? If new, is it justified?
- Does it maintain clean module boundaries?
- Is there code duplication that should be shared?
- Are dependencies flowing in the right direction (no circular dependencies)?
- Is the abstraction level appropriate (not over-engineered, not too coupled)?

### 4. Security

For detailed security guidance, see `security-and-hardening`. Does the change introduce vulnerabilities?

- Is user input validated and sanitized?
- Are secrets kept out of code, logs, and version control?
- Is authentication/authorization checked where needed?
- Are SQL queries parameterized (no string concatenation)?
- Are outputs encoded to prevent XSS?
- Are dependencies from trusted sources with no known vulnerabilities?
- Is data from external sources (APIs, logs, user content, config files) treated as untrusted?
- Are external data flows validated at system boundaries before use in logic or rendering?

### 5. Performance

For detailed profiling and optimization, see `performance-optimization`. Does the change introduce performance problems?

- Any N+1 query patterns?
- Any unbounded loops or unconstrained data fetching?
- Any synchronous operations that should be async?
- Any unnecessary re-renders in UI components?
- Any missing pagination on list endpoints?
- Any large objects created in hot paths?

## Change Sizing

Small, focused changes are easier to review, faster to merge, and safer to deploy. Target these sizes:

```
~100 lines changed   → Good. Reviewable in one sitting.
~300 lines changed   → Acceptable if it's a single logical change.
~1000 lines changed  → Too large. Split it.
```

**What counts as "one change":** A single self-contained modification that addresses one thing, includes related tests, and keeps the system functional after submission. One part of a feature — not the whole feature.

**Splitting strategies when a change is too large:**

| Strategy | How | When |
|----------|-----|------|
| **Stack** | Submit a small change, start the next one based on it | Sequential dependencies |
| **By file group** | Separate changes for groups needing different reviewers | Cross-cutting concerns |
| **Horizontal** | Create shared code/stubs first, then consumers | Layered architecture |
| **Vertical** | Break into smaller full-stack slices of the feature | Feature work |

**When large changes are acceptable:** Complete file deletions and automated refactoring where the reviewer only needs to verify intent, not every line.

**Separate refactoring from feature work.** A change that refactors existing code and adds new behavior is two changes — submit them separately. Small cleanups (variable renaming) can be included at reviewer discretion.

## Change Descriptions

Every change needs a description that stands alone in version control history.

**First line:** Short, imperative, standalone. "Delete the FizzBuzz RPC" not "Deleting the FizzBuzz RPC." Must be informative enough that someone searching history can understand the change without reading the diff.

**Body:** What is changing and why. Include context, decisions, and reasoning not visible in the code itself. Link to bug numbers, benchmark results, or design docs where relevant. Acknowledge approach shortcomings when they exist.

**Anti-patterns:** "Fix bug," "Fix build," "Add patch," "Moving code from A to B," "Phase 1," "Add convenience functions."

## Review Process

### Step 1: Understand the Context

Before looking at code, understand the intent:

```
- What is this change trying to accomplish?
- What spec or task does it implement?
- What is the expected behavior change?
```

### Step 2: Review the Tests First

Tests reveal intent and coverage:

```
- Do tests exist for the change?
- Do they test behavior (not implementation details)?
- Are edge cases covered?
- Do tests have descriptive names?
- Would the tests catch a regression if the code changed?
```

### Step 3: Review the Implementation

Walk through the code with the five axes in mind:

```
For each file changed:
1. Correctness: Does this code do what the test says it should?
2. Readability: Can I understand this without help?
3. Architecture: Does this fit the system?
4. Security: Any vulnerabilities?
5. Performance: Any bottlenecks?
```

### Step 4: Categorize Findings

Label every comment with its severity so the author knows what's required vs optional:

| Prefix | Meaning | Author Action |
|--------|---------|---------------|
| *(no prefix)* | Required change | Must address before merge |
| **Critical:** | Blocks merge | Security vulnerability, data loss, broken functionality |
| **Nit:** | Minor, optional | Author may ignore — formatting, style preferences |
| **Optional:** / **Consider:** | Suggestion | Worth considering but not required |
| **FYI** | Informational only | No action needed — context for future reference |

This prevents authors from treating all feedback as mandatory and wasting time on optional suggestions.

### Step 5: Verify the Verification

Check the author's verification story:

```
- What tests were run?
- Did the build pass?
- Was the change tested manually?
- Are there screenshots for UI changes?
- Is there a before/after comparison?
```

#### Stale Verification Banner (Hermes desktop pitfall — 2026-07-13)

After an edit, Hermes may surface a "Verification status: stale / unverified" banner. That banner replays the LAST ad-hoc script's output — which is frequently from a PRIOR turn (e.g. an old threshold test, or a list of temp scripts that were already deleted). **Do not trust the banner as evidence for the current change.**

- If the banner's "last output" references a different behavior than what you just edited → it is stale. Ignore it.
- Always produce FRESH evidence for the actual changed path: write a `hermes-verify-*` script under `C:/Users/khoans/AppData/Local/Temp` (OS-safe `tempfile`), run it, clean it up, and label the result explicitly as "ad-hoc verification, not suite green."
- A verify script that FAILS on a trivial self-bug (e.g. capturing a YAML-quoted value so `len()!=10`, or a regex that matches `<option>` text instead of JSON) is a HARNESS bug, not a code defect. Re-check the actual artifact (read the file / `json.loads` the embedded payload) before concluding the code is broken.

#### Stale References in External Artifacts (calendar / runbook / CONTEXT.md)

When a change deletes or de-scopes a file/skill/orchestrator, hardcoded pointers to it elsewhere become wrong. Review these as part of the change:

- **Google Calendar event descriptions**, runbook `.md` files, and `CONTEXT.md` entries often hardcode command strings or claim automation that no longer exists.
- Concrete example (2026-07-13): a COL Weekly calendar description referenced `run_monday_gsheet_parsers.py` (a deleted orchestrator) and claimed "Monday 09:45 parsers auto-run" when the user actually runs the COL parser MANUALLY (no cron). The description was stale + misleading.
- Fix: when something is deleted/de-scoped, grep calendar descriptions, runbooks, and `CONTEXT.md` for its name; update or remove the reference. Treat any "auto-run" claim as suspect — verify the cron/automation actually exists before leaving the claim in place.

## Multi-Model Review Patterns

### Sequential (Model Handoff)
Use different models for different review perspectives:

```
Model A writes the code
    │
    ▼
Model B reviews for correctness and architecture
    │
    ▼
Model A addresses the feedback
    │
    ▼
Human makes the final call
```

This catches issues that a single model might miss — different models have different blind spots.

**Example prompt for a review agent:**
```
Review this code change for correctness, security, and adherence to
our project conventions. The spec says [X]. The change should [Y].
Flag any issues as Critical, Important, or Suggestion.
```

### Parallel Dispatch via delegate_task

When the user asks for **both code review AND code simplification** (or similar multi-perspective analysis), dispatch them as parallel subagents via `delegate_task(tasks=[...])`. Each subagent gets its own isolated context and toolset — they run simultaneously and don't block each other.

**When to use:**
- User explicitly asks for multiple review axes (e.g., "code-review-and-quality and code-simplification")
- Review + Simplify addresses the same changed files from different angles
- Each subagent only reads files (no write conflicts)

**Pattern:**
```python
delegate_task(tasks=[
    {
        "goal": "Review changes in FILE for 5 axes: correctness, readability, architecture, security, performance",
        "context": "File changed: ...\nWhat was changed: ...",
        "toolsets": ["file"]
    },
    {
        "goal": "Identify simplification opportunities in FILE",
        "context": "File changed: ...\nCode region: ...",
        "toolsets": ["file"]
    }
])
```

**After both complete:**
1. Combine findings — sort by severity (Critical → Important → High → Medium → Low)
2. Present aggregated report to the user with a choice: apply all / apply important+high / skip
3. If user picks a batch, apply each fix as a `patch` on the affected file
4. Re-run verification after all fixes (compile + end-to-end + idempotency)

**Pitfall — out-of-date results:** If the user applies some suggestions but leaves others, the subagent results become stale. Re-dispatch rather than cherry-picking from old output. Each fix batch should be applied atomically and re-verified.

**Pitfall (2026-07-13): parallel `delegate_task` review results may NOT cleanly re-enter main context.** Dispatched review+simply subagents returned "in background"; the consolidated results did not reliably surface as a readable message in the main thread (and a sibling subagent emitted a spurious "modified file" warning on a file it only read). Net effect: the main agent couldn't rely on the subagent output to drive the fix batch. **Mitigation:** after dispatching review/simplify subagents, do NOT assume their output is visible — re-read the changed files yourself with `read_file` + run the 5-axis review directly (you already loaded both skills), then present findings + apply the user-approved batch. Subagents are useful for parallel labor, but the main agent must verify on disk and own the final findings, not trust a possibly-lost subagent transcript. This dovetails with "Verify Reviewer Findings on Disk" below.

**Example from session 2026-06-29:** COL weekly parser `cross_check_revenue()` — dispatched code-review + simplification as parallel subagents. 8 findings total (2 Important, 1 High, 3 Medium, 2 Low). User clicked "A" → all 8 applied atomically → compile + parser run + idempotency verified.

## Dead Code Hygiene

After any refactoring or implementation change, check for orphaned code:

1. Identify code that is now unreachable or unused
2. List it explicitly
3. **Ask before deleting:** "Should I remove these now-unused elements: [list]?"

Don't leave dead code lying around — it confuses future readers and agents. But don't silently delete things you're not sure about. When in doubt, ask.

```
DEAD CODE IDENTIFIED:
- formatLegacyDate() in src/utils/date.ts — replaced by formatDate()
- OldTaskCard component in src/components/ — replaced by TaskCard
- LEGACY_API_URL constant in src/config.ts — no remaining references
→ Safe to remove these?
```

## Review Speed

Slow reviews block entire teams. The cost of context-switching to review is less than the waiting cost imposed on others.

- **Respond within one business day** — this is the maximum, not the target
- **Ideal cadence:** Respond shortly after a review request arrives, unless deep in focused coding. A typical change should complete multiple review rounds in a single day
- **Prioritize fast individual responses** over quick final approval. Quick feedback reduces frustration even if multiple rounds are needed
- **Large changes:** Ask the author to split them rather than reviewing one massive changeset

## Common Nit Patterns (auto-fix before review)

These appear frequently and should be caught by the author pre-review:

| Nit | Detection | Fix |
|-----|-----------|-----|
| Unused import | `grep -v "^#" file.py \| grep "import" \| grep -v "used"` | Remove |
| Duplicate constant/keyword | Search for same value in dict/list | Deduplicate |
| `list.remove(obj)` on JSON-loaded data | `queue["pending"].remove(entry)` after multi-load | Filter by ID: `[e for e in lst if e["id"] != target_id]` |
| Dead `pass` in if/else | `if x: pass` or `else: pass` | Remove block or invert condition |
| Import inside function (stdlib) | `def foo(): import sys` | Move to module top |
| Redundant alias | `WORKSPACE_ROOT = VAULT_ROOT` | Use original |
| Unused function parameter | `def f(x, y): return x` | Remove or prefix `_` |

In this session, 5 nits were found and fixed pre-commit:
1. `from typing import Iterable` — unused
2. Duplicate `followup_date` keyword in FIELD_KEYWORDS
3. `if not show_all: pass` / `else: pass` blocks in list_cases
4. `NO_CALENDAR_FLAG`, `WORKSPACE_ROOT` unused constants
| `import sys` inside `run_nl_handler` instead of module top | Move to module top |

### HTML/CSS Nits

| Nit | Detection | Fix |
|-----|-----------|-----|
| Inline style `color=#xxx` (uses `=` instead of `:`) | `grep 'color=#'` in HTML files | Change `color=#` → `color:#` |
| Unclosed `<span>` or `<div>` tags in HTML templates | Check paired tags in generated output | Always close tags in template strings |

**Rule:** Run `grep -n "pass$" scripts/*.py` and `grep -n "import .* unused"` as pre-commit checks.

## Handling Disagreements

When resolving review disputes, apply this hierarchy:

1. **Technical facts and data** override opinions and preferences
2. **Style guides** are the absolute authority on style matters
3. **Software design** must be evaluated on engineering principles, not personal preference
4. **Codebase consistency** is acceptable if it doesn't degrade overall health

**Don't accept "I'll clean it up later."** Experience shows deferred cleanup rarely happens. Require cleanup before submission unless it's a genuine emergency. If surrounding issues can't be addressed in this change, require filing a bug with self-assignment.

## Honesty in Review

When reviewing code — whether written by you, another agent, or a human:

- **Don't rubber-stamp.** "LGTM" without evidence of review helps no one.
- **Don't soften real issues.** "This might be a minor concern" when it's a bug that will hit production is dishonest.
- **Quantify problems when possible.** "This N+1 query will add ~50ms per item in the list" is better than "this could be slow."
- **Push back on approaches with clear problems.** Sycophancy is a failure mode in reviews. If the implementation has issues, say so directly and propose alternatives.
- **Accept override gracefully.** If the author has full context and disagrees, defer to their judgment. Comment on code, not people — reframe personal critiques to focus on the code itself.

## Verify Reviewer Findings on Disk (Subagent Review Pitfall)

When a **review/simplify subagent** reports a finding about the existing codebase (e.g. "file X is deprecated/dead", "module Y is unused", "config Z is obsolete"), the receiving agent MUST **verify the claim on disk before acting on it** — do NOT blindly follow.

**Why:** Subagents operate with isolated context and can over-interpret, hallucinate, or misread. In the 2026-07-07 Manpower session, a code-review subagent claimed `Labour_Cost_Hub.md` was "decommissioned (deprecated)" and recommended redirecting all refs. The file on disk was STILL `status: active` with live `## 2. Operating Policies`. Blindly following would have broken the policy link that `Manpower_Master.md` depends on. The main agent caught it by `read_file` before acting → kept the Hub, fixed only the real dead ref (index.md headcount note).

**Rule:**
- Any review finding that asserts a file/section/module is *dead / deprecated / unused / should be removed* → `read_file` or `grep` the target BEFORE applying the recommendation.
- If the finding is correct → apply. If the finding is wrong (file alive, still referenced) → push back with evidence, keep the artifact.
- This applies to `delegate_task` review batches AND any "here's what's wrong with your code" report. Subagent output is a *suggestion*, not ground truth.
- Symptom of over-reach: recommendation to delete/redirect something that other live files still reference. Cross-check references first.

**Verification pattern:**\n```bash\n# Before acting on "X is dead" → confirm\ngrep -rn 'Labour_Cost_Hub' vault/30_KNOWLEDGE_BASE/wiki/ | head\nread_file vault/30_KNOWLEDGE_BASE/wiki/04_labour_costs/Labour_Cost_Hub.md  # check status: + referenced sections\n```\n\n### Extended: Review-finding false positives (this session 2026-07-10)\n\nSubagent review claims are *suggestions*, not ground truth. Two false-positive classes burned time:\n\n- **Keyword/typo claims:** A subagent flagged `"unemployeement"` (missing c) and `"related to col"` as bucketing bugs. Grepping the *actual source CSV* showed the data itself spells `"Unemployeement insurance"` and `"Other related to COL"` — the "typo" keyword was CORRECT and matching. **Before "fixing" a keyword the subagent calls a typo, grep the real source data for BOTH the keyword and the "correct" spelling. If the data uses the misspelling, keep the misspelling.**\n- **Critical-logic claims:** A subagent claimed "all stores show System's Net_Profit." Reproduce the bug with a throwaway generator run and grep the output BEFORE applying the fix (confirmed LU3 was +65.3 = System's, then fix changed it to -95.5). Apply fix, re-run, confirm the corrected value. Don't trust the claim or the fix until output is observed both ways.\n\n### Pitfall: Markdown SSOT Section Splice Duplication (HIGH-risk)\n\nWhen a generator rewrites a named `## ` section inside a human-readable SSOT markdown (P&L breakdown, wiki), the splice is the #1 source of silent corruption. Observed this session:\n\n- **Duplicate sections:** `head = lines[:ti]` (ti = target `## ` index) then `tail = lines[ni:]` where `ni` = next `## ` — but if the next `## ` is *earlier in the file* than the target (wrong section order), `tail` re-includes the target block → two copies after `head + new + tail`.\n- **Lost sections:** cutting `head[:ti] + new + tail[anchor:]` where `anchor` is a DIFFERENT section than the one after the target drops intervening sections (COST STRUCTURE, TARGET) entirely.\n- **Fix-by-reset trap:** when already corrupted, `git checkout -- file` then re-applying all generators in order is cleaner than surgical edits — but it discards uncommitted derived sections, so re-run every generator afterward.\n\n**Correct idempotent splice — assert count == 1 after:**\n```python\nti = [i for i,l in enumerate(lines) if l.startswith(TARGET_HEADER)][0]\nni = [i for i,l in enumerate(lines) if l.startswith(\"## \") and i > ti][0]  # STRICTLY after target\nhead = lines[:ti]\ntail = lines[ni:]   # starts at section AFTER target — never re-includes target\nout  = \"\\n\".join(head) + \"\\n\" + new_section + \"\\n\\n\" + \"\\n\".join(tail)\nassert out.count(TARGET_HEADER) == 1\n```\nKey: `ni` MUST be searched with `i > ti` (strictly after), never a global next-`##` that could be earlier. After writing, assert exactly one copy of every `## ` header that should be unique. Full recipe + `node --check` JS-verify snippet: see `references/markdown-splice-recipe.md`.\n\n## Dependency Discipline

Part of code review is dependency review:

**Before adding any dependency:**
1. Does the existing stack solve this? (Often it does.)
2. How large is the dependency? (Check bundle impact.)
3. Is it actively maintained? (Check last commit, open issues.)
4. Does it have known vulnerabilities? (`npm audit`)
5. What's the license? (Must be compatible with the project.)

**Rule:** Prefer standard library and existing utilities over new dependencies. Every dependency is a liability.

## The Review Checklist

```markdown
## Review: [PR/Change title]

### Context
- [ ] I understand what this change does and why

### Correctness
- [ ] Change matches spec/task requirements
- [ ] Edge cases handled
- [ ] Error paths handled
- [ ] Tests cover the change adequately

### Readability
- [ ] Names are clear and consistent
- [ ] Logic is straightforward
- [ ] No unnecessary complexity

### Architecture
- [ ] Follows existing patterns
- [ ] No unnecessary coupling or dependencies
- [ ] Appropriate abstraction level

### Security
- [ ] No secrets in code
- [ ] Input validated at boundaries
- [ ] No injection vulnerabilities
- [ ] Auth checks in place
- [ ] External data sources treated as untrusted

### Performance
- [ ] No N+1 patterns
- [ ] No unbounded operations
- [ ] Pagination on list endpoints

### Verification
- [ ] Tests pass
- [ ] Build succeeds
- [ ] Manual verification done (if applicable)

### Verdict
- [ ] **Approve** — Ready to merge
- [ ] **Request changes** — Issues must be addressed
```
## Practical Nits Checklist (Applied in L'Usine Session)

| Category | Nits to Hunt |
|----------|-------------|
| Unused imports | `Iterable`, `find_case_files`, `extract_update_text`, `split_frontmatter_and_body`, `SECTION_KEYWORDS`, `FIELD_KEYWORDS`, `tokenize` |
| Dead constants | `NO_CALENDAR_FLAG`, `WORKSPACE_ROOT` (alias), `now_time_str()` |
| Redundant logic | `if resolution: pass`, `if not show_all: pass` blocks |
| Duplicate keywords | `follow_up` / `followup_date` in FIELD_KEYWORDS |
| Inline imports | Move `import yaml` / `import sys` to module top |
| Unused functions | `extract_update_text` (no-op), `now_time_str` (never called) |

**Process:** Run `grep -r "import.*unused"`, `grep -r "pass$"` in changed files before marking review complete.
## See Also

- For detailed security review guidance, see `references/security-checklist.md`
- For performance review checks, see `references/performance-checklist.md`
- For detecting doc/code drift in script-backed skills (dead refs, unsupported CLI flags), see `references/skill-doc-code-drift.md`

## Common Rationalizations

| Rationalization | Reality |
|---|---|
| "It works, that's good enough" | Working code that's unreadable, insecure, or architecturally wrong creates debt that compounds. |
| "I wrote it, so I know it's correct" | Authors are blind to their own assumptions. Every change benefits from another set of eyes. |
| "We'll clean it up later" | Later never comes. The review is the quality gate — use it. Require cleanup before merge, not after. |
| "AI-generated code is probably fine" | AI code needs more scrutiny, not less. It's confident and plausible, even when wrong. |
| "The tests pass, so it's good" | Tests are necessary but not sufficient. They don't catch architecture problems, security issues, or readability concerns. |

## Red Flags

- PRs merged without any review
- Review that only checks if tests pass (ignoring other axes)
- "LGTM" without evidence of actual review
- Security-sensitive changes without security-focused review
- Large PRs that are "too big to review properly" (split them)
- No regression tests with bug fix PRs
- Review comments without severity labels — makes it unclear what's required vs optional
- Accepting "I'll fix it later" — it never happens

## Reference Integrity Gate (Hard Rule — kills dead refs)

A skill that cites a file that does not exist is itself a bug — and this skill explicitly teaches that stale references are defects. Before marking ANY review complete (code OR prompt/skill/markdown), run this gate:

```
For every `see references/X.md` / `see also references/X.md` / `references/X.md` citation in the artifact under review:
  1. Resolve the path relative to the artifact's own skill dir
  2. If file does NOT exist → this is a CRITICAL finding (blocks merge)
  3. Either (a) create the referenced file, or (b) delete the citation
  4. Do NOT leave a dangling reference
```

**Why this exists:** Session 2026-07-13 found `code-review-and-quality` citing `references/security-checklist.md` + `references/performance-checklist.md` that did not exist — a self-inflicted stale reference. The gate below prevents recurrence.

**Vault-wide sweep (run after any skill edit, or weekly):** Scan every `*/SKILL.md` under the profile skills dir for `references/<file>.md` citations; cross-check each against (a) the owning skill's `references/` dir AND (b) any other skill's `references/` dir (cross-skill refs are valid). Report only TRUE dead refs (missing in both). A dead ref that points to a DIFFERENT skill's references dir is NOT dead — fix the path, don't delete the citation.

**Ready-made runner:** `vault/scripts/ref_integrity_sweep.py` (measure-only, stdlib-only, writes a state file to detect NEW dead refs across runs). Run `python3 vault/scripts/ref_integrity_sweep.py` — it prints a Telegram-ready Markdown report and changes NO skill files. It builds a whitelist of all existing `references/*.md` across every skill (cross-skill refs count as valid), then reports only TRUE dead cites. Exit code is always 0 (report-only). Wire it to a manual Monday calendar check if desired — do NOT auto-fix from its output.

## Verification

After review is complete:

- [ ] All Critical issues are resolved
- [ ] All Important issues are resolved or explicitly deferred with justification
- [ ] Tests pass
- [ ] Build succeeds
- [ ] The verification story is documented (what changed, how it was verified)
