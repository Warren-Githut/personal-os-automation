# Simplification Patterns from L'Usine Session (2026-06-19)

## Applied Patterns (12 total)

### 1. Shared Helper for Duplicate Logic
**Before:**
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

**After:**
```python
def _match_keywords(text, keyword_dict):
    normalized = text.strip().lower()
    for key, keywords in keyword_dict.items():
        if any(k in normalized for k in keywords): return key

def detect_section(text): return _match_keywords(text, SECTION_KEYWORDS)
def detect_field(text): return _match_keywords(text, FIELD_KEYWORDS)
```

**File:** `case_brain_nl_parser.py`

---

### 2. Delete Dead Constants
**Before:**
```python
WORKSPACE_ROOT = VAULT_ROOT
NO_CALENDAR_FLAG = "migrate-simplify --no-calendar"
```

**After:** Inline `VAULT_ROOT` directly, delete aliases.

**File:** `case_brain_nl_handler.py`

---

### 3. Remove Unused Imports
**Before:** 8 imports from `case_brain_nl_parser`
**After:** 4 imports (only used ones)

**File:** `case_brain_nl_handler.py`

---

### 4. Delete No-Op Functions
**Before:**
```python
def extract_update_text(payload: str) -> str:
    return payload.strip()
```

**After:** Mark `# no-op, kept for API compat` if public API, else delete.

**File:** `case_brain_nl_parser.py`

---

### 5. Simplify Title Extraction
**Before:**
```python
body_tokens = tokenize(body)
for idx, token in enumerate(body_tokens):
    if token.startswith("#") and idx + 1 < len(body_tokens):
        title = " ".join(body_tokens[:idx + 3])
        break
```

**After:**
```python
for line in body.splitlines():
    if line.strip().startswith("#"):
        title = line.strip().lstrip("# ")
        break
```

**File:** `case_brain_nl_parser.py`

---

### 6. Dead Code Elimination
**Before:**
```python
if resolution:
    pass
```

**After:** Delete block entirely.

**File:** `ops_cases_cli.py`

---

### 7. Inline Trivial Functions
**Before:**
```python
def now_time_str() -> str:
    return datetime.now().strftime("%H:%M")
```

**After:** Delete (never called).

**File:** `case_brain_nl_handler.py`

---

### 8. Hoist Local Imports
```python
# Before: import yaml inside list_cases()
# After: import yaml at module top
```

**File:** `ops_cases_cli.py`

---

### 9. Simplify Conditional Logic
**Before:**
```python
if not show_all:
    pass
else:
    pass
```

**After:**
```python
if not show_all and status != "active":
    continue
```

**File:** `ops_cases_cli.py`

---

### 10. Hidden Data Block (JSON in HTML Comment)

**Context:** Ops data files serve two audiences: humans reading and machines parsing. Visible JSON clutters the human view.

**Pattern:** Wrap machine-only JSON in HTML comments. Grep for `HERMES JSON BLOCK`, humans see nothing.

**Before (visible JSON block):**
```markdown
### Machine Data
```json
{"week":"W27","system":{"qty":4280}}
```

**After (hidden from human, grep-able by machine):**
```markdown
<!-- HERMES JSON BLOCK
```json
{"week":"W27","system":{"qty":4280}}
```
-->
```

**Why better:** One file, two views, zero duplication.

**Pitfall:** ENTIRE block must be inside `<!-- ... -->`. Put `<!-- HERMES JSON BLOCK` on the line before ` ```json`, and `-->` on the line after closing ` ````.

**File:** `11_Item_Sales_Weekly_Log_Star_Horse_Tracker.md` (v2.0)

---

### 11. Repeated Formula → Shared Helper (`_pct_change`)

**Context:** Same arithmetic appears ~10 times in one function.

**Before:**
```python
d_q = ((system_items - p["qty"]) / p["qty"] * 100) if p["qty"] else 0
d_r = ((system_rev - p["rev"]) / p["rev"] * 100) if p["rev"] else 0
```

**After:**
```python
def _pct_change(new, old):
    return ((new - old) / old * 100) if old else 0.0

d_q = _pct_change(system_items, p["qty"])
d_r = _pct_change(system_rev, p["rev"])
```

**When to extract:** 3+ repetitions. Not for 2.

**File:** `item_sales_parser.py` (v2.0)

---

### 12. elif Chain → Dict-Driven (infer_category)

**Before (8 elif branches):**
```python
if "breakfast" in g: return "Breakfast"
elif "lunch" in g: return "Lunch"
elif "coffee" in g: return "Drink"
elif "cake" in g: return "Breakfast"
# ... 4 more elifs ...
return "Lunch"
```

**After (1 dict + 1 loop):**
```python
CATEGORY_KEYWORDS = {
    "Breakfast": ["breakfast", "brunch", "cake", "gelato"],
    "Lunch": ["lunch", "main", "dinner", "sandwich"],
    "Drink": ["coffee", "drink", "beverage", "juice"],
}
if g:
    for cat, keywords in CATEGORY_KEYWORDS.items():
        if any(k in g for k in keywords):
            return cat
return "Lunch"
```

**Why better:** Adding category = 1 dict entry. Mapping declarative, not imperative.

**File:** `item_sales_parser.py` (v2.0)

---

## Verification Rule

> **"If you delete it and tests still pass, it was dead code."**

---

## Applicability Checklist

Before applying any simplification:
- [ ] Does it change behavior?
- [ ] Is it actually dead/unused? (grep for usage)
- [ ] Does it follow project conventions?
- [ ] Is the abstraction earning its complexity? (3+ uses minimum)
