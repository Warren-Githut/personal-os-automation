# Vault File Rename → Repoint ALL Stale Refs (docs + code paths)

## When this applies
Warren renames a vault markdown/log file (e.g. `01_Weekly_Revenue_Log.md` →
`01_SSOT_01_Weekly_Revenue_Log.md`). Every other file that referenced the old
path/name must be repointed, OR it goes stale (broken wikilink, or — worse —
a parser/script that hardcodes the old path crashes the next Monday pipeline).

This is the SAME integrity concern as Phase 0G skill-rename, but for **vault
files**. Do it whenever a rename is committed.

## 🔴 THE TRAP: new name CONTAINS old name as substring
`01_SSOT_01_Weekly_Revenue_Log.md` literally contains `01_Weekly_Revenue_Log.md`.
A naive `str.replace(OLD, NEW)` produces `01_SSOT_01_SSOT_01_Weekly_Revenue_Log.md`
(double-substitution). Every naive sweep that replaces OLD→NEW, or that
regex-replaces `01_Weekly_Revenue_Log` without guarding, double-substitutes.

### Detector pitfalls (learned the hard way 2026-07-13)
- **`(?<!\01_SSOT_)01_Weekly_Revenue_Log` negative lookbehind FAILS at string
  start** — when the old name is at line start with no preceding chars, the
  lookbehind has nothing to match and the negative assertion passes → FALSE
  POSITIVE (reports already-correct `01_SSOT_01_...` lines as stale).
- **Wrong offset** — the guard prefix `01_SSOT_` is **8 chars**, not 12.
  Checking `line[max(0,j-12):j]` misses the boundary and still false-positives.
  Use `line[max(0,j-8):j] == '01_SSOT_'`.

### ✅ WORKING DETECTOR (char-scan, prefix guard)
```python
import os
ROOT = r'C:\Users\khoans\Documents\Warren_OS_Local\vault'
OLD = '01_Weekly_Revenue_Log.md'
PREFIX = '01_SSOT_'   # 8 chars immediately before OLD => part of NEW name
seen = set(); stale = []
for dp, dn, fn in os.walk(ROOT):
    parts = dp.split(os.sep)
    if any(p.startswith('.') or p in ('_archives','.git','node_modules') for p in parts):
        continue
    for f in fn:
        if not f.endswith(('.md','.py','.json','.html','.yaml','.yml')):
            continue
        p = os.path.join(dp, f)
        try:
            lines = open(p, encoding='utf-8', errors='replace').read().splitlines()
        except Exception:
            continue
        for i, line in enumerate(lines, 1):
            start = 0
            while True:
                j = line.find(OLD, start)
                if j == -1:
                    break
                if line[max(0, j-8):j] == PREFIX:   # already the NEW name
                    start = j + 1
                    continue
                key = (p, i, line.strip()[:140])
                if key not in seen:
                    seen.add(key)
                    stale.append(key)
                start = j + 1
print("GENUINE STALE:", len(stale))
for x in stale:
    print("  ", x)
```

### ✅ WORKING APPLIER (bulk replace, prefix-guarded, idempotent)
```python
import os
ROOT = r'C:\Users\khoans\Documents\Warren_OS_Local\vault'
OLD = '01_Weekly_Revenue_Log.md'
NEW = '01_SSOT_01_Weekly_Revenue_Log.md'
PREFIX = '01_SSOT_'
DRY = os.environ.get('APPLY') != '1'     # run with APPLY=1 to mutate
changed = []
for dp, dn, fn in os.walk(ROOT):
    parts = dp.split(os.sep)
    if any(p.startswith('.') or p in ('_archives','.git','node_modules') for p in parts):
        continue
    for f in fn:
        if not f.endswith(('.md','.py','.json','.html','.yaml','.yml')):
            continue
        p = os.path.join(dp, f)
        try:
            raw = open(p, encoding='utf-8', errors='replace').read()
        except Exception:
            continue
        if OLD not in raw:
            continue
        out = []
        for line in raw.splitlines(keepends=True):
            nl = line
            start = 0
            while True:
                j = nl.find(OLD, start)
                if j == -1:
                    break
                if nl[max(0, j-8):j] == PREFIX:   # skip NEW-name occurrences
                    start = j + 1
                    continue
                nl = nl[:j] + NEW + nl[j+len(OLD):]
                start = j + len(NEW)
            out.append(nl)
        new_raw = ''.join(out)
        if new_raw != raw:
            changed.append(os.path.relpath(p, ROOT))
            if not DRY:
                open(p, 'w', encoding='utf-8').write(new_raw)
            print(('[DRY] ' if DRY else '[APPLIED] ') + os.path.relpath(p, ROOT))
print("Total files changed:", len(changed))
```
- **Dry-run first** (no `APPLY` env) to eyeball the file list.
- **Apply** with `APPLY=1 python3 <script>`.
- **Idempotent**: re-running finds 0 stale → 0 changes.

## 🔴 THOROUGHNESS RULE (Warren: "sửa cho triệt để")
Scan BOTH:
1. **Docs** (`.md` wikilinks, markdown path refs, `00_OPERATION_INDEX.md`,
   `00_DASHBOARDS.md`, `CONTEXT.md`, `ONTOLOGY.md`, case files, `_inbox/` specs).
2. **CODE PATHS** — `parsers/*.py` and `scripts/*.py` that HARDCODE the old
   path as a variable (`revlog_path = .../"01_Weekly_Revenue_Log.md"`,
   `REVENUE_LOG_FILE = ...`, `LOG01 = ...`, `read_vault_file("01_Weekly_Revenue_Log.md")`).
   A stale code path does NOT show as a broken link — it crashes the next
   Monday pipeline with `FileNotFoundError`. The 2026-07-13 rename left 14
   stale refs in parsers/scripts; docs were already clean.

## ✅ VERIFY before commit (mandatory gate)
1. **Re-run detector → expect 0 genuine stale.**
2. `python3 -m py_compile <every touched .py>` — no syntax break.
3. `grep` the NEW name in the 4 critical path-variable lines to confirm repoint:
   `col_weekly_parser.py`, `hourly_cover_parser.py`, `google_review_parser.py`,
   `item_sales_parser.py` (and any other script that read the old file).
4. Commit once: rename + delete-old + all repoints + the Monday pipeline sync.

## Real example (2026-07-13)
`01_Weekly_Revenue_Log.md` → `01_SSOT_01_Weekly_Revenue_Log.md`.
23 genuine stale refs (14 in parsers/scripts + 9 already-clean docs).
Fixed 15 files (8 parsers + 7 scripts). Verify: 0 stale, all py compile,
4 critical path vars repointed. Committed with the Monday parser sync.
