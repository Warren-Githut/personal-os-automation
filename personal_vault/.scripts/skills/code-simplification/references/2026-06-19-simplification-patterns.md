# Simplification Patterns: L'Usine Case Management Session

## 9 Patterns Applied (All Tests Pass: 30/30)

| # | Pattern | Before | After | File |
|---|---------|--------|-------|------|
| 1 | **Shared helper for duplicate logic** | `detect_section` + `detect_field` both loop keywords | Single `_match_keywords(text, dict)` | parser |
| 2 | **Delete dead constants** | `WORKSPACE_ROOT = VAULT_ROOT`, `NO_CALENDAR_FLAG` | Removed, use `VAULT_ROOT` directly | handler |
| 3 | **Remove unused imports** | 8 imports from parser | 4 imports (only used ones) | handler |
| 4 | **Delete no-op functions** | `extract_update_text()` (just `.strip()`) | Kept but marked `# no-op, API compat` | parser |
| 5 | **Simplify title extraction** | Tokenize body, scan for `#` | Split lines, find first `#` | parser |
| 6 | **Inline obvious constants** | `now_time_str()` called nowhere | Deleted | handler |
| 6 | **Simplify conditional logic** | `if not show_all: pass` blocks | `if not show_all and status != "active": continue` | cli |
| 7 | **Remove dead code** | `if resolution: pass` in close_case | Deleted | cli |
| 8 | **Consolidate imports** | `import yaml` inside function | Top-level | cli |
| 9 | **Dead code elimination** | `if not show_all: pass` / `else: pass` | Removed | cli |

---

## Rule Applied
> **"If you delete it and tests still pass, it was dead code."**

All 30 tests pass after all simplifications.

---

## Pattern: Shared Helper for Near-Identical Functions
```python
# Before
def detect_section(text):
    for section, keywords in SECTION_KEYWORDS.items():
        if any(k in text.lower() for k in keywords): return section

def detect_field(text):
    for field, keywords in FIELD_KEYWORDS.items():
        if any(k in text.lower() for k in keywords): return field

# After
def _match_keywords(text, keyword_dict):
    normalized = text.strip().lower()
    for key, keywords in keyword_dict.items():
        if any(k in normalized for k in keywords):
            return key
    return None

def detect_section(text): return _match_keywords(text, SECTION_KEYWORDS)
def detect_field(text): return _match_keywords(text, FIELD_KEYWORDS)
```

---

## Pattern: Simplify Title Extraction
```python
# Before: Tokenize entire body, find # token, reconstruct from tokens
body_tokens = tokenize(body)
for idx, token in enumerate(body_tokens):
    if token.startswith("#") and idx + 1 < len(body_tokens):
        title = " ".join(body_tokens[: idx + 3])
        break

# After: Direct line iteration
for line in body.splitlines():
    if line.strip().startswith("#"):
        title = line.strip().lstrip("# ")
        break
```

---

## Pattern: Remove Alias Constants
**Before:** `WORKSPACE_ROOT = VAULT_ROOT` — used once in one function
**After:** Inline `VAULT_ROOT` directly, delete alias

---

## Verification
> **"If you delete it and tests still pass, it was dead code."**

All 30 tests pass after all simplifications:
- 8 orchestrator + 8 NL + 7 vault_resolver + 6 smoke = 30/30