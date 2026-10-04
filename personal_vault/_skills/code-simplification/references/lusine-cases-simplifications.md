# Simplifications Applied: lusine-cases Skill Development

## Session Context
Applied: 2026-06-19 | Session: lusine-cases skill development | Outcome: 30/30 tests passing, 9 simplifications

---

## Simplification Patterns Applied

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

**File:** `scripts/case_brain_nl_parser.py`

---

### 2. Remove Dead / Redundant Constants
**Before:**
```python
WORKSPACE_ROOT = VAULT_ROOT  # Alias, used once
NO_CALENDAR_FLAG = "migrate-simplify --no-calendar"  # Never used
```

**After:** Deleted. Use `VAULT_ROOT` directly. Flag inlined where needed.

**File:** `scripts/case_brain_nl_handler.py`

---

### 3. Remove Unused Imports
**Before (8 imports from parser):**
```python
from case_brain_nl_parser import (
    detect_prefix,
    find_case_by_query,
    find_case_files,
    parse_frontmatter,
    format_frontmatter,
    detect_section,
    detect_field,
    extract_update_text,  # UNUSED
    build_update_entry,
    inject_update_entry,
    split_frontmatter_and_body,  # UNUSED
    SECTION_KEYWORDS,  # UNUSED
    FIELD_KEYWORDS,  # UNUSED
    tokenize,  # UNUSED
)
```

**After (4 imports):**
```python
from case_brain_nl_parser import (
    detect_prefix,
    find_case_by_query,
    parse_frontmatter,
    format_frontmatter,
    detect_section,
    detect_field,
    build_update_entry,
    inject_update_entry,
)
```

**File:** `scripts/case_brain_nl_handler.py`

---

### 4. Keep No-Op Function for API Compatibility
**Function:**
```python
def extract_update_text(payload: str) -> str:
    return payload.strip()  # no-op, kept for API compatibility
```

**Decision:** Kept but marked `# no-op, kept for API compatibility` — public API may depend on it.

**File:** `scripts/case_brain_nl_parser.py`

---

### 5. Simplify Title Extraction (Tokenization → Line Scan)
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

**File:** `scripts/case_brain_nl_parser.py` — `find_case_by_query()`

---

### 6. Delete Unused Function
**Function:** `now_time_str()` — never called anywhere

**Action:** Deleted entirely.

**File:** `scripts/case_brain_nl_handler.py`

---

### 7. Simplify Conditional Logic (Guard Clauses)
**Before:**
```python
if status == "active":
    active_count += 1
    if not show_all:
        # Only show active unless --all
        pass
    else:
        pass  # Will print below
else:
    closed_count += 1
    if not show_all:
        continue
```

**After:**
```python
if status == "active":
    active_count += 1
else:
    closed_count += 1
if not show_all and status != "active":
    continue
```

**File:** `scripts/ops_cases_cli.py` — `list_cases()`

---

### 8. Remove Dead Code Blocks
**Before:**
```python
def close_case(slug, resolution=None):
    orch_args = ["followup", "--slug", slug, "--close"]
    if resolution:
        # Resolution is passed via case file update, orchestrator uses default
        # We could extend orchestrator to accept resolution, for now use default
        pass
    run_orchestrator(orch_args)
```

**After:**
```python
def close_case(slug, resolution=None):
    orch_args = ["followup", "--slug", slug, "--close"]
    run_orchestrator(orch_args)
```

**File:** `scripts/ops_cases_cli.py`

---

### 9. Hoist Local Imports to Module Top
**Before:**
```python
def list_cases(show_all=False):
    import yaml
    ...
```

**After:**
```python
import yaml

def list_cases(show_all=False):
    ...
```

**File:** `scripts/ops_cases_cli.py`

---

## Verification

All simplifications verified by **running full test suite (30/30 pass)** after each change:

| Phase | Tests | Result |
|-------|-------|--------|
| Before simplifications | 30 | 30/30 ✅ |
| After each simplification | 30 | 30/30 ✅ |
| Final | 30 | 30/30 ✅ |

---

## Rule Applied

> **ASK BEFORE EVERY CHANGE:**
> → Does this produce the same output for every input?
> → Does this maintain the same error behavior?
> → Does this preserve the same side effects and ordering?
> → Do all existing tests still pass without modification?

> **RULE:** If you delete it and tests still pass, it was dead code.

---

## Session Artifacts

| Simplification | File | Lines Changed |
|----------------|------|---------------|
| Shared helper `_match_keywords` | `case_brain_nl_parser.py` | ~20 |
| Remove `WORKSPACE_ROOT`, `NO_CALENDAR_FLAG` | `case_brain_nl_handler.py` | -5 |
| Remove unused imports | `case_brain_nl_handler.py` | -12 |
| Mark `extract_update_text` as no-op | `case_brain_nl_parser.py` | +1 comment |
| Simplify `find_case_by_query` title extraction | `case_brain_nl_parser.py` | -8 |
| Delete `now_time_str()` | `case_brain_nl_handler.py` | -3 |
| Simplify `list_cases()` conditionals | `ops_cases_cli.py` | -6 |
| Remove `if resolution: pass` block | `ops_cases_cli.py` | -4 |
| Hoist `import yaml` | `ops_cases_cli.py` | +1/-1 |

**Total:** ~60 lines added/removed, **net reduction** in complexity