# Phantom File Bulk Cleanup

> Technique developed 2026-07-01 during Warren's vault stress test.
> Detected: `Store_Roadmap_2026–2027.md` — listed in `00_WIKI_INDEX.md` for months, **never created on disk**. 36 `[[wikilinks]]` across the wiki pointed to it.

---

## Detection

### During stress test
A stress test task ("Find store roadmap 2026-2027") fails with `File not found`. The file is referenced in `00_WIKI_INDEX.md` and 36 other files. Cross-check:

```bash
# 1. Check git history — was it ever committed?
git log --all --oneline -- "*/Store_Roadmap*"

# 2. Search disk
find . -name "*Store_Roadmap*" 2>/dev/null

# 3. Check all references
grep -rn "Store_Roadmap" --include="*.md" .
```

If git history is empty AND the file doesn't exist on disk → **phantom file**.

### During index scan
Phase 1F of vault-structure-audit runs `test -f` for every INDEX path reference. Any path returning missing is a phantom.

---

## Bulk Cleanup Strategy

### Step 1 — Categorize reference patterns

From `grep -rn "PhantomName" --include="*.md" .`:

| Pattern | Count | Example |
|---------|:-----:|---------|
| `- [[PhantomName]]` (standalone list item) | 30+ | In "Related" sections at file bottoms |
| `\| [[PhantomName]] \|` (table cell) | 1-2 | In inline See-also tables |
| `"PhantomName.md"` (frontmatter `related:` array) | 1-3 | In YAML frontmatter |
| `[[30_KNOWLEDGE_BASE/wiki/old_folder/PhantomName\|display]]` (full-path wikilink) | Rare | In policy/SOP files |
| INDEX table row | 1 | `00_WIKI_INDEX.md` or similar |

### Step 2 — Bulk delete simple patterns with `sed`

For the majority `- [[PhantomName]]` pattern across 30+ files:

```bash
cd vault/30_KNOWLEDGE_BASE/wiki
grep -rln "PhantomName" --include="*.md" . | grep -v ".archive/" | \
  grep -v "EXCLUDE_FILE" | \
  while read f; do sed -i '/PhantomName/d' "$f"; done
```

**⚠️ WARNING:** `sed -i '/PhantomName/d'` deletes EVERY LINE containing the string. This is correct for standalone list items but WRONG for:
- Frontmatter `related:` arrays (deletes the entire YAML line → data loss)
- Inline wikilinks in body text (deletes the entire sentence/line)
- INDEX table rows (deletes the row → INDEX needs re-counting)

**Always exclude files with complex patterns** from the sed bulk pass:

```bash
# Exclude files with frontmatter or inline references
grep -v "WIKI_INDEX\|EBITDA_Strategy\|CAPEX\|PL_LU5\|PL_LU7"
```

### Step 3 — Handle complex patterns individually with `patch`

#### Frontmatter `related:` array

```patch
old: related: ["FileA.md", "PhantomName.md", "FileB.md"]
new: related: ["FileA.md", "FileB.md"]
```

⚠️ Watch for `Escape-drift` — use the exact string from the file, not backslash-escaped.

#### Inline wikilink in body text

```patch
old: See also: [[FileA]] | [[PhantomName]] | [[FileB]]
new: See also: [[FileA]] | [[FileB]]
```

#### INDEX table row

```patch
old: | `folder/PhantomName.md` | 2026-05 | strategy | description | 2026-05-11 |
new: (delete entire line)
```

Update `total_files` frontmatter in the INDEX.

### Step 4 — Verify

```bash
grep -rn "PhantomName" --include="*.md" . | grep -v ".archive/"
# Expected: 0
```

---

## Real Example: Store_Roadmap_2026–2027

| Metric | Value |
|--------|-------|
| Files with references | 40 (29 wiki + 4 ops + 5 archive + INDEX + backup) |
| Total wikilinks removed | ~36 |
| SED bulk pass | 29 files, ~10 seconds |
| Complex fixes | 5 files (frontmatter + inline) |
| INDEX cleanup | 00_WIKI_INDEX.md (row + total_files: 23→22) |
| Total time | ~3 minutes |

### Files excluded from sed bulk:
- `00_WIKI_INDEX.md` — table row + total_files frontmatter
- `EBITDA_Strategy_to_10pct.md` — `related:` frontmatter + inline wikilink
- `Lusine_CAPEX_LU7_vs_LU8_Comparison_July2024.md` — `related:` frontmatter
- `PL_LU5_2026.md` — inline See-also text
- `PL_LU7_2026.md` — inline See-also text

### Lessons learned

1. **Phantom files accumulate silently** — the file was listed in the INDEX for ~6 weeks before detection. INDEX auto-audit (Phase 1F) should flag any INDEX path where `test -f` returns false.
2. **CASES_INDEX is also vulnerable** — real case found in this sweep: `2026-06-26_vespa-o-lu3-qua-lu5-da-gui-mail-cho-bod-vespa-da` had an index entry but no file.
3. **`sed -i` with exclusion is faster than individual `patch`** for bulk (30+ files). But `patch` is safer for complex patterns — use both in combination.
4. **Em dash in filename** (U+2013 vs regular hyphen) is a common source of phantom files — the file was `Store_Roadmap_2026–2027` with an em dash, which may have been invisible to users scanning visually.
