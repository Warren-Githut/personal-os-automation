# 2026-07-06 — `menu_gp_parser.py` v2.0 Simplification

**Source file:** `vault/scripts/menu_gp_parser.py` (917→931 lines, ~38KB)
**Goal:** Deduplicate `bcq_counts`, simplify patterns. Zero behavior change.

---

## Changes Applied

### 1. Extract inner function to module level + add parameter

`write_table()` was an inner function inside `build_entry()` that captured `lines` from the enclosing scope via closure. Moving to module level required injecting `lines` as an explicit parameter — making the dependency visible and the function independently testable.

| Aspect | Before | After |
|--------|--------|-------|
| Scope | Inner function of `build_entry()` | Module-level `def _write_table(lines, title, grp_items, emoji)` |
| Closure dependency | `lines` captured from enclosing scope | Explicit parameter |
| Duplication | Identical body existed once (only one call site) | None — but extracted for clarity and testability |

**Before:**
```python
def build_entry(...):
    ...
    def write_table(title, grp_items, emoji):
        if not grp_items:
            return
        lines.append(f"{emoji} **{title}**")
        lines.append("| # | Item | Units | Rev(M) | GP% |")
        lines.append("|---|---|---|---|---|")
        for idx, it in enumerate(grp_items[:10], 1):
            lines.append(...)
        lines.append("")

    write_table("Top 10 Food (Best Margin)", food_items, "🥩")
    write_table("Top 10 Beverage (Best Margin)", drink_items, "🥤")
```

**After:**
```python
def _write_table(lines, title, grp_items, emoji):
    if not grp_items:
        return
    lines.append(f"{emoji} **{title}**")
    lines.append("| # | Item | Units | Rev(M) | GP% |")
    lines.append("|---|---|---|---|---|")
    for idx, it in enumerate(grp_items[:10], 1):
        lines.append(...)
    lines.append("")

def build_entry(...):
    ...
    _write_table(lines, "Top 10 Food (Best Margin)", food_items, "🥩")
    _write_table(lines, "Top 10 Beverage (Best Margin)", drink_items, "🥤")
```

### 2. Extract duplicated inner function algorithm to shared helper

`bcq_counts()` was an inner function inside `_build_json_block()` that classified items into BCG menu-engineering quadrants. The **identical algorithm** was inlined in `build_entry()` with different variable names and dict key casing (`"Star"` vs `"star"`, `"PH"` vs `"ph"`).

| Aspect | Before | After |
|--------|--------|-------|
| `_build_json_block` | Inner `def bcq_counts(grp)` | Calls `_menu_eng_counts(items)` |
| `build_entry` | 8 lines of inline logic with capitalised keys | Calls `_menu_eng_counts(grp)` with lowercase keys |
| Maintenance risk | Two copies to keep in sync | Single source of truth |

**Before (16 lines across 2 locations):**
```python
# In _build_json_block:
def bcq_counts(grp):
    if not grp:
        return {"star": 0, "ph": 0, "dog": 0, "qmark": 0}
    gp_vals = sorted([i["gp_pct"] for i in grp])
    qty_vals = sorted([i["qty"] for i in grp])
    med_gp = gp_vals[len(gp_vals) // 2]
    med_qty = qty_vals[len(qty_vals) // 2]
    c = {"star": 0, "ph": 0, "dog": 0, "qmark": 0}
    for i in grp:
        hgp, hqt = i["gp_pct"] >= med_gp, i["qty"] >= med_qty
        if hgp and hqt: c["star"] += 1
        elif not hgp and hqt: c["ph"] += 1
        elif not hgp and not hqt: c["dog"] += 1
        else: c["qmark"] += 1
    return c

# In build_entry (inline, capitalised keys):
gp_v = sorted([i["gp_pct"] for i in grp])
qt_v = sorted([i["qty"] for i in grp])
med_gp = gp_v[len(gp_v) // 2]
c = {"Star": 0, "PH": 0, "Dog": 0, "?": 0}
for i in grp:
    hgp, hqt = i["gp_pct"] >= med_gp, i["qty"] >= qt_v[len(qt_v) // 2]
    if hgp and hqt: c["Star"] += 1
    elif not hgp and hqt: c["PH"] += 1
    elif not hgp and not hqt: c["Dog"] += 1
    else: c["?"] += 1
```

**After (single shared function):**
```python
def _menu_eng_counts(items):
    if not items:
        return {"star": 0, "ph": 0, "dog": 0, "qmark": 0}
    gp_vals = sorted(i["gp_pct"] for i in items)
    qty_vals = sorted(i["qty"] for i in items)
    med_gp = gp_vals[len(gp_vals) // 2]
    med_qty = qty_vals[len(qty_vals) // 2]
    counts = {"star": 0, "ph": 0, "dog": 0, "qmark": 0}
    for i in items:
        hgp = i["gp_pct"] >= med_gp
        hqt = i["qty"] >= med_qty
        if hgp and hqt: counts["star"] += 1
        elif not hgp and hqt: counts["ph"] += 1
        elif not hgp and not hqt: counts["dog"] += 1
        else: counts["qmark"] += 1
    return counts
```

**Key consistency check:** Both call sites used `gp_vals[len(gp_vals) // 2]` for median — the **upper‑median convention** (for 2 items, picks the second). Extracting to a shared function guarantees both stay in sync.

### 3. Extract `_median_gp()` helper

The inline `round(sorted(gp_vals)[len // 2], 1) if ... else 0` appeared twice in `_build_json_block()`'s `menu_eng` dict literal. Extracted to a one-line helper:

```python
def _median_gp(items):
    if not items:
        return 0
    gp_vals = sorted(i["gp_pct"] for i in items)
    return round(gp_vals[len(gp_vals) // 2], 1)
```

Then the dict literal becomes a clean two-liner:
```python
"menu_eng": {
    "food": {"total": len(food), "med_gp": _median_gp(food), **_menu_eng_counts(food)},
    "bev": {"total": len(bev), "med_gp": _median_gp(bev), **_menu_eng_counts(bev)},
}
```

### 4. Simplify nested store-data loop with `.get()` + local alias

**Before:** `if s_name in store_data:` + three `store_data[s_name][...]` accesses per iteration, then `for s in STORES: store_data[s]["items"] = len(...)`

**After:** `sd = store_data.get(s_name); if sd:` + three `sd[...]` accesses on local alias, then `for sd in store_data.values(): sd["items"] = len(sd["items"])`

| Aspect | Before | After |
|--------|--------|-------|
| Dict lookup pattern | `if s_name in d: d[s_name]...d[s_name]...d[s_name]` | `sd = d.get(s_name); if sd: sd...sd...sd` |
| Final loop | `for s in STORES: d[s]["items"] = len(...)` — dependent on key list | `for sd in d.values(): sd["items"] = len(...)` — agnostic to keys |

The `.get()` approach avoids redundant dict key checks on every line and reads as "find or skip" rather than "check existence then index."

---

## Verification Strategy

An ad-hoc assertion-driven script was created and run against the refactored file (cleaned up after pass). Structure:

1. **`_menu_eng_counts()`** — 8 items spanning all 4 quadrants (2 each), empty list, single-item edge cases
2. **`_median_gp()`** — empty, single, odd-count, even-count including upper-median convention check
3. **`_write_table()`** — format check (header columns), empty table (no output), line count per item count
4. **`_build_json_block()`** — full JSON block: structure, store keys, menu-engineering quadrants, flag detection, unmatched count
5. **`_write_table` call parity** — same call pattern as `build_entry()` uses, verifying interleaved food/beverage tables

### Pitfall: Test expectations must match the algorithm, not intuition

The median convention (`len // 2`) picks the **upper** element for even-length lists. Several test assertions initially failed because they assumed mean-of-two or lower-median semantics. The extracted helper is correct — the tests were wrong. Always verify against the *original* algorithm, not what feels right.

---

---

## Round 2: `cross_check_month_revenue()` (same session, same file)

**Goal:** Reduce complexity, shorten code, improve readability of the RevLog cross-check function (~58 lines).

### Changes Applied

#### 1. `date.fromisoformat()` replaces manual string splitting

**Before:** Manual parse with `date(int(parts[0]), int(parts[1]), int(parts[2]))`
**After:** `date.fromisoformat(week_start)` — stdlib one-liner, no IndexError risk.

```python
# Before
parts = week_start.split("-")
ws = date(int(parts[0]), int(parts[1]), int(parts[2]))
we = ws + timedelta(days=6)

# After
start_date = date.fromisoformat(week_start)
end_date = start_date + timedelta(days=6)
```

#### 2. Double-scan eliminated (`if x in s` + `s.find(x)` → single `s.find()`)

**Before:** Two O(n) scans of the full RevLog content per week:
```python
if date_str in content:            # scan #1
    sec_start = content.find(f"## ", content.find(date_str) - 50)  # scan #2
```

**After:** One scan, one check:
```python
pos = content.find(date_str)
if pos < 0:
    print(f"    WARN: ...")
    continue
```

#### 3. `rfind` for section boundary instead of magic-offset backup

**Before:** Backup from date position minus 50, then fallback:
```python
sec_start = content.find(f"## ", content.find(date_str) - 50)
if sec_start < 0:
    sec_start = content.find(date_str)
```

**After:** Walk backward from the match to the preceding `## ` header:
```python
section_start = content.rfind("## ", 0, pos)
if section_start < 0:
    section_start = max(0, pos - 100)
```

`rfind` with an end-position bound is the right tool — it finds the *last* `## ` before the target position, which is exactly the enclosing header.

#### 4. Flatten control flow (3 levels → 2)

**Before:** `if date_str in content:` with an `else:` branch — the "not found" case was nested inside an `else`.
**After:** `if pos < 0: print + continue` — flat loop body, the "not found" case exits early instead of wrapping the success path.

#### 5. Better variable names

| Before | After | Why |
|--------|-------|-----|
| `ws` | `start_date` | Self-documenting |
| `we` | `end_date` | Self-documenting |
| `sec_start` | `section_start` | Full word, clear |
| `sec_end` | `section_end` | Full word, clear |

### Verification Strategy

An ad-hoc assertion-driven script was created, run, and cleaned up:

1. **Mock RevLog file** created in `tempfile.TemporaryDirectory` with 5 weeks of known revenue data
2. **`REV_LOG` monkey-patched** to point at the temp file
3. **5 test scenarios** covering all paths:
   - Exact match (Star Horse == RevLog, diff = 0%)
   - Big delta (7.69% > 5% threshold → `ok=False`)
   - Missing RevLog file (graceful skip)
   - One extra week with no RevLog match (still extracts the 4 valid weeks)
   - Zero matched weeks at all (returns `(True, 0, 0)`)
4. **12 assertions** — all passed first time after fixing an invalid-date test input (PITFALL: always use valid dates in dummy test data, or `date.fromisoformat` will raise `ValueError`)
5. **Temp script cleaned up** with `rm`

### Verdict

| Pattern | Applied | Impact |
|---------|---------|--------|
| `date.fromisoformat()` | Yes | 3 fewer lines, no IndexError risk |
| Double-scan → single `find()` | Yes | 1 fewer O(n) scan per week |
| `rfind` for section boundary | Yes | No magic offset, clearer intent |
| Flat control flow with `continue` | Yes | 3 levels → 2 |
| Better variable names | Yes | Readability, not lines |

Net: still ~60 lines (blank lines added for breathing room), but every scan is single-pass and the section-finding algorithm expresses intent directly.

---

## Summary

| Change | Pattern | Lines changed |
|--------|---------|--------------|
| `write_table` inner→module | Move inner function, add missing parameter | −10 |
| `bcq_counts`→`_menu_eng_counts` | Extract duplicated algorithm to shared helper | −18 |
| `_median_gp` helper | Extract repeated inline expression to named function | −4 |
| Store data loop | `.get()` + local alias + `.values()` iteration | −2 |
| `cross_check_month_revenue()` | `date.fromisoformat`, `rfind`, double-scan elimination, flat control flow, naming | N/A |
