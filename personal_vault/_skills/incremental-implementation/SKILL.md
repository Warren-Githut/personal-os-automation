---
name: incremental-implementation
description: Delivers changes incrementally. Use when implementing any feature or change that touches more than one file. Use when you're about to write a large amount of code at once, or when a task feels too big to land in one step.
---

# Incremental Implementation

## Overview

Build in thin vertical slices — implement one piece, test it, verify it, then expand. Avoid implementing an entire feature in one pass. Each increment should leave the system in a working, testable state. This is the execution discipline that makes large features manageable.

## When to Use

- Implementing any multi-file change
- Building a new feature from a task breakdown
- Refactoring existing code
- Any time you're tempted to write more than ~100 lines before testing

**When NOT to use:** Single-file, single-function changes where the scope is already minimal.

## The Increment Cycle

```
┌──────────────────────────────────────┐
│                                      │
│   Implement ──→ Test ──→ Verify ──┐  │
│       ▲                           │  │
│       └───── Commit ◄─────────────┘  │
│              │                       │
│              ▼                       │
│          Next slice                  │
│                                      │
└──────────────────────────────────────┘
```

For each slice:

1. **Implement** the smallest complete piece of functionality
2. **Test** — run the test suite (or write a test if none exists)
3. **Verify** — confirm the slice works as expected (tests pass, build succeeds, manual check)
4. **Commit** -- save your progress with a descriptive message (see `git-workflow-and-versioning` for atomic commit guidance)
5. **Move to the next slice** — carry forward, don't restart

## Slicing Strategies

### Vertical Slices (Preferred)

Build one complete path through the stack:

```
Slice 1: Create a task (DB + API + basic UI)
    → Tests pass, user can create a task via the UI

Slice 2: List tasks (query + API + UI)
    → Tests pass, user can see their tasks

Slice 3: Edit a task (update + API + UI)
    → Tests pass, user can modify tasks

Slice 4: Delete a task (delete + API + UI + confirmation)
    → Tests pass, full CRUD complete
```

Each slice delivers working end-to-end functionality.

### Contract-First Slicing

When backend and frontend need to develop in parallel:

```
Slice 0: Define the API contract (types, interfaces, OpenAPI spec)
Slice 1a: Implement backend against the contract + API tests
Slice 1b: Implement frontend against mock data matching the contract
Slice 2: Integrate and test end-to-end
```

### Infrastructure Verification Slicing (Pre-Slice 0)

Before writing any implementation code, verify that critical infrastructure and dependencies are actually working:

```
Slice 0: Verify infrastructure (API endpoint responds, credentials work, proxy is alive)
Slice 1: Build core logic on confirmed infrastructure
Slice 2: Add features on top of proven foundation
```

**Concrete failure from this session:** A plan task said "Test proxy support" as Task 4.2 (last). When executed first, the proxy was dead — had to switch from CLI spawn to direct API calls. Infrastructure assumptions that are wrong cost the entire design.

**Rule:** If your plan has a task like "verify X works" or "test connectivity to Y", move it to Phase 1. If it's not in the plan, add it. Do not build code that depends on unverified infrastructure.

### Risk-First Slicing
### Wide-Refactor Slicing — Expand-Contract (steal từ mattpocock/to-tickets)
Khi 1 thay đổi là **wide refactor** — 1 mechanical change (rename SSOT, retype shared symbol) có **blast radius** lan toàn codebase, làm nổ hàng ngàn call-site cùng lúc → KHÔNG ép vào tracer-bullet. Thay vào đó sequence theo **expand–contract**:
```
1. EXPAND: thêm form MỚI song song form cũ (nothing breaks)
2. MIGRATE: dời call-sites sang form MỚI theo batch (theo blast radius:
            per-package / per-directory), mỗi batch = 1 task blocked by EXPAND,
            giữ CI green batch-to-batch vì form cũ vẫn tồn tại
3. CONTRACT: xóa form cũ SAU khi không còn caller, trong 1 task blocked by mọi migrate-batch
```
Nếu ngay cả các batch cũng không tự green → giữ sequence nhưng share 1 **integration branch** mà tất cả block 1 task `integrate-and-verify` cuối (green chỉ hứa ở đó).

### Frontier / Blocking-Edge mental model (steal từ mattpocock/to-tickets)
Mỗi task có **blocking edges** = những task khác phải xong trước nó mới start. Task không có blocker → start ngay.
→ Luôn làm việc trên **frontier**: tập hợp các task có blocker đều đã done. Với chain tuyến tính = top-to-bottom. Vẽ dependency graph trước khi implement để không block nhầm.

### Risk-First Slicing
Tackle the riskiest or most uncertain piece first:

```typescript
Slice 1: Prove the WebSocket connection works (highest risk)
Slice 2: Build real-time task updates on the proven connection
Slice 3: Add offline support and reconnection
```

If Slice 1 fails, you discover it before investing in Slices 2 and 3.

## Implementation Rules

### Rule 0: Simplicity First

Before writing any code, ask: "What is the simplest thing that could work?"

After writing code, review it against these checks:
- Can this be done in fewer lines?
- Are these abstractions earning their complexity?
- Would a staff engineer look at this and say "why didn't you just..."?
- Am I building for hypothetical future requirements, or the current task?

```
SIMPLICITY CHECK:
✗ Generic EventBus with middleware pipeline for one notification
✓ Simple function call

✗ Abstract factory pattern for two similar components
✓ Two straightforward components with shared utilities

✗ Config-driven form builder for three forms
✓ Three form components
```

Three similar lines of code is better than a premature abstraction. Implement the naive, obviously-correct version first. Optimize only after correctness is proven with tests.

### Rule 0.5: Scope Discipline

Touch only what the task requires.

Do NOT:
- "Clean up" code adjacent to your change
- Refactor imports in files you're not modifying
- Remove comments you don't fully understand
- Add features not in the spec because they "seem useful"
- Modernize syntax in files you're only reading

If you notice something worth improving outside your task scope, note it — don't fix it:

```
NOTICED BUT NOT TOUCHING:
- src/utils/format.ts has an unused import (unrelated to this task)
- The auth middleware could use better error messages (separate task)
│   want me to create tasks for these?\n```\n\n### Reference: hourly-cover-v5-format-pattern\n`references/hourly-cover-v5-format-pattern.md` documents the L'Usine weekly log hybrid format (60% machine JSON + 40% human Decision Board) used for `09_Hourly_Cover_Revenue_Log.md`. Reuse this pattern when redesigning other operational logs — it cuts parse tokens by ~55% while improving decision-making speed.
```

### Rule 1: One Thing at a Time

Each increment changes one logical thing. Don't mix concerns:

**Bad:** One commit that adds a new component, refactors an existing one, and updates the build config.

**Good:** Three separate commits — one for each change.

### Rule 2: Keep It Compilable

After each increment, the project must build and existing tests must pass. Don't leave the codebase in a broken state between slices.

### Rule 3: Feature Flags for Incomplete Features

If a feature isn't ready for users but you need to merge increments:

```typescript
// Feature flag for work-in-progress
const ENABLE_TASK_SHARING = process.env.FEATURE_TASK_SHARING === 'true';

if (ENABLE_TASK_SHARING) {
  // New sharing UI
}
```

This lets you merge small increments to the main branch without exposing incomplete work.

### Rule 4: Safe Defaults

New code should default to safe, conservative behavior:

```typescript
// Safe: disabled by default, opt-in
export function createTask(data: TaskInput, options?: { notify?: boolean }) {
  const shouldNotify = options?.notify ?? false;
  // ...
}
```

### Rule 5: Rollback-Friendly

Each increment should be independently revertable:

- Additive changes (new files, new functions) are easy to revert
- Modifications to existing code should be minimal and focused
- Database migrations should have corresponding rollback migrations
- Avoid deleting something in one commit and replacing it in the same commit — separate them

## Working with Agents

When directing an agent to implement incrementally:

```
"Let's implement Task 3 from the plan.

Start with just the database schema change and the API endpoint.
Don't touch the UI yet — we'll do that in the next increment.

After implementing, run `npm test` and `npm run build` to verify
nothing is broken."
```

Be explicit about what's in scope and what's NOT in scope for each increment.

## Increment Checklist

After each increment, verify:

- [ ] The change does one thing and does it completely
- [ ] All existing tests still pass (`npm test`)
- [ ] The build succeeds (`npm run build`)
- [ ] Type checking passes (`npx tsc --noEmit`)
- [ ] Linting passes (`npm run lint`)
- [ ] The new functionality works as expected
- [ ] The change is committed with a descriptive message

**Note:** Run each verification command after a change that could affect it. After a successful run, don't repeat the same command unless the code has changed since — re-running on unchanged code adds no information.

## Common Rationalizations

| Rationalization | Reality |
|---|---|
| "I'll test it all at the end" | Bugs compound. A bug in Slice 1 makes Slices 2-5 wrong. Test each slice. |
| "It's faster to do it all at once" | It *feels* faster until something breaks and you can't find which of 500 changed lines caused it. |
| "These changes are too small to commit separately" | Small commits are free. Large commits hide bugs and make rollbacks painful. |
| "I'll add the feature flag later" | If the feature isn't complete, it shouldn't be user-visible. Add the flag now. |
| "This refactor is small enough to include" | Refactors mixed with features make both harder to review and debug. Separate them. |
| "Let me run the build command again just to be sure" | After a successful run, repeating the same command adds nothing unless the code has changed since. Run it again after subsequent edits, not as reassurance. |

## Red Flags

- More than 100 lines of code written without running tests
- Multiple unrelated changes in a single increment
- "Let me just quickly add this too" scope expansion
- Skipping the test/verify step to move faster
- Build or tests broken between increments
- Large uncommitted changes accumulating
- Building abstractions before the third use case demands it
- Touching files outside the task scope "while I'm here"
- Creating new utility files for one-time operations
- Running the same build/test command twice in a row without any intervening code change
- **Assuming infrastructure in config.yaml works without verifying.** A dead proxy, wrong base_url, or expired credential in config.yaml will silently break everything that depends on it. Test the actual endpoint before writing code that assumes it works.

### Warren Workflow (Ops Vault)

When executing ops tasks for Warren (non-IT, vault-based):

1. **Present plan first** — 3-4 options with tradeoffs + recommendation
2. **Get explicit go-ahead** ("ok", "approved")
3. **Execute ONE step at a time** — no batching, no parallel execution
4. **Test immediately after each step** — show Warren what changed
5. **Fix bugs found during testing BEFORE the next step** — Warren will say "gắt gao lên" if you skip this
6. **Apply FULL §1-9 Pre-Edit Checklist before every vault write.** Do not shorten — Warren specifically said "cẩn thận ko bao giờ thừa". Must declare `ĐÃ ĐỌC CHECKLIST §1-9 ✅` before writing.
7. **§9 Language gate (HARD RULE):** ALL human-facing text in vault files = Tiếng Việt có dấu. Self-scan before showing.
8. **Per-slice quality sub-steps (HARD RULE):** Every task slice MUST include these 3 sub-steps before advancing to the next slice — run them in parallel when possible via `delegate_task`:
   - **Verification:** temp `hermes-verify-*.py` script (≥5 checks) for Python code; format check + data cross-check for markdown files
   - **Code review (5-axis):** correctness, readability, architecture, security, performance
   - **Code simplification:** deduplicate, simplify logic, remove dead code
   
   Warren calls this pattern "vừa làm vừa verify + code-review + code-simplification song song cho mỗi task". Do NOT batch these at the end of all tasks — apply them per-slice.
9. **Sequence per task slice:** Implement → Verify → Code Review + Simplify (parallel) → Next slice. Commit is per-logical-chunk (rule 11) but review+simplify run per-slice.
10. **Commit after every completed phase** — not just "logical chunks." Commit at every PHASE boundary (Phase 1 Foundation, Phase 2 Core, etc.). A phase = a task group that passes a checkpoint. This is the minimum safe cadence for git-backed vault files: a single corrupt Python script can destroy ALL uncommitted work (concrete failure 2026-07-06: a compression script reduced `09_Hourly_Cover_Revenue_Log.md` from 1,079 to 2 lines; `git checkout -- <file>` restored the committed state, wiping all uncommitted changes from 3 prior phases). Phase-by-phase commits limit any loss to one phase.
11. **Verify with `git status` before presenting**

**🚫 Show evidence, not claims.** Terminal output + file diff + path + Vietnamese commentary.

**L'Usine vault ops pipeline — sequence discipline (Warren correction 2026-07-11).** When the task touches a vault SSOT (rename, new ingest script, dashboard), the user explicitly requires: **audit all source files and existing references BEFORE writing any code.** Concrete order observed and approved:
1. Search the whole vault for every reference to the file/entity being changed (grep `search_files` for the path/name).
2. List existing cron jobs + scripts that read the source, to confirm reuse vs new code.
3. Present a source-audit report to the user and get "approved" BEFORE implementing.
4. Only then: implement slice → verify → review → simplify → commit.

**L'Usine-specific pitfalls (from 2026-07-11 SSOT rename + ingest-script build):**

- **Double-nested `vault/vault` path.** A script in `vault/scripts/` computing `Path(__file__).parent.parent / "vault" / "30_..."` resolves to `vault/vault/...` (parent already IS `vault`). Fix: `VAULT_ROOT = Path(__file__).parent.parent` (== `vault/`), then `VAULT_ROOT / "10_OPERATION_DATA" / "parsers"` (no extra `"vault"` segment). Detect by running once — it reports "file không tồn tại: .../vault/vault/...".
- **`sys.stdout = io.TextIOWrapper(sys.stdout.buffer, ...)` closes stdout.** Reassigning stdout without keeping a reference causes `ValueError: I/O operation on closed file` later. Fix: drop the wrap (terminal is already UTF-8) or use `sys.stdout.reconfigure(encoding="utf-8")`.
- **Rename-then-refs ordering.** `git mv` the file FIRST, then update all references (`00_OPERATION_INDEX.md`, `WIKI_GRAPH.json` edges, `FRONTMATTER_CACHE.json`) in the SAME slice. After updating, `search_files` for the OLD path must return 0. JSON graph files need bulk `str.replace` (safe — they are generated caches, not vault markdown); verify with `json.load` + `count(old)==0`.
- **SSOT `aa_` prefix convention.** Warren uses `aa_` prefix on SSOT files to sort them to the top of the folder and mark them as authority. When renaming an SSOT, keep the `aa_` prefix.
- **Idempotent markdown upsert (append-or-update block).** When writing a monthly block into an SSOT, anchor with `re.search(rf"^## {re.escape(header)}\s*$", content, re.MULTILINE)` (line-start, header-only — NOT substring, which falsely matches template docs). To replace: find `ti` (target index), `ni` = next `## ` with `i > ti` (strictly after), `head=lines[:ti]`, `tail=lines[ni:]`, write `head + new + tail`, assert exactly 1 copy of the header after.
- **Reuse existing parser aggregates.** `col_weekly_parser.build_monthly_summary(year, month, cols, rows)` already aggregates GSheet `COL_Weekly` by month. Wrap it (call `fetch_sheet()` → pass cols/rows) instead of re-implementing fetch. Stub it in tests with `sys.modules["col_weekly_parser"] = ...` to verify pure functions without a live GSheet call.

**Visual output verification (HTML dashboards).** When the deliverable includes an HTML file that the user opens in a browser, code-inspection verification is INSUFFICIENT — JS syntax errors, data-injection issues, and Chart.js CDN failures only surface at runtime. After generating the file:
1. Open it in browser manually (`start chrome "path/to/file.html"` on Windows)
2. Visually confirm: KPI cards show numbers, charts render, interactive elements respond to clicks
3. Check browser DevTools Console (F12) for JS errors if page is blank
4. Only after visual confirmation, mark the task as verified

**E2E verification as final gate** — After ALL steps complete, run comprehensive verification proving all changes correct together. Before/after summary table. Clean up temp scripts. Then present.

**Pitfall: stale list indices after reconstruction.** When modifying a list in-place and then inserting new elements, indices computed BEFORE the modification are invalid AFTER it. Recalculate after any list insert/append/replace.

Concrete failure (2026-07-05): `auto_update_case_file()` computed `fm_end` (index of frontmatter closing `---`) from the original file. After adding 2 frontmatter lines, the closing `---` shifted by 2 positions, but the banner insertion used the STALE `fm_end + 1`. Result: banner injected INSIDE frontmatter.

```python
# WRONG: stale index from original list
insert_pos = fm_end + 1  # BUG!

# CORRECT: recalculate after modification
close_idx = len(fm_lines) + 1
insert_pos = close_idx + 1
```

**Pitfall: after fixing data-writing bugs, re-test against a clean copy, not the corrupted intermediate state.** When a bug corrupts a file (e.g. wrong YTD, duplicate rows), applying fixes to the buggy file and re-testing can produce false passes because the fix only partially corrects the corruption. **Fix:** `git checkout -- <corrupted_file>` to restore the original known-good state, then re-run the fixed script. Verify the output against the original file, not the corrupted one. This applies doubly to `--force` operations that overwrite multiple sections — re-testing against the clean original proves the fix works correctly end-to-end. |
When iterating rows from `openpyxl` (0-indexed list), spreadsheet row numbers (1-indexed) don't match Python list indices. Always print rows 0-15 before coding hardcoded ranges. A one-off error silently produces wrong totals (session 2026-07-02: range(4,10) instead of range(3,9) produced 554.25 instead of 750.75).

**Pitfall: patch boundary ambiguity with `---` in markdown files.** When using `patch` to replace a large block in a markdown file where the boundary marker is `---`, the fuzzy matcher may match the WRONG `---` (e.g. YAML frontmatter close instead of the intended section separator). **Fix:** Use a Python script with explicit line ranges instead of fuzzy patch. Or include unique surrounding context lines (5+ on each side) to disambiguate. Always `git diff` or backup-first before large markdown patches.

**Pitfall: bulk Python file mutation on vault markdown files can silently corrupt the entire file.** Writing a Python script that reads a markdown file, processes it, and writes it back is DANGEROUS for vault files — a regex logic error can truncate the file to 2 lines (concrete failure 2026-07-06: a compression script with faulty boundary detection reduced `09_Hourly_Cover_Revenue_Log.md` from 1,079 to 2 lines). **Fix:** Never use bulk Python file-mutation scripts on vault markdown files. Instead, use `patch` tool per-section with unique surrounding context (5+ lines each side). If you MUST use Python, (a) write_only, never read-modify-write; (b) always `git checkout -- <file>` to restore a clean copy before retrying; (c) verify with `wc -l` immediately after write. The `git checkout` to restore from the committed state is the fastest recovery path: no need for stashes or reflog.

**Pitfall: idempotency check for month/section headers must use regex, not substring.** `if f"## {month}" in content` will match template documentation (e.g. `"## YYYY-MM (vd: ## 2026-06)"` inside a template block), causing false "already exists" skips. **Fix:** use `re.search(rf"^## {re.escape(month)}\s*$", content, re.MULTILINE)` — anchor to line start and require only the header on that line.

**Pitfall: verifying a parser/writer with the system's own lint only (no real run).** `write_file` lint status "ok" only means syntax — it does NOT prove the script runs, parses input, or writes correct output. **Fix (ad-hoc verification — NOT suite green):** when a changed Python file has no test suite, write a temporary verification script under `%TEMP%` with a `hermes-verify-` filename prefix that (a) builds a minimal fixture (e.g. a small openpyxl workbook for a payroll parser), (b) runs the target script against a COPY of the real output file, (c) asserts ≥5 concrete checks (entry count, idempotency on 2nd run, preserved sections, JSON present, newest-on-top), (d) cleans up the temp dir. Run it; if EXIT=0, report as ad-hoc verification. Concrete session 2026-07-07: `update_manpower_master.py` passed lint but had a column-mapping bug in the test fixture and a broken default path (`SCRIPT_DIR.parent/"vault"/...` double-nested) — only caught by a real run, not lint. After fixing, the temp verify script confirmed: apply#1 writes, apply#2 skips (idempotency), Block 1 intact, Δ line correct.

**Fixture column-mapping trap (openpyxl parsers).** When generating a test Excel for a parser that reads by absolute column number (e.g. `parse_payroll.py` reads col 3=code, col 57=cost), a positional list `[1,"T01",...]` shifts every field by one because list index ≠ column number. **Fix:** build the fixture row as a dict `{field: col_number}` and write each cell by its true 1-indexed column (`ws.cell(row=r, column=colmap[key], value=val)`). Verify by printing `ws.cell(row, col).value` for header + first data row before trusting the fixture.

**Pitfall: default path double-nesting.** A script in `vault/scripts/` computing `SCRIPT_DIR.parent / "vault" / "30_..."` resolves to `vault/vault/...` (parent already IS `vault`). **Fix:** `SCRIPT_DIR.parent / "30_KNOWLEDGE_BASE" / ...` (no extra `"vault"` segment). Detect by running the script once — it will report "Master không tồn tại: .../vault/vault/...".

**Pitfall: dry-run flag mismatch.** If the script defaults to dry-run (no flag), do NOT invent a `--dry-run` flag the argparse doesn't define — it raises "unrecognized arguments". Run with no extra flag for dry-run, `--apply` for write.

**Pitfall: f-string + JS template literal `${}` conflict.** When generating HTML with embedded JavaScript inside a Python f-string, JS template literals (`${var}`) and ternary operators (`a ? b : c`) cause `SyntaxError` because `:` inside `{...}` is interpreted as an f-string format specifier. **Fix: use `.replace()` on a static HTML template string instead of f-strings.** Define the HTML as a module-level constant with `{PLACEHOLDER}` markers, then call `.replace("{PLACEHOLDER}", value)` at generation time. Avoids all escaping complexity.

```python
# WRONG: SyntaxError at JS ternary
def gen_html():
    return f'''<script>
    var x = {isWO ? "r" : "g"};  # ❌ f-string parses ':' as format spec
    </script>'''

# CORRECT: use .replace()
_HTML = '''<script>
var x = {MARKER};
</script>'''
def gen_html():
    return _HTML.replace("{MARKER}", '"r"' if isWO else '"g"')
```

**Pitfall: Chart.js scope bug — function can't see caller's local variable.** When generating Chart.js HTML from Python, a helper function defined at module level (`function getDataset(key, label, color)`) cannot access a local variable (`weeks`) defined inside the calling function (`renderAll()`). The function only has access to its own scope and global scope — not `renderAll()`'s local variables. **Fix:** Pass required data as parameters: `function getDataset(weeks, key, label, color)`. Or define the helper inside the calling function for closure access. **Detection:** Dashboard renders blank with no JS console error — `weeks.map(...)` throws ReferenceError, all charts fail silently. Double-check JS variable scoping when extracting helper functions.

**Pitfall: Chart.js `Chart.instances` is not a real API.** Using `Chart.instances.forEach(c => c.destroy())` to clean up charts before re-render silently fails — charts accumulate and overlap. `Chart.instances` does not exist in the standard Chart.js API. **Fix:** Manage instances manually: `let charts = []; function makeChart(id, config) { const c = new Chart(ctx, config); charts.push(c); } function destroyAll() { charts.forEach(c => { try { c.destroy(); } catch(e) {} }); charts = []; }`. Call `destroyAll()` before each re-render cycle.

**Pitfall: verify data sign conventions before displaying in tables.** When aggregating numeric data (WO, shortage, surplus), always verify which values should be positive and which negative. Common mistakes include (a) mixing shortage (negative) and surplus (positive) in the same category table, and (b) displaying shortage as a positive absolute value when it should be negative to indicate loss. **Fix: trace the sign through the entire pipeline — raw data → parse → aggregate → display.** For each metric, ask: "Is this a gain or a loss? Should it show with a minus sign?" Print raw per-category sums before building display templates. If two metrics have opposite sign conventions, they MUST be in separate display groups (e.g. "Shortage by Category" and "Surplus by Category" as separate tables).

**Pitfall: Obsidian Markdown table renders as raw `| |` instead of a table.** Two distinct causes, both hit in the 2026-07-11 session and cost real time:
1. **Emoji inside table cells** (e.g. `🔴` `🟡` `🔵` as cell content). Obsidian strict Markdown fails to parse the row → shows literal pipes. **Fix:** never put emoji inside a table cell. Use text tags instead (`(RED)` `(WARN)` `(OK)`), or move the status into a separate non-table line. Emoji in headings/bullets/outside-tables is fine.
2. **Missing blank line between a heading/bold line and the table.** `## Heading` directly followed by `| col |...|` (no blank line) → Obsidian does not recognize it as a table. **Fix:** always insert one blank line between any `##`/`**bold**` line and the opening `|` row. Same for `**Delta vs 2026-05:**` → table.
3. **Stray empty pipe row** (`|` alone on a line) between a heading and the header → breaks the table. **Fix:** delete the stray `|` line; ensure the first table line is the real header.
Verify Obsidian render by reloading the note (Ctrl+R) after edits — paste-only snippets that omit the top table are not the file's fault; always check the actual file on disk, not the chat excerpt.

**Pitfall: multi-source SSOT confusion — audit ALL references BEFORE building an ingest/writer.** When Warren says "sợ nhiêu nguồn, ko biết cái nào là SSOT", do NOT pick a source by guess. **Fix (audit-first workflow):**
1. `search_files` the entity name across the vault (e.g. `Total_Working_Hours_Tracking_Rolling`).
2. Classify each hit: true SSOT (tracking file with `latest_month` metadata) vs mirror/derived (wiki log, JSON cache, index) vs live source (GSheet the SSOT aggregates from).
3. Confirm the SSOT and its live source with Warren BEFORE writing any script. Note: caches like `WIKI_GRAPH.json` / `FRONTMATTER_CACHE.json` must be updated on rename but are NOT the SSOT.
4. Reuse existing aggregation functions (e.g. `col_weekly_parser.build_monthly_summary`) instead of writing new fetch logic — the live-source reader already exists.
Warren trigger phrases: "kiểm tra kỹ nguồn", "cái nào là SSOT", "đừng nhiêu nguồn".

**Pitfall: cross-source derived metrics — time-range mismatch between numerator and denominator.** When computing a percentage from two independent data sources (e.g. channel mix = GrabFood weekly gross / total weekly revenue), a common bug is using different time ranges for each source. Concrete failure (2026-07-06): fetch_store_revenue_month() was called to get total revenue (monthly), while GrabFood gross was already filtered to just the current week. Result: GF 8.3M / Total 932M = 0.9% instead of GF 8.3M / Total 199M (weekly) = 4.2%. The ratio was ~4x too small, which could cause under-investment in a healthy channel if left undetected.

**Fix:** When building a derived metric from two sources:
1. Identify the time range of each source's filter before dividing
2. If they differ, write a new fetch function that accepts the same filter (same week_start/end, same month, same store list) for BOTH sources
3. Verify: run the ratio with hand-calculated expected value for one data point (e.g. LU3: 8.3M / 199M = 4.2%)
4. Consider fetching both the numerator and denominator from the same source call to guarantee alignment (single GSheet query with the same date filter applied to both)

Key triggers: "gửi plan", "vừa làm vừa test", "test từng cái", "implement từng cái", "thể hiện cho tôi thấy", "làm qua loa", "test e2e", "vừa làm vừa battle test".

## Verification

After completing all increments for a task:

- [ ] Each increment was individually tested and committed
- [ ] The full test suite passes
- [ ] The build is clean
- [ ] The feature works end-to-end as specified
- [ ] No uncommitted changes remain
