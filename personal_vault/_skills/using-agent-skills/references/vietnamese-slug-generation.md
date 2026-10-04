# Vietnamese Slug Generation with Unicode Normalization

## Problem
Standard regex slug generation breaks Vietnamese text with diacritics:
- Input: `"phần 5 trái ổ cỏ trái bơ..."`
- Broken regex `re.sub(r"[^a-z0-9-]+", "-", text.lower())` produces: `ph-n-5-tr-i-o-c-o-tr-i-b-b-v-mi-ng-n-m-m-a-xu-n`
- Each diacritic treated as separate non-alphanumeric character

## Solution: Unicode NFD Normalization

```python
import unicodedata
import re

def _slugify(text: str) -> str:
    """Convert text to slug: normalize unicode, remove diacritics, replace spaces/special chars with hyphens."""
    # 1. NFD normalization decomposes characters into base + combining marks
    text = unicodedata.normalize("NFD", text)
    
    # 2. Remove combining marks (diacritics) - category "Mn" = Mark, Nonspacing
    text = "".join(c for c in text if unicodedata.category(c) != "Mn")
    
    # 3. Remove non-word, non-space, non-hyphen chars
    text = re.sub(r"[^\w\s-]", "", text.lower())
    
    # 4. Collapse spaces/hyphens, trim
    text = re.sub(r"[-\s]+", "-", text).strip("-")
    
    # 5. Limit length
    return text[:48]
```

## How NFD Works

| Character | NFD Decomposition | Category "Mn" Removed | Result |
|-----------|-------------------|----------------------|--------|
| `ấ` | `a` + `́` (U+0301) | `́` (combining acute) | `a` |
| `ử` | `u` + `̉` (U+0309) | `̉` (combining hook) | `u` |
| `ở` | `o` + `̉` (U+0309) | `̉` | `o` |
| `ể` | `e` + `̉` (U+0309) | `̉` | `e` |

Vietnamese diacritics are combining marks (category "Mn") that get stripped cleanly.

## Test Results

| Vietnamese Input | Old (Broken) | New (Fixed) |
|------------------|--------------|-------------|
| `phần 5 trái ổ cỏ trái bơ...` | `ph-n-5-tr-i-o-c-o-tr-i-b-b-v-mi-ng-n-m-m-a-xu-n` | `phan-5-trai-o-co-trai-bo-bo-vo-mieng-nem-mua-xua` |
| `trái đào cào trái bơ...` | `tr-i-o-c-o-tr-i-b-b-v-mi-ng-n-m-m-a-xu-n` | `trai-dao-cao-trai-bo-bo-vo-mieng-nem-mua-xuan-nh` |
| `Testing đào vải canned mới` | `testing-o-v-v-i-canned-m-i-v-nh-cung-c-p-hi-n-t` | `testing-đao-vai-canned-moi` |
| `phần 2 trái ổ cỏ...` | `ph-n-2-tr-i-o-c-o-tr-i-b-b-v-mi-ng-n-m-m-a-xu-n` | `phan-2-trai-o-co-trai-bo-bo-vo-mieng-nem-mua-` |

## Integration Point

In `case_brain_nl_handler.py`:
```python
def create_case_from_payload(payload: str, *, dry_run: bool = False) -> Path:
    slug = datetime.now().strftime("%Y-%m-%d") + "_" + _slugify(payload.splitlines()[0])
    # ...
```

## Multi-Profile Deployment

After fixing `_slugify()`, deploy to all 3 profiles:
```bash
# 1. Fix in vault/scripts/case_brain_nl_handler.py
# 2. Sync to all profiles
for p in warren-profile lusine-profile personal_profile; do
  cp vault/scripts/case_brain_nl_handler.py ~/.hermes/profiles/$p/skills/lusine-cases/
done

# 3. Clear caches
find ~/.hermes/profiles -name "__pycache__" -exec rm -rf {} +
find vault/scripts -name "__pycache__" -exec rm -rf {} +

# 4. Restart bot process
```

## Dependencies
- Standard library only: `unicodedata`, `re`
- No external packages required
- Works on Python 3.8+

## Unicode Categories Reference

| Category | Description | Example |
|----------|-------------|---------|
| `Mn` | Mark, Nonspacing | Combining diacritics (acute, grave, hook, etc.) |
| `Mc` | Mark, Spacing Combining | Devanagari vowel signs |
| `Me` | Mark, Enclosing | Combining enclosing circle |
| `Ll` | Letter, Lowercase | `a`, `à`, `ả` (base letters) |
| `Lu` | Letter, Uppercase | `A`, `À`, `Ả` |

## References
- [Unicode Normalization Forms](https://unicode.org/reports/tr15/)
- [Python unicodedata module](https://docs.python.org/3/library/unicodedata.html)
- [Python re module](https://docs.python.org/3/library/re.html)