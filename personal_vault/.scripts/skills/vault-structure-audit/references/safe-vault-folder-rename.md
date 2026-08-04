# Safe Vault Folder Rename — B1–B13 Checklist

> **Use when:** renaming any vault folder that has `[[wikilinks]]` pointing to/from it.
> **Principle:** Never rename before you know exactly what breaks.

## Why This Matters

Obsidian `[[wikilinks]]` use absolute paths from vault root. Renaming a folder like `customer_experience/` → `03_customer_experience/` breaks every link that references it — across all `.md` files in the vault, including archived content, cases, logs, and cross-references.

One rename can break **90+ links across 47+ files** (as was the case in Warren's wiki/ folder, 2026-07-01).

---

## Pre-Flight Scan (B1–B5)

Run these **before any rename**. Batch as many searches as possible in parallel.

### B1 — Scan all wikilinks to the old folder

```bash
# In the vault root, search for wikilinks containing the old folder name
grep -rn '\[\[customer_experience/' . --include='*.md'
grep -rn '\[\[P&L_Budget/' . --include='*.md'      # & in path OK in grep
```

Record affected files in a list.

### B2 — Scan all plain-text path references

Wikilinks aren't the only thing that breaks. Plain-text paths in `CONTEXT.md`, `SOUL.md` (RULES.md deprecated), SOUL files, and table cells in indexes also need updating.

```bash
grep -rn 'customer_experience/' . --include='*.md'
grep -rn 'P&L_Budget/' . --include='*.md'
```

Also check for **relative paths** like `../customer_experience/` or `../../customer_experience/`.

### B3 — Check WIKI_INDEX.md path columns

The `file` column in WIKI_INDEX.md tables contains paths like `customer_experience/...`. Every row for the renamed folder needs updating.

### B4 — Check CONTEXT.md

CONTEXT.md §3 (Vault Architecture) and §4 (Data Cadence) often contain plain-text path references to specific wiki subfolders. Search for `wiki/P&L_Budget/`, `wiki/menu_cogs/`, etc.

### B5 — Check vault root files

Search `SOUL.md`, `SOUL.md` (deprecated RULES.md), `AGENTS.md` for any path references that include the folder being renamed.

> **Warren's vault result (2026-07-01):** SOUL.md, SOUL.md (deprecated RULES.md), AGENTS.md only referenced `wiki/` (no subfolder paths) — no changes needed.

---

## Impact Summary Table

After B1–B5, compile an impact summary:

| Folder | Wikilinks broken | Files affected | External refs |
|--------|:-:|:-:|:-:|
| `customer_experience` | ~18 | ~8 | 1 (CONTEXT.md) |
| `lusine_operations` | ~18 | ~8 | 1 (CONTEXT.md) |
| ... | ... | ... | ... |

This lets you decide whether the rename is worth the fix cost.

---

## Execute (B6–B7)

### B6 — Git commit BEFORE renaming

```bash
cd /path/to/vault
git add -A
git commit -m "pre-rename snapshot: before renaming <folder>"
```

This gives you a one-command revert (`git reset --hard HEAD~1`).

### B7 — Rename the folder

```bash
mv "old_name/" "01_new_name/"
```

> **Windows/MSYS note:** Use `mv` (not `git mv`). `mv` works for folders with `&` in names. Then `git add -A` stages the rename. If `mv` fails with "Device or resource busy", retry immediately — Windows API caching resolves on second attempt.

---

## Post-Rename Fix (B8–B11)

### Strategy: Prefer `patch` tool over `sed` for individual file edits

On Windows/MSYS, the `patch` tool with `replace_all=True` is **safer than `sed`** for wikilink replacements:

| Aspect | `patch` with replace_all | `sed` |
|--------|------------------------|-------|
| `&` in names | ✅ Handles natively | ❌ Needs escaping |
| MSYS path resolution | ✅ Uses absolute Windows paths | ❌ `/c/` prefix issues in some contexts |
| Safety | ✅ Fuzzy matching, shows diff | ✅ Bulk but silent |
| Bulk (50+ files) | ❌ Each file = 1 tool call | ✅ One command |

**Use `patch` for individual files** (5-20 files). **Use `sed` for bulk sweeps** (50+ files across the vault).

### B8 — Update all wikilinks

For each affected file from B1, use `patch` with `old_string="[[old_name/"` and `new_string="[[01_new_name/"`:

```python
from hermes_tools import patch
patch(path="/path/to/file.md",
      old_string="[[customer_experience/",
      new_string="[[03_customer_experience/",
      replace_all=True)
```

**Parallel batching:** When fixing many files simultaneously, use independent `patch` calls — the runtime executes them concurrently.

**Verify:**
```bash
grep -rn '\[\[old_name/' --include='*.md' | grep -v '01_new_name'
# → should return zero
```

### B9 — Update all plain-text path references

Same approach as B8 but without `[[` brackets:

```python
patch(path="/path/to/file.md",
      old_string="old_name/",
      new_string="01_new_name/",
      replace_all=True)
```

**⚠️ Important:** Plain-text paths may appear in:
- `scope:` frontmatter fields (e.g. `scope: "30_KNOWLEDGE_BASE/wiki/SOP_POLICY_LUSINE/SOP/"`)
- `related:` frontmatter arrays (e.g. `related: ["customer_experience/customer_experience_Hub.md"]`)
- Table cells in INDEX files
- Backtick-enclosed paths in SOPs and guides: `` `wiki/customer_experience/` ``

**Verify:**
```bash
grep -rn 'old_name/' --include='*.md' | grep -v '01_new_name\|^Binary'
# → should return zero
```

### B10 — Update WIKI_INDEX.md

1. Replace `old_name/` → `01_new_name/` in all table `file` column entries
2. Update the section heading: `## old_name` → `## XX. old_name`

**Tip:** Do WIKI_INDEX.md after the B8+B9 sweep so remaining unfixed entries are obvious.

### B12 — Update documentation files (SOUL.md, CONTEXT.md, SOUL.compact.md)

After all folder links are fixed, update the **descriptive documentation** — these files describe vault structure but don't contain direct folder paths that break:

| File | What to check |
|------|---------------|
| `SOUL.md §3 — Vault Structure` | Folder paths, INDEX mentions, `_inbox/index` + `_journal/index`, `_cases/projects/`, memory file name |
| `SOUL.md — Key Files table` | `ACTIVE_CASES_INDEX.md` → `CASES_INDEX.md`, any renamed index paths |
| `SOUL.md — Memory System (§2)` | `_inbox/memory_raw.md` → `_inbox/warren_memory_raw.md` (typically 8+ references) |
| `SOUL.compact.md` | Same checks as SOUL.md vault table + Key Files |
| `CONTEXT.md §3 — VAULT ARCHITECTURE` | Numbered subfolder description, INDEX file mentions, `00_WIKI_INDEX.md` + Where To Go |
| `CONTEXT.md §4 — Data Cadence` | Inflow path references like `wiki/menu_cogs/` → `wiki/08_menu_cogs/` |
| `RULES.md` / `AGENTS.md` | Only if they reference specific subfolder paths (usually they reference `wiki/` root only) |

**Verification:** Search for stale description patterns:
```bash
grep -rn "30_KNOWLEDGE_BASE/wiki/WIKI_INDEX" --include='*.md' . | grep -v ".archive/"
grep -rn "_inbox/memory_raw" --include='*.md' . | grep -v ".archive/"
grep -rn "ACTIVE_CASES_INDEX" --include='*.md' . | grep -v ".archive/"
# All three should return 0
```

**Real-world (Warren, 2026-07-01):** After 10-folder numbering + INDEX renames:
- SOUL.md had 8 `_inbox/memory_raw.md` → `_inbox/warren_memory_raw.md` needed
- SOUL.md Key Files said `ACTIVE_CASES_INDEX.md` (never existed — correct is `CASES_INDEX.md`)
- CONTEXT.md §3 said "Analysis, hub pages, store profiles" (no numbered structure mention)
- CONTEXT.md §4 had `wiki/menu_cogs/Recipe_Index.json` → `wiki/08_menu_cogs/Recipe_Index.json`

### B13 — Update CONTEXT.md §3 structure description specifically

CONTEXT.md §3 (Vault Architecture) is the human-facing vault map. It must describe the numbered structure:

```markdown
## 3. VAULT ARCHITECTURE - Where Things Live

| Path | What's Inside |
|---|---|---|
| | `00_CORE_LOGIC/` | Session essentials |
| `10_OPERATION_DATA/` | Rolling logs — index: `OPERATION_INDEX.md` |
| `30_KNOWLEDGE_BASE/wiki/` | 10 numbered subfolders (01–10) + `00_WIKI_INDEX.md` (Where To Go) |
| `30_KNOWLEDGE_BASE/raw/` | Read-only |
| `_cases/active/` | Active cases — index: `CASES_INDEX.md` |
| `_cases/closed/` | Closed case archive |
| `_cases/projects/` | Capital projects |
| `_inbox/` | Drop zone — index: `INDEX.md` |
| `_journal/` | Warren's journal — index: `INDEX.md` |
| `scripts/` | Utility scripts |

> **Navigation:** Hermes reads `00_WIKI_INDEX.md` first → "Where To Go" table → đi thẳng tới folder đúng.
```

### B11 — Run vault lint & verify

```bash
# Warren's vault: /ops-lint
# Manual check:
grep -rn '\[\[old_name/' --include='*.md' | grep -v '01_new_name'
# Should return zero
```

Also verify:
- All `[[wikilinks]]` resolve to existing files
- All index files have correct paths
- Frontmatter `scope:` fields match actual folder structure
- `last_updated` in WIKI_INDEX.md frontmatter is bumped

---

## Special Cases

### 1. Ampersand in folder name (`P&L_Budget`)

`patch` handles `&` natively — no escaping needed. You can use `replace_all=True` without issues.

### 2. Archive subfolders that mirror active names

If `archive/customer_experience/` exists and you rename `customer_experience/` → `03_customer_experience/`, you have two options:

**Option A (recommended):** Also rename the archive subfolder to match:
```bash
mv archive/customer_experience/ archive/03_customer_experience/
```
This keeps path consistency. The `replace_all` sweep in B9 will automatically convert `archive/customer_experience/` → `archive/03_customer_experience/` in wikilink content.

**Option B:** Leave archive subfolder as-is. Manually fix each reference to `archive/customer_experience/` — this is tedious and error-prone.

### 3. Internal `scope:` frontmatter fields

Files inside the renamed folder may have frontmatter like:
```yaml
scope: "30_KNOWLEDGE_BASE/wiki/SOP_POLICY_LUSINE/SOP/"
```

These are **plain-text path references** that must be updated. They don't break wikilinks but break metadata consistency. Run a separate B8-style sweep for these.

### 4. `_connections/` → `09_connections/` (underscore prefix)

When renaming underscore-prefixed folders (`_connections/`), the `replace_all` pattern `_connections/` → `09_connections/` works because the underscore is part of the literal string. No special handling needed.

### 6. Index file naming — `00_` prefix convention

Index files at wiki root (like `WIKI_INDEX.md`) are not folders, but they follow the same logic: **sort first for fastest agent retrieval**.

When restructuring a wiki with numbered folders (01_, 02_, ...), also rename the index file so it sorts BEFORE folder 01:

```bash
mv WIKI_INDEX.md 00_WIKI_INDEX.md
```

**What breaks:**
- `[[WIKI_INDEX]]` wikilinks (Obsidian search-by-name stops matching)
- Text references to `WIKI_INDEX.md` in SOUL.md, CONTEXT.md, RULES.md, AGENTS.md
- Ingest log entries: `wiki/WIKI_INDEX.md` → `wiki/00_WIKI_INDEX.md`

**Fix scope:**
```bash
grep -rn 'WIKI_INDEX' --include='*.md' /path/to/vault
grep -rn 'WIKI_INDEX' --include='*.md' /path/to/SOUL.md /path/to/root/*.md
```

**Same 3-layer verification applies:** wikilinks → plain paths → full-path refs.

**Why `00_` and not just keeping the original name:** When Hermes (or any AI) lists directory contents, files sort alphabetically. `00_WIKI_INDEX.md` appears before `01_P&L_Budget/`, making the index the FIRST thing the agent reads — exactly the right behavior for a map-first navigation pattern.

> **Applies to:** `WIKI_INDEX.md`, `index.md` (wiki root hub page), and any other root-level file that functions as a retrieval index.

---

## Batch Strategy: One-at-a-Time vs. Bulk

| Approach | When to use | Pros | Cons |
|----------|------------|------|------|
| **One folder at a time** | First time, small vault (< 5 folders) | Safer, easier to verify each step | Slow for 10+ folders |
| **Bulk rename then bulk fix** | Large restructuring (5+ folders) | Much faster (all `mv` + one sweep) | Must verify all at once |

**Real-world example (Warren's wiki/, 2026-07-01):**
- 10 folders renamed
- Approach: batched folders 1-3 individually (learning curve), then bulk-renamed folders 4-9 + archive in a single `mv` batch
- Total: ~90 wikilinks updated across ~50 files
- Time: ~2-3 hours for full operation including verification

### Bulk workflow

```bash
# Step 1: Rename all at once
mv folder_a/ 01_folder_a/
mv folder_b/ 02_folder_b/
mv folder_c/ 03_folder_c/
# ...

# Step 2: Fix all wikilinks — one patch per folder, per file
# Each patch uses replace_all=True with the distinctive [[oldname/ pattern
```

**The key insight:** `[[old_name/` is a distinctive enough pattern that `replace_all=true` across the entire vault won't double-replace files that already have `[[01_new_name/`.

---

## Numbering Convention (for wiki-style vaults)

When adding numbers, use a logical ordering:

```
01_Financials           # P&L, Budget
02_Policies             # SOPs, policies
03_Customer_Experience  # CX
04_Labour               # COL, hours, HR
05_LTO                  # LTO tracking
06_Operations           # Ops analysis
07_Marketing            # Growth, campaigns
08_Menu_COGS            # Menu, COGS
09_Connections          # Cross-domain hubs
10_Archive              # Old content
```

> **@wandermist's rule:** "Numbers don't have to be perfect as long as they're directional."

---

## Verification — 3-Layer Scan

After all fixes, run **3 verification passes** — each catches different breakage types:

### Layer 1: Wikilinks (`[[old_name/`)

```bash
grep -rn '\[\[old_name/' --include='*.md' . | grep -v 'XX_new_name'
# → 0 matches
```

This catches all Obsidian `[[wikilinks]]` that still reference the old folder path. These are the HIGHEST impact because they produce broken-link indicators in Obsidian and silent dead-ends for AI retrieval.

### Layer 2: Plain-text path references (`old_name/`)

```bash
grep -rn 'old_name/' --include='*.md' . | grep -v 'XX_new_name\|^Binary\|\.git'
# → 0 matches
```

This catches non-wikilink path references in:
- Frontmatter `related:` arrays: `related: ["customer_experience/Hub.md"]`
- Frontmatter `scope:` fields: `scope: "wiki/SOP_POLICY_LUSINE/SOP/"`
- Backtick-enclosed paths in SOP docs: `` `wiki/menu_cogs/Recipe_Index.json` ``
- CONTEXT.md data inflow tables: `wiki/P&L_Budget/`
- Ingest path descriptions in log files

These don't produce Obsidian broken links but **break AI navigation** — the agent reads a plain-text path and can't find the file.

### Layer 3: FULL-PATH wikilinks (`[[30_KNOWLEDGE_BASE/wiki/old_name/`)

```bash
grep -rn '\[\[30_KNOWLEDGE_BASE/wiki/old_name/' --include='*.md' .
# → 0 matches
```

Some files use **absolute wikilinks** instead of relative ones:
```markdown
[[30_KNOWLEDGE_BASE/wiki/lusine_operations/PL_LU3_2026|P&L LU3]]
```
These are rare but dangerous — they bypass the normal wikilink resolution and break silently. Policy files and SOPs are the most common source.

### Layer 4 (Archive subfolders): grep with `-v` exclusion

```bash
# For folders that ALSO have archive subfolder copies:
grep -rn '\[\[old_name/' --include='*.md' . | grep -v 'XX_new_name\|10_archive'
# → should only show files in 10_archive/ (expected, not broken)
```

Archive files (`10_archive/`) may still reference old active-folder names if you chose to leave them. Confirm these are intentional.

### Checklist

- [ ] Layer 1 (wikilinks): `grep -rn '\[\[old_name/'` → 0 external matches
- [ ] Layer 2 (plain paths): `grep -rn 'old_name/'` → 0 external matches (except archive)
- [ ] Layer 3 (full-path wikilinks): `grep -rn '\[\[30_KNOWLEDGE_BASE/wiki/old_name/'` → 0 matches
- [ ] WIKI_INDEX.md section headings have numbers: `## XX. name`
- [ ] WIKI_INDEX.md `last_updated` bumped
- [ ] CONTEXT.md §3 and §4 references updated
- [ ] `git status` shows folder rename + file content changes (not just folder rename)
- [ ] Git commit message includes all renamed folders

---

## Risks & Pitfalls

| Risk | Mitigation |
|------|-----------|
| **Ampersand in folder name** (`P&L_Budget`) — breaks `sed` patterns | Use `patch` tool with literal `&`. Avoid `sed` for `&` paths. |
| **Archive subfolder same name as active** — need to rename both | Use Option A (rename archive subfolder too). Global replace handles both. |
| **Cross-vault references** — cases, logs, CONTEXT.md, SOUL.md | B2 scan catches these. |
| **`scope:` frontmatter fields inside renamed folder** — silent metadata breakage | Run separate B8 sweep for scope patterns. |
| **`mv "Device or resource busy"` on Windows** | Retry immediately — API caching resolves on second attempt. |
| **Archive subfolders inside renamed archive** (`10_archive/lusine_operations/`) | Already renamed when archive was bulk-moved. No extra action needed. |
| **`replace_all` doubles content** (e.g., `04_labour_costs` → `04_04_labour_costs`) | Only happens if old_string is a substring of new_string. Use distinctive prefix patterns like `[[oldname/` to avoid. |
| **Commit before rename is essential** | Without it, reverting 90+ link fixes is impractical |
| **`patch` with `---` separator matches too broadly in table-heavy files** | When patching near section separators (`---`), use the full section heading + at least 1 unique body line as context. Example: use `## Update Protocol` + `- Append newest entries` as old_string, not just `---` + `## Update Protocol`. Test uniqueness with `old_string` first. |

---

## One-Folder-at-a-Time Strategy

Do NOT batch-rename 10 folders at once. Do:

1. Rename folder 1 → fix all links → verify → commit
2. Rename folder 2 → fix all links → verify → commit
3. ...repeat

Per-folder time: ~15-30 minutes (including scans and link fixes).
Total for 10 folders: spread across 3+ sessions to avoid fatigue and mistakes.

> **Exception:** If folders are totally independent (no overlapping content), you can batch-rename non-interfering folders. Verify per-folder link integrity after the batch.