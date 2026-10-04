---
name: "Vault File Rename & Cross-Reference Patching"
description: "Safe rename of any vault file — rename, find all references across vault + profile + skills, patch precisely, deep-verify."
version: "1.0"
---

# Vault File Rename & Cross-Reference Patching

Use when renaming a vault file (`.md`, `.py`, `.json`, `.yaml`) that has references scattered across the vault, profile configs, and skill files.

## Procedure

### Step 1: Rename the file
```bash
mv <old_name>.md <new_name>.md
```

### Step 2: Find ALL references (every file type, both dirs)
Scan vault AND profile. Exclude data dirs (`cache/`, `sessions/`, `sandboxes/`, `state-snapshots/`, `snapshots/`, `logs/`, `storage/`, `workspace/`, `audio_cache/`, `image_cache/`, `bin/`, `lsp/`, `pairing/`, `plans/`, `gateway-service/`, `home/`, `hooks/`, `templates/`, `skins/`).

Exclude binary extensions: `.pyc`, `.exe`, `.dll`, `.png`, `.jpg`, `.db`, **`.db-wal`**, **`.db-shm`**, `.sqlite`, `.zip`, `.pdf`, etc.

**Critical:** SQLite WAL files (`.db-wal`, `.db-shm`) contain raw conversation fragments — always exclude them from text scans.

### Step 3: Patch references — AVOID `replace_all` on path strings

**🚫 DON'T** — This causes double prefixes and cross-profile corruption:
```python
# replace_all with old_string="_inbox/memory_raw.md"
# → "vault/_inbox/memory_raw.md" becomes "vault/vault/_inbox/..."
# → "_stock_profile_memory_raw.md" becomes "_stock_profile_warren_memory_raw.md"
```

**✅ DO** — Replace the EXACT filename only:
```python
# Replace "memory_raw.md" → "warren_memory_raw.md" (filename, not path)
# Or use a regex negative lookbehind to exclude already-prefixed versions:
import re
stale = re.compile(r'(?<!warren_)memory_raw\.md')
```

**✅ DO** — For pre-prefixed paths, replace the full path atomically:
```
"_inbox/memory_raw.md"  → "_inbox/warren_memory_raw.md"
"vault/_inbox/memory_raw.md"  → "vault/_inbox/warren_memory_raw.md"
```

### Step 4: Deep verification (single-pass)

Write a script that walks both VAULT and PROFILE once:

| Check | What to verify |
|-------|----------------|
| OLD_FILE_GONE | Old name no longer exists |
| NEW_FILE_EXISTS | New name exists |
| STALE_VAULT | 0 stale refs in vault (bare `old_name` not preceded by prefix) |
| STALE_PROFILE | 0 stale refs in profile (same) |
| DOUBLE_PREFIX | 0 `vault/vault/` introduced by rename (filter pre-existing bugs) |
| SYNC_COPY | If sync copy exists, check it |
| NEW_FILE_CONTENT | Header correct |

**Filter known-legitimate patterns (do NOT flag as stale):**
- Other profiles' raw logs: `_stock_profile_memory_raw.md`, `_personal_memory_raw.md`, `_<profile>_memory_raw.md`
- Pre-existing documented bugs (e.g., `VAULT_ROOT` double-`vault/` path docs)

## Common Pitfalls

1. **`replace_all` on path substrings** — Always replace the full filename component, not a path segment. Prefer regex negative lookbehind.

2. **SQLite WAL false positives** — `.db-wal` files in `sessions/` contain conversation fragments where you *thought about* the old filename. Add `.db-wal`/`.db-shm` to binary exclusions.

3. **Cross-profile contamination** — Other profiles may use the same generic filename. The rename is profile-specific. Other profiles' equivalents must stay unchanged.

4. **Double `vault/vault/` prefix** — Scan for `vault/vault/` after any path replacement. Fix immediately.

5. **Archives are read-only** — `_archives/memory/*.md` contain historical refs to the old name. Do NOT patch them.
