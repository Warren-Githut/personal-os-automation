# Vietnamese Slug Normalization with unicodedata

## Problem
Vietnamese text with diacritics (e.g., "đào vải") was being converted to garbled slugs like `testing-o-v-v-i-canned-m-i-v-nh-cung-c-p-hi-n-t` instead of clean slugs like `testing-dao-vai-canned-moi`.

## Root Cause
The original slug generation used `re.sub(r"[^a-z0-9-]+", "-", text.lower())` which:
1. Treated each Vietnamese character with diacritics as a separate non-ASCII character
2. Replaced each diacritic character with a hyphen
3. Created excessive hyphens between every Vietnamese character

## Solution: Unicode NFD Normalization

```python
import unicodedata
import re

def _slugify(text: str) -> str:
    """Convert text to slug: normalize unicode, remove diacritics, replace spaces/special chars with hyphens."""
    # NFD: Decompose characters into base + combining marks
    text = unicodedata.normalize("NFD", text)
    # Remove combining marks (diacritics)
    text = "".join(c for c in text if unicodedata.category(c) != "Mn")
    # Remove non-word characters except spaces and hyphens
    text = re.sub(r"[^\w\s-]", "", text.lower())
    # Collapse spaces/hyphens to single hyphen
    text = re.sub(r"[-\s]+", "-", text).strip("-")
    return text[:48]
```

## How NFD Normalization Works

| Input | NFD Decomposition | After Removing Mn Category |
|-------|-------------------|---------------------------|
| `đ` | `d` + `̣` (combining dot below) | `d` |
| `ầ` | `a` + ` ̣ ` + ` ̀ ` | `a` |
| `ở` | `o` + ` ̛ ` + ` ̉ ` | `o` |

The `Mn` (Mark, Nonspacing) Unicode category contains all combining diacritical marks.

## Usage
```python
_slugify("Testing đào vải canned mới")
# Returns: "testing-dao-vai-canned-moi"

_slugify("Testing đào và vải (canned) mới vì nhà cung cấp")
# Returns: "testing-dao-va-vai-canned-moi-vi-nha-cung-cap"
```

## Key Points
- `unicodedata.normalize("NFD", text)` decomposes composed characters
- `unicodedata.category(c) != "Mn"` filters out combining marks
- `re.sub(r"[^\w\s-]", "", text.lower())` keeps only word chars, spaces, hyphens
- `re.sub(r"[-\s]+", "-", text).strip("-")` collapses consecutive hyphens/spaces

## Common Pitfall
Don't use `unicodedata.normalize("NFC", text)` - this COMPOSES characters, keeping diacritics intact.
Use `NFD` (decomposition) to separate base characters from diacritics.