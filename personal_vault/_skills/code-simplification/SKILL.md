---
name: code-simplification
description: Simplifies code for clarity. Use when refactoring code for clarity without changing behavior. Use when code works but is harder to read, maintain, or extend than it should be. Use when reviewing code that has accumulated unnecessary complexity.
---

# Code Simplification

> Inspired by the [Claude Code Simplifier plugin](https://github.com/anthropics/claude-plugins-official/blob/main/plugins/code-simplifier/agents/code-simplifier.md). Adapted here as a model-agnostic, process-driven skill for any AI coding agent.

## Overview

Simplify code by reducing complexity while preserving exact behavior. The goal is not fewer lines — it's code that is easier to read, understand, modify, and debug. Every simplification must pass a simple test: "Would a new team member understand this faster than the original?"

## When to Use

- After a feature is working and tests pass, but the implementation feels heavier than it needs to be
- During code review when readability or complexity issues are flagged
- When you encounter deeply nested logic, long functions, or unclear names
- When refactoring code written under time pressure
- When consolidating related logic scattered across files

## Relationship to `simplify-code` (the OTHER simplify skill)

Warren-profile has two simplify skills by design — different cost/intent:

| | `code-simplification` (this) | `simplify-code` |
|---|---|---|
| Mode | **Inline single-pass** (model does it directly) | **Parallel 4-agent fan-out** (delegate_task batch) |
| Cost | Low (free-model inline) | High (4 subagents' tokens) |
| When | **Default** cleanup / "dọn code" / per-slice in pipeline | Deep review / "simplify at architecture level" / 4 altitudes |
| L'Usine pitfalls | **Yes** — loop-scope drift, date-field loss, py3.12 escapes, template artifacts, multi-store chart flag (13 reference files) | No |

**Rule:** This is the DEFAULT simplify skill — cheap, behavior-preserving, and
carries the operationally-critical L'Usine parser pitfalls. Use `simplify-code`
only when Warren explicitly wants the deep parallel 4-altitude review.
- After merging changes that introduced duplication or inconsistency

**When NOT to use:**

- Code is already clean and readable — don't simplify for the sake of it
- You don't understand what the code does yet — comprehend before you simplify
- The code is performance-critical and the "simpler" version would be measurably slower
- You're about to rewrite the module entirely — simplifying throwaway code wastes effort

## The Five Principles

### 1. Preserve Behavior Exactly

Don't change what the code does — only how it expresses it. All inputs, outputs, side effects, error behavior, and edge cases must remain identical. If you're not sure a simplification preserves behavior, don't make it.

```
ASK BEFORE EVERY CHANGE:
→ Does this produce the same output for every input?
→ Does this maintain the same error behavior?
→ Does this preserve the same side effects and ordering?
→ Do all existing tests still pass without modification?
```

### 2. Follow Project Conventions

Simplification means making code more consistent with the codebase, not imposing external preferences. Before simplifying:

```
1. Read CLAUDE.md / project conventions
2. Study how neighboring code handles similar patterns
3. Match the project's style for:
   - Import ordering and module system
   - Function declaration style
   - Naming conventions
   - Error handling patterns
   - Type annotation depth
```

Simplification that breaks project consistency is not simplification — it's churn.

### 3. Prefer Clarity Over Cleverness

Explicit code is better than compact code when the compact version requires a mental pause to parse.

```typescript
// UNCLEAR: Dense ternary chain
const label = isNew ? 'New' : isUpdated ? 'Updated' : isArchived ? 'Archived' : 'Active';

// CLEAR: Readable mapping
function getStatusLabel(item: Item): string {
  if (item.isNew) return 'New';
  if (item.isUpdated) return 'Updated';
  if (item.isArchived) return 'Archived';
  return 'Active';
}
```

```typescript
// UNCLEAR: Chained reduces with inline logic
const result = items.reduce((acc, item) => ({
  ...acc,
  [item.id]: { ...acc[item.id], count: (acc[item.id]?.count ?? 0) + 1 }
}), {});

// CLEAR: Named intermediate step
const countById = new Map<string, number>();
for (const item of items) {
  countById.set(item.id, (countById.get(item.id) ?? 0) + 1);
}
```

### 4. Maintain Balance

Simplification has a failure mode: over-simplification. Watch for these traps:

- **Inlining too aggressively** — removing a helper that gave a concept a name makes the call site harder to read
- **Combining unrelated logic** — two simple functions merged into one complex function is not simpler
- **Removing "unnecessary" abstraction** — some abstractions exist for extensibility or testability, not complexity
- **Optimizing for line count** — fewer lines is not the goal; easier comprehension is
- **Scope-indentation drift when moving lines** — when extracting or moving lines between loop levels (`for day` → outside loop), the indentation of the moved lines must match the target scope. A real bug from session 2026-06-22: `d1c += c; d1row.append(...)` for a daily-total accumulator line was accidentally placed OUTSIDE the `for day` loop after simplification, causing the D1 row to show only 3 columns instead of 9. The simplified code compiled and ran without error — but produced wrong output. **Always verify loop-scope indentation after moving lines, and test output correctness, not just compilation.**

### 5. Scope to What Changed

Default to simplifying recently modified code. Avoid drive-by refactors of unrelated code unless explicitly asked to broaden scope. Unscoped simplification creates noise in diffs and risks unintended regressions.

## The Simplification Process

### Step 1: Understand Before Touching (Chesterton's Fence)

Before changing or removing anything, understand why it exists. This is Chesterton's Fence: if you see a fence across a road and don't understand why it's there, don't tear it down. First understand the reason, then decide if the reason still applies.

```
BEFORE SIMPLIFYING, ANSWER:
- What is this code's responsibility?
- What calls it? What does it call?
- What are the edge cases and error paths?
- Are there tests that define the expected behavior?
- Why might it have been written this way? (Performance? Platform constraint? Historical reason?)
- Check git blame: what was the original context for this code?
```

If you can't answer these, you're not ready to simplify. Read more context first.

### Step 2: Identify Simplification Opportunities

Scan for these patterns — each one is a concrete signal, not a vague smell:

**Structural complexity:**

| Pattern | Signal | Simplification |
|---------|--------|----------------|
| Deep nesting (3+ levels) | Hard to follow control flow | Extract conditions into guard clauses or helper functions |
| Long functions (50+ lines) | Multiple responsibilities | Split into focused functions with descriptive names |
| Nested ternaries | Requires mental stack to parse | Replace with if/else chains, switch, or lookup objects |
| Boolean parameter flags | `doThing(true, false, true)` | Replace with options objects or separate functions |
| Repeated conditionals | Same `if` check in multiple places | Extract to a well-named predicate function |

**Naming and readability:**

| Pattern | Signal | Simplification |
|---------|--------|----------------|
| Generic names | `data`, `result`, `temp`, `val`, `item` | Rename to describe the content: `userProfile`, `validationErrors` |
| Abbreviated names | `usr`, `cfg`, `btn`, `evt` | Use full words unless the abbreviation is universal (`id`, `url`, `api`) |
| Misleading names | Function named `get` that also mutates state | Rename to reflect actual behavior |
| Comments explaining "what" | `// increment counter` above `count++` | Delete the comment — the code is clear enough |
| Comments explaining "why" | `// Retry because the API is flaky under load` | Keep these — they carry intent the code can't express |

**Redundancy:**

| Pattern | Signal | Simplification |
|---------|--------|----------------|
| Duplicated logic | Same 5+ lines in multiple places | Extract to a shared function |
| Dead code | Unreachable branches, unused variables, commented-out blocks | Remove (after confirming it's truly dead) |
| Unnecessary abstractions | Wrapper that adds no value | Inline the wrapper, call the underlying function directly |
| Over-engineered patterns | Factory-for-a-factory, strategy-with-one-strategy | Replace with the simple direct approach |
| Redundant type assertions | Casting to a type that's already inferred | Remove the assertion |
| Loop-accumulated code moved outside loop | `d1c += c` after `for day:` instead of inside it | Verify accumulating statements are INSIDE their loop after refactoring |

**Loop-structure pitfall:** When extracting repeated code from inside a loop into a helper function, the loop-accumulated variables (`+=`, `.append()`) can accidentally be placed at the same indentation as the `for` statement instead of inside its body. The result: only the last iteration's values survive, producing truncated output (e.g., D1 row with 3 columns instead of 9).  

**Generic-helper pitfall:** When replacing N near-identical functions with a single shared helper, do NOT lose type-specific field transformations. The most common failure: date fields stored as raw Excel/API values instead of parsed `date` objects. A generic `_read_section()` that stores `ws.cell(r, col).value` directly will produce `datetime` or serial-number values where downstream code expects parsed `date` objects. 

**Fix pattern for generic helpers with varying field types:**
```python
# In the shared helper, transform based on field name conventions:
for field, col in col_map.items():
    val = ws.cell(r, col).value
    if "date" in field or "day" in field:     # ← type-specific transform
        val = parse_excel_date(val)           # must preserve this!
    elif field in ("some_other_special",):    # ← add others as needed
        val = transform(val)
    row[field] = val
```

**Always verify date field behavior after any simplification** that touches sub-table reading, even if the helper compiles and runs without errors. A simplified helper that silently stores raw cell values instead of parsed dates will produce `—` in date columns downstream — easy to miss.

**Prevention:** After any multi-line simplification that touches loop bodies:
1. Check accumulating statements — are they inside or outside the loop?
2. Run the output and verify row/column count before committing
3. When in doubt, move one line at a time and run tests between each

**Historical example (2026-06-22):** `hourly_cover_parser.py` v4.5 — `d1c += c; d1rev += r/1000` was moved outside `for day in DAY_ORDER:` during split-cover helper extraction.

### Step 3: Apply Changes Incrementally

Make one simplification at a time. Run tests after each change. **Submit refactoring changes separately from feature or bug fix changes.** A PR that refactors and adds a feature is two PRs — split them.

```
FOR EACH SIMPLIFICATION:
1. Make the change
2. Run the test suite
3. If tests pass → commit (or continue to next simplification)
4. If tests fail → revert and reconsider
```

Avoid batching multiple simplifications into a single untested change. If something breaks, you need to know which simplification caused it.

**The Rule of 500:** If a refactoring would touch more than 500 lines, invest in automation (codemods, sed scripts, AST transforms) rather than making the changes by hand. Manual edits at that scale are error-prone and exhausting to review.

### Step 4: Verify the Result

After all simplifications, step back and evaluate the whole:

```
COMPARE BEFORE AND AFTER:
- Is the simplified version genuinely easier to understand?
- Did you introduce any new patterns inconsistent with the codebase?
- Is the diff clean and reviewable?
- Would a teammate approve this change?
```

If the "simplified" version is harder to understand or review, revert. Not every simplification attempt succeeds.

## Language-Specific Guidance

### TypeScript / JavaScript

```typescript
// SIMPLIFY: Unnecessary async wrapper
// Before
async function getUser(id: string): Promise<User> {
  return await userService.findById(id);
}
// After
function getUser(id: string): Promise<User> {
  return userService.findById(id);
}
```

```typescript
// SIMPLIFY: Verbose conditional assignment
// Before
let displayName: string;
if (user.nickname) {
  displayName = user.nickname;
} else {
  displayName = user.fullName;
}
// After
const displayName = user.nickname || user.fullName;
```

```typescript
// SIMPLIFY: Manual array building
// Before
const activeUsers: User[] = [];
for (const user of users) {
  if (user.isActive) {
    activeUsers.push(user);
  }
}
// After
const activeUsers = users.filter((user) => user.isActive);
```

```typescript
// SIMPLIFY: Redundant boolean return
// Before
function isValid(input: string): boolean {
  if (input.length > 0 && input.length < 100) {
    return true;
  }
  return false;
}
// After
function isValid(input: string): boolean {
  return input.length > 0 && input.length < 100;
}
```

### Python

```python
# SIMPLIFY + FIX: list.remove() on deserialized objects → filter by ID
# When queue entries come from JSON file loads, list.remove(obj) can fail
# with ValueError if the file changed between loads (different instance).
# Always use filter by ID instead.
# Before (race condition, crashes on double-load):
queue = _load_queue()
entry = get_pending_approval()  # loads file AGAIN → different instance!
queue["pending"].remove(entry)   # ValueError: list.remove(x): x not in list

# After (load once, filter by ID):
queue = _load_queue()
entry = next((e for e in reversed(queue["pending"])
              if e.get("status") == "pending_approval"), None)
col_id = entry.get("id")
queue["pending"] = [e for e in queue["pending"] if e.get("id") != col_id]
```

#### Pitfall: Python 3.12+ invalid escape sequences in code-generation patterns

**Symptom**: `SyntaxWarning: invalid escape sequence '\|'` when running a Python script that generates/modifies Python code through string templates (triple-quoted strings, heredocs). The generated parser file has `\\|` (two backslashes + pipe) where it should have `\|` (one backslash + pipe), causing regex patterns to match literal `\\` instead of `|`.

**Root cause**: Python 3.12+ warns about invalid escape sequences (like `\|`, `\s`, `\d`) in **regular (non-raw) strings**. This matters when you embed `r"..."` regex patterns inside an outer triple-quoted string:
```python
# Outer string (NOT raw) contains embedded raw regex string
new_code = '''...cm = re.search(r"\\\|\\s*Covers...", bk)...'''
#           ^-- outer string processes \\ first:
#               \\ → \  (one backslash)
#               \| → \| (invalid escape, SyntaxWarning, stays as \|)
# Result in file: r"\|..."  ← CORRECT by accident
```

The `\|` inside the outer string is an invalid escape. In Python 3.12-3.14 it produces `\|` (backslash+pipe) with a warning, but in Python 3.15+ it will produce just `|` (pipe only), breaking the regex.

**Detection**: Run `python3 -W error script.py` — if it crashes on an invalid escape, the pattern needs fixing. Or grep for `'\\|'`, `'\\s'`, `'\\d'` in triple-quoted strings that aren't raw.

**Fix strategies** (from safest to riskiest):

1. **BEST — Use a separate `.py` file** (write_file → execute) instead of embedding code in triple-quoted strings. This avoids all escaping issues because each file is a clean Python module with its own string context. This is the most reliable pattern for parser simplifications.

2. **GOOD — Use raw outer string**: Prefix the outer triple-quoted string with `r`: `r'''...r"\\|"...'''`. In a raw outer string, `\\` is literal, so `\\|` produces `\\|` (two backslashes + pipe) in the output — matching the original `\\|` regex in the target file. **But**: raw strings cannot contain `\'''` (backslash + triple quote), so this fails if your code template ends with `'''`.

3. **ACCEPTABLE — Use double backslash `\\\\` in the outer string**: In a non-raw outer string `'''...\\\\...'''`, `\\\\` → `\\` (two backslashes). This produces the regex `\\` which matches literal `\`. But this creates confusing "backslash Tetris" in the source — hard to read, easy to get wrong.

4. **SPECIAL CASE — For `\|` specifically in Python 3.12-3.14**: The current behavior (`\|` → `\|`) happens to be correct for regex pipes. But this WILL break in Python 3.15+. Use strategy 1 or 2 instead.

**Real example (2026-06-29)**: `hourly_cover_parser.py` simplification — the `_tmp_simplify.py` script embedded regex patterns in a `'''...'''` outer string. Python 3.14 produced `\|` (correct for regex) but with a SyntaxWarning. After git restore and re-application, the patterns had to be applied via write_file not heredoc to avoid the ambiguity.

**Prevention**: When building scripts that modify Python source code through string generation:
1. Prefer `write_file` to write a complete `.py` file, then execute it — avoids all nesting issues
2. If using heredocs, use `<< 'PYEOF'` (single-quoted delimiter prevents shell expansion) and write Python that reads/writes files with `path.read_text()` + `str.replace()` — this avoids string-escaping layers entirely
3. Test regex patterns in the GENERATED file by reading it back and compiling before running

```python
# SIMPLIFY: Verbose dictionary building
# Before
result = {}
for item in items:
    result[item.id] = item.name
# After
result = {item.id: item.name for item in items}
```

```python
# SIMPLIFY: Nested conditionals with early return
# Before
def process(data):
    if data is not None:
        if data.is_valid():
            if data.has_permission():
                return do_work(data)
            else:
                raise PermissionError("No permission")
        else:
            raise ValueError("Invalid data")
    else:
        raise TypeError("Data is None")
# After
def process(data):
    if data is None:
        raise TypeError("Data is None")
    if not data.is_valid():
        raise ValueError("Invalid data")
    if not data.has_permission():
        raise PermissionError("No permission")
    return do_work(data)
```

```python
# SIMPLIFY: Double-scan elimination — avoid scanning the same string twice
# Before
if date_str in content:                        # scan #1
    sec_start = content.find(f"## ", content.find(date_str) - 50)  # scan #2
...
# After
pos = content.find(date_str)                   # one scan
if pos < 0:
    continue                                   # early exit, no else
```

**Note:** The outer `if x in s:` pre-check is a natural reflex but adds a full O(n) scan with zero benefit when you immediately call `s.find(x)` anyway. A single `s.find()` + `if pos < 0: continue` is one scan, flatter (no else), and more idiomatic Python.

```python
# SIMPLIFY: rfind for section boundaries in delimited documents
# When you need the preceding header/section-marker before a known position
# in markdown, config files, or any `## `-delimited document:
# Before
sec_start = content.find(f"## ", content.find(date_str) - 50)
if sec_start < 0:
    sec_start = content.find(date_str)

# After
section_start = content.rfind("## ", 0, pos)
if section_start < 0:
    section_start = max(0, pos - 100)
```

`str.rfind(sub, start, end)` searches *backward* from `end`, finding the *last* occurrence of `sub` before the target position. This is exactly the right tool: "find the closest `## ` header that starts before `pos`." No magic offsets, no double scans.

```python
# SIMPLIFY: date.fromisoformat() replaces manual date(int(...), int(...), int(...))
# Before
parts = week_start.split("-")
ws = date(int(parts[0]), int(parts[1]), int(parts[2]))

# After
start_date = date.fromisoformat(week_start)
```

`date.fromisoformat()` (Python 3.7+) handles ISO 8601 format `YYYY-MM-DD` natively — no split, no int-casting, no IndexError if the string is malformed. Available for any `date` parsing from a well-known format. For arbitrary date strings use `datetime.strptime` instead.

### React / JSX

```tsx
// SIMPLIFY: Verbose conditional rendering
// Before
function UserBadge({ user }: Props) {
  if (user.isAdmin) {
    return <Badge variant="admin">Admin</Badge>;
  } else {
    return <Badge variant="default">User</Badge>;
  }
}
// After
function UserBadge({ user }: Props) {
  const variant = user.isAdmin ? 'admin' : 'default';
  const label = user.isAdmin ? 'Admin' : 'User';
  return <Badge variant={variant}>{label}</Badge>;
}
```

```tsx
// SIMPLIFY: Prop drilling through intermediate components
// Before — consider whether context or composition solves this better.
// This is a judgment call — flag it, don't auto-refactor.
```

## Simplification Patterns Applied (L'Usine Case Management)

| Pattern | Before | After | File |
|---------|--------|-------|------|
| **Shared helper for duplicate logic** | `detect_section` + `detect_field` both loop keywords | Single `_match_keywords(text, dict)` | parser |
| **Delete dead constants** | `WORKSPACE_ROOT = VAULT_ROOT`, `NO_CALENDAR_FLAG` | Removed, use `VAULT_ROOT` directly | handler |
| **Remove unused imports** | 8 imports from parser | 4 imports (only used ones) | handler |
| **Delete no-op functions** | `extract_update_text()` (just `.strip()`) | Kept but marked `# no-op, API compat` | parser |
| **Simplify title extraction** | Tokenize body, scan for `#` | Split lines, find first `#` | parser |
| **Inline obvious constants** | `now_time_str()` called nowhere | Deleted | handler |
| **Simplify conditional logic** | `if not show_all: pass` blocks | `if not show_all and status != "active": continue` | cli |
| **Remove dead code** | `if resolution: pass` in close_case | Deleted | cli |
| **Consolidate imports** | `import yaml` inside function | Top-level | cli |

**Rule applied:** "If you delete it and tests still pass, it was dead code."

## Real-World Simplifications from This Session

### 1. Shared Helper for Near-Identical Functions
**Before:** Two functions with identical loop structure:
```python
def detect_section(text):
    normalized = text.strip().lower()
    for section, keywords in SECTION_KEYWORDS.items():
        if any(k in normalized for k in keywords): return section

def detect_field(text):
    normalized = text.strip().lower()
    for field, keywords in FIELD_KEYWORDS.items():
        if any(k in normalized for k in keywords): return field
```

**After:** Single shared helper:
```python
def _match_keywords(text, keyword_dict):
    normalized = text.strip().lower()
    for key, keywords in keyword_dict.items():
        if any(k in normalized for k in keywords): return key

def detect_section(text): return _match_keywords(text, SECTION_KEYWORDS)
def detect_field(text): return _match_keywords(text, FIELD_KEYWORDS)
```

### 2. Simplify Title Extraction (Tokenization → Line Scan)
**Before:** Tokenize entire body, find first `#` token, reconstruct from tokens
```python
body_tokens = tokenize(body)
for idx, token in enumerate(body_tokens):
    if token.startswith("#") and idx + 1 < len(body_tokens):
        title = " ".join(body_tokens[:idx+3])
        break
```

**After:** Direct line iteration
```python
for line in body.splitlines():
    if line.strip().startswith("#"):
        title = line.strip().lstrip("# ")
        break
```

### 3. Remove Alias Constants
**Before:** `WORKSPACE_ROOT = VAULT_ROOT` — used once in one function
**After:** Inline `VAULT_ROOT` directly, delete alias

### 4. Inline Trivial Functions
**Before:** `def extract_update_text(payload): return payload.strip()`
**After:** Delete (or mark `# no-op, kept for API compat` if public API)

### 5. Dead Code Elimination
**Before:** `if resolution: pass` in close_case
**After:** Delete block entirely

### 6. Hoist Local Imports
**Before:** `def f(): import sys; ...`
**After:** `import sys` at module top (stdlib imports are always cheap)

### 7. Non-Friction Windows Deployment
**Before:** NSSM Windows Service with SYSTEM account, password prompts, PATH issues
**After:** `.bat` file with auto-restart loop in Startup folder
- No NSSM install, no password, no SYSTEM account
- Auto-restart on crash via `goto loop`
- Zero friction: click `.bat` or add to Startup folder

### 8. Python Module Path Resolution
**Before:** ModuleNotFoundError when running from skill directory
**After:** `set PYTHONPATH=%SKILL_DIR%;%VAULT_SCRIPTS_DIR%` in .bat before python -m

### 9. Telegram Bot Integration with aiogram 3.x
- Use polling (not webhook) for zero-friction deployment
- Wire to existing NL handler (`handle_message`)
- Env config via .env: `TELEGRAM_BOT_TOKEN`, `TELEGRAM_ALLOWED_USERS`
- Allowlist via `TELEGRAM_ALLOWED_USERS` (empty = dev mode allow all)

### 10. Dict-Driven Replace Chain
**Before:** 27 `.replace()` lines, one per placeholder:
```python
html = html.replace("{WEEKS}", json.dumps(weeks))
html = html.replace("{START}", str(start_w))
# ... 25 more lines ...
```
**After:** Single dict + 2-line loop:
```python
placeholders = {"{WEEKS}": json.dumps(weeks), "{START}": str(start_w), ...}
for ph, val in placeholders.items():
    html = html.replace(ph, val)
```

### 11. Zip for Element-Wise Parallel Sums
**Before:** `sys_ord = [ord_lu3[i] + ord_lu5[i] + ord_lu7[i] for i in range(len(records))]`
**After:** `sys_ord = [a + b + c for a, b, c in zip(ord_lu3, ord_lu5, ord_lu7)]`

### 12. Helper + Comprehension for Nested Loop + Pre-Allocation
**Before:** 12 lines of imperative pre-allocation + nested loop + if-elif-else
**After:** Small helper + three list comprehensions (see reference file)

### 13. defaultdict Auto-Vivification for Nested Accumulators
**Before:** Outer dict + inner dict with manual `if key not in` guards:
```python
by_item = {}
for r in parsed:
    key = r["item"].strip().lower()
    if key not in by_item:
        by_item[key] = {"qty": 0, "net_rev": 0.0, "stores": {}}
    by_item[key]["qty"] += r["qty"]
    by_item[key]["net_rev"] += r["net_rev"]
    store = r["store"]
    if store not in by_item[key]["stores"]:
        by_item[key]["stores"][store] = {"qty": 0, "net_rev": 0.0}
    by_item[key]["stores"][store]["qty"] += r["qty"]
    by_item[key]["stores"][store]["net_rev"] += r["net_rev"]
```

**After:** `defaultdict` for inner dict + local alias to avoid repeated indexing:
```python
by_item = {}
for r in parsed:
    key = r["item"].strip().lower()
    if key not in by_item:
        by_item[key] = {"qty": 0, "net_rev": 0.0,
                        "stores": defaultdict(lambda: {"qty": 0, "net_rev": 0.0})}
    entry = by_item[key]
    entry["qty"] += r["qty"]
    entry["net_rev"] += r["net_rev"]
    sd = entry["stores"][r["store"]]
    sd["qty"] += r["qty"]
    sd["net_rev"] += r["net_rev"]
```

**Why better:** Removes 1 level of nesting (no inner `if`). `defaultdict` auto-vivifies the store accumulator on first access. The local aliases (`entry`, `sd`) replace repeated `by_item[key]` and `by_item[key][...]` indexing, making each arithmetic line a one-liner.

**Tradeoff:** The outer `if key not in` is kept intentionally — using `setdefault` would evaluate the dict literal on every iteration (wasteful). Using `defaultdict` for the outer dict would require a factory function that knows `r` per iteration. The hybrid pattern (outer `if`, inner `defaultdict`) is the sweet spot.

**Also applied in this session:**
- Orphan cleanup: `[k for k in d if not d[k].get(...)]` → `[k for k, v in d.items() if not v.get(...)]`
- Month tracking: manual `set() + for-loop + .add()` → set comprehension + `sorted()`

See `references/2026-07-06-accumulate-week-simplification.md` for the full before/after.

## Pitfalls

### P1. Pitfall Loading the Code-Simplification Skill
**Lesson from session 2026-07-06:** When asked to simplify code, the agent loaded this skill only *after* completing the work, not before. The skill's triggers explicitly cover this use case, and following its steps would have caught the template-placeholder coverage check earlier.

**Action:** If you are about to simplify, deduplicate, or refactor code — load this skill first.

### P2. Pitfall: String-Template Artifacts After Simplification
**Symptom:** Dashboard rendered but unstyled — pipe characters (`|`) injected into CSS inside a Python string template by a subagent trying to improve formatting.
**Prevention:** After any simplification touching string templates, generate the output and grep for artifact characters. Run a syntax-validity check on the output, not just compilation of the generator.

### P3. Pitfall: Multi-Store Data Source Confusion in Chart Helpers
**Symptom:** Multi-store chart showed only 1 visible line because `isAll` flag was used to switch data source instead of just controlling dataset inclusion.
**Rule:** Never use a view-mode flag to choose the data source. Base the source on which entity is being read.

### P4. Pitfall: Orphaned F-String Escapes in Non-F-String Templates
**Symptom:** HTML output has `{{` everywhere — JavaScript sees double braces, syntax errors.
**Rule:** Choose ONE substitution strategy: either f-strings (`f"""..."""` + `{{` escapes) OR `.replace()` (single braces for JS + unique placeholders). Never mix. `r"""` + `{{` = wrong. After generating, grep for orphan `{{`.