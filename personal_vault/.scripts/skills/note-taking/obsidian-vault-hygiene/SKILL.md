---
name: obsidian-vault-hygiene
description: Hide system/junk folders and files from Obsidian's file explorer for Warren's vault using `.obsidian/app.json` `userIgnoreFilters`. Covers Obsidian's EXACT regex matching logic (reverse-engineered from obsidian.asar), mandatory verification via reproduced regex, re-index pitfalls, and the dotfolder-rename fallback when filters don't hide folder containers. Use when Warren complains the vault looks cluttered or wants system folders (scripts/, parsers/, tmp/, *.csv, *.json) hidden.
version: 1.0.0
tags: [obsidian, vault, hygiene, userIgnoreFilters, cleanup, warren, non-it]
---

# obsidian-vault-hygiene

## Purpose
Warren is non-IT. Obsidian's file explorer showing `scripts/`, `parsers/`, `_accumulation/`, `*.csv`, `*.json` etc. makes the vault look cluttered ("nhìn rối quá"). Hide them so only operational data (`.md` logs + index) shows.

## When to use
- Warren: "sao Obsidian hiện mấy cái này", "nhìn rối quá", "ẩn hoặc xóa được ko"
- After adding new system folders/files to the vault that shouldn't be visible

## ⚠️ CRITICAL FINDING (2026-07-15, confirmed via liteparse on Obsidian UI screenshot)
**Obsidian `userIgnoreFilters` (Settings → Files & Links → "Excluded files") does NOT hide anything from the FILE EXPLORER tree.** It only hides from **Search, Graph View, Unlinked Mentions, and (less noticeably) Quick Switcher / link suggestions.** The Excluded-files UI literally states this. So if Warren says "vault rối, ẩn folder đi" → `userIgnoreFilters` ALONE will FAIL to clean the file pane. You will waste turns thinking the pattern is wrong.

**THE ONLY reliable way to hide from the file explorer tree is the `.dotfolder` convention** (rename folder to start with `.`). Obsidian auto-hides any `.folder`/`.file` from the tree on all platforms — no settings, no plugins.

**Recommended approach (proven 2026-07-15):**
1. **PRIMARY: rename junk folders to `.dotfolder`** (e.g. `parsers` → `.parsers`, `_accumulation` → `._accumulation`). This hides them from the file tree 100%.
2. **SECONDARY (optional, redundant):** keep `userIgnoreFilters` too — it additionally hides from Search/Graph. Not required.
3. **NEVER lead with userIgnoreFilters expecting tree-hiding** — it won't work, Warren will report "vẫn hiện".

### CSS-SNIPPET HIDE — non-destructive alternative (when rename breaks pipeline)
**Use case (2026-07-25):** Warren wanted to hide `30_KNOWLEDGE_BASE/wiki/dashboards/` from the explorer. But this folder is the **SSOT output of the dashboard pipeline** — 50+ hardcoded `file:///.../wiki/dashboards/...html` refs across `.py` scripts, parsers, tracking logs, and index files. A dotfolder rename would GÃY every script + link. `userIgnoreFilters` wouldn't hide the tree anyway. → **CSS snippet** is the right tool: hides the folder visually, file stays at the SAME path, pipeline untouched.

**Mechanism:** Obsidian renders the file explorer with `.nav-folder-title` elements carrying a `data-path` attribute = vault-relative path. A CSS snippet with `display:none` on the matching selector hides that ONE folder from the tree. It does NOT rename, does NOT touch `app.json`, does NOT affect search/graph/open-by-link.

**Steps:**
1. Create `vault/.obsidian/snippets/hide-dashboards.css` (any name; multiple snippets allowed).
2. Content (target the exact `data-path`; `data-type="file-explorer"` scopes it to the explorer pane only):
```css
/* Hide ONE folder from Obsidian File Explorer (non-destructive) */
.workspace-leaf-content[data-type="file-explorer"]
  .nav-folder-title[data-path="30_KNOWLEDGE_BASE/wiki/dashboards"] {
  display: none;
}
```
3. Enable: Obsidian → Settings → Appearance → CSS snippets → toggle on (Ctrl+P → "Reload app without saving" if it doesn't appear).
4. Verify: folder gone from tree; file still opens via `file:///` link; scripts still write to same path.

**Tradeoffs / pitfalls:**
- Snippet is per-vault (lives in `.obsidian/snippets/`). If Warren switches/duplicates vault, re-add.
- If `data-path` value is wrong (typo / wrong relative path), the folder stays visible silently — double-check the exact path Obsidian uses (vault-relative, forward slashes, NO leading `/`).
- Does NOT hide from Graph/Search — pair with `userIgnoreFilters` if Warren also wants those hidden (redundant but harmless).
- Fully reversible (toggle snippet off) — zone 🟡 (touches `.obsidian`, no data risk). Con may apply directly; Bố can revert in 1 click.
- **Preferred method when the target folder is referenced by hardcoded paths you must NOT break.** Reserve dotfolder rename for junk folders with no external refs.

**OPERATIONAL REFINEMENTS (verified 2026-07-25, live `wiki/dashboards` case):**
- **Detect refs BEFORE choosing method (operationalizes Decision-tree step 0).** Run a vault-wide grep across the 3 file classes that hold paths:
  ```bash
  grep -rIn --include="*.py" --include="*.md" --include="*.json" -E "wiki/dashboards|/dashboards/|dashboards/" . 2>/dev/null | grep -v node_modules | head -60
  ```
  If the count is **high (≳10 refs)** → CSS-snippet (do NOT rename). If near-zero → dotfolder rename is safe. For `wiki/dashboards` this returned **50+ refs** (scripts, parsers, tracking logs, index, `00_DASHBOARDS.md`) → CSS-snippet was mandatory.
- **Programmatic enable (no manual toggle).** Instead of telling Warren to flip Appearance → CSS snippets, ADD the snippet name to `app.json`'s `cssSnippets` array directly:
  ```json
  "cssSnippets": ["hide-dashboards"]
  ```
  This enables it on next Obsidian load — same effect as the UI toggle, but deterministic and git-trackable.
- **`appearance.json` REDUNDANCY PITFALL.** When Warren later toggles the snippet in the UI, Obsidian auto-writes `vault/.obsidian/appearance.json` adding `"hide-dashboards"` to `enabledCssSnippets`. This is **redundant** with `app.json cssSnippets` — the snippet runs either way. If you see `appearance.json` modified after enabling, it is harmless; you may `git rm` it (revert to HEAD) to keep the commit clean. Do NOT confuse it with a required file.
- **VALIDATE `app.json` after editing.** Always `python3 -c "import json; json.load(open('.obsidian/app.json')); print('OK')"` before commit — a stray comma breaks Obsidian silently.
- **Working selector (both forms valid).** The skill's example uses `.workspace-leaf-content[data-type="file-explorer"] .nav-folder-title[data-path="..."]`. A simpler equivalent also works and is what shipped live:
  ```css
  .nav-folder[data-path="30_KNOWLEDGE_BASE/wiki/dashboards"] { display: none !important; }
  ```
  `data-path` is vault-relative, forward slashes, **NO leading `/`**. Wrong path → folder silently stays visible (no error). Verify the exact path Obsidian uses.
- **`search_files` FALSE-NEGATIVE on this folder.** `search_files(target="files", pattern="*")` returned 0 for `wiki/dashboards` though `ls` showed 8 files — same false-negative pitfall as session-start. TRUST `terminal ls`/`grep`, never `search_files` empty-result, when confirming a folder's contents.

### Obsidian's EXACT matching logic (from obsidian.asar — for the optional filter)
Obsidian does NOT use plain .gitignore semantics. Reverse-engineered:
```js
o = filter.trim();
if (o.length > 2 && o.startsWith("/") && o.endsWith("/")) {
    n.push(new RegExp(o.substring(1, o.length-1), "i"));   // DIRECTORY: substring match, case-insensitive
} else {
    n.push(new RegExp("^.*" + escape(o) + ".*$", "i"));     // GLOB: wrapped, substring match
}
```
Implications:
- `/_accumulation/` → regex `/_accumulation/i` → matches ANY path containing `_accumulation` (substring, anywhere).
- `10_OPERATION_DATA/parsers` (no slashes) → regex `^.*10_OPERATION_DATA\/parsers.*$` → also matches. Both forms work.
- `*.csv` → `^.*\*.csv.*$` → matches any `.csv` anywhere.
- **Confirms: this only affects Search/Graph/Unlinked Mentions — NOT the file tree.** Hence dotfolder is primary.

### Step-by-step (DOTFOLDER-FIRST — proven working)
1. **Inventory** junk folders in `vault/` and `vault/10_OPERATION_DATA/` (e.g. `parsers`, `scripts`, `monthly`, `morning_briefs`, `01_Payroll`, `_accumulation`, `_inbox`, `_verify_tmp`, `_assets`, `_scripts_cron`, `_scripts_temp`, `_private`).
2. **Check hardcoded refs** BEFORE renaming: `grep -rn "10_OPERATION_DATA/parsers\|.../scripts\|.../monthly" --include=*.py vault/`. Obsidian's `Path(__file__).resolve().parent` survives rename (folder name changes, path follows), but **string literals** in 17+ `.py` files must be bulk-updated. Use a Python script: read each `.py`/`.md`/`.json`, `.replace(old, new)` for each mapping, write back. Verify zero leftovers with grep.
3. **Rename** (git mv for tracked, mv for empty dirs since git won't track empty):
   - `mv parsers .parsers` etc. (leading dot added)
   - Empty dirs can't `git mv` → plain `mv`.
4. **Bulk-update refs** (Python script, NOT sed). Map: `10_OPERATION_DATA/parsers` → `10_OPERATION_DATA/.parsers`, etc. Extend to `.md`/`.json` (CONTEXT.md, WARREN_MEMORY.md, Log files, app.json, plugin data.json).
5. **`__pycache__` prevention** (critical if any renamed folder holds `.py` scripts that get run): Python regenerates `__pycache__/` (non-dot) after rename → reappears in tree. Fix:
   - Add `import sys; sys.dont_write_bytecode = True` after shebang in each run script (verified: clean run no longer regens).
   - Add `vault/<folder>/.gitignore` with `__pycache__/` + `*.pyc` as backstop.
6. **Verify** via script (below) + tell Warren to **reload Obsidian** (Ctrl+P → Reload app without saving). Dotfolders disappear from tree immediately.
7. **Commit** `git add -A` (catches renames + new dotfolders), `git -c gc.auto=0 commit` (avoid auto-gc timeout on Windows).

### Verification (MANDATORY)
Run `scripts/verify_obsidian_ignore.py` — but since dotfolder is the mechanism now, the real check is: **`ls` the parent dir → dotfolders present, old names GONE; grep vault-wide for old path strings → 0 matches; run a renamed parser → still imports + resolves paths**. Also confirm no `__pycache__` regen after a script run.

### Liteparse-as-UI-verification technique (2026-07-15)
If Warren pastes an Obsidian screenshot and vision_analyze fails (provider 402 / no vision), **use liteparse** (mandatory per SOUL §3.1) to OCR the UI text. This is how we READ the Excluded-files UI and confirmed it only hides Search/Graph — the screenshot told us the truth vision couldn't. Always liteparse screenshots from Warren; don't assume vision.

### Obsidian TABLE-RENDER FAILURE — MULTI-LAYER (2026-07-20, battle-tested, EXTENDED)
**Symptom Warren reports:** a markdown table shows raw `|||` pipes (won't render); table looks "broken". He may say *"bị lỗi ko hiển thị bảng, vì |||"* or *"vẫn toàn hiện ||| ko à"*.
**KEY FACT:** the literal `|||` is ALWAYS an *artifact* — `grep -c "|||" file.md` returns **0**. Obsidian's table parser chokes on a row and dumps the whole table as raw pipe text. The real cause is one (or more) of **4 layered issues**. **Diagnose ALL 4 before fixing — do NOT stop at the first you find.** (2026-07-20 session failure: fixed emoji only, declared done, Warren reported still-broken → root cause was **309 blank lines inside tables**. Cost a redo.)

**DIAGNOSTIC ORDER — run `scripts/diagnose_obsidian_table_render.py` for all at once:**
1. **BLANK LINES INSIDE TABLE (PRIMARY culprit).** Any empty line sandwiched between two `|` rows splits the table → Obsidian renders raw `|||`. This broke BOTH `03_COGS_Supplier_Monthly_Log.md` (309 blanks) and `14_Menu_GP_Monthly_Tracker.md` (60 blanks) in 2026-07. **Check this FIRST — it is the most common cause and the one most easily missed.**
2. **BLOCKQUOTE `>` INSIDE TABLE.** A `> note` line between rows also splits the table. Defer it AFTER the last row (or remove). (2 found in Menu GP file.)
3. **EMOJI IN CELL.** 🔴/🟡/✅/⏳ sitting in a cell column (Flag/Decision/Status) breaks the row. Other emoji in bullets/headers/`<!-- -->` templates render fine — preserve them.
4. **MOJIBAKE INSIDE TABLE (double-encoded UTF-8).** Text like `ThÃ¡ng` (should be `Tháng`), `Ä'Ã¡n vá»‹` (`Đơn vị`), `Î”%` (`Δ%`), `ðŸ"´` (`🔴`) = UTF-8 bytes decoded as cp1252. Looks like "sai font" but is a render+parse killer. Reverse: `s.encode('cp1252').decode('utf-8')` per line (outside HTML comments).

**Verify on disk — never assume (use the script or this corrected form):**
```bash
# 1. blank / blockquote INSIDE table regions (the REAL cause)
python3 - <<'PY'
import sys
lines=open(sys.argv[1],encoding='utf-8').read().split('\n')
in_c=False; in_t=False; blank=0; note=0
for l in lines:
    if '<!--' in l: in_c=True
    if in_c:
        if '-->' in l: in_c=False
        continue
    s=l.strip()
    if s.startswith('|'):
        if not in_t: in_t=True
        else:
            if s=='' : blank+=1
            elif s.startswith('>'): note+=1
    else: in_t=False
print("blank-in-table:",blank,"| blockquote-in-table:",note)
PY
# 2. emoji-in-cell count
grep -cE "\|[^|]*[🔴🟡✅⏳][^|]*\|" file.md
# 3. mojibake lines (cp1252-of-utf8 artifacts)
grep -cE "Ã|â€|ð.*‚|Â" file.md
```
**Fix (lean, deterministic — run the scripts IN THIS ORDER):**
1. `scripts/fix_obsidian_table_blanks.py <file>` — remove blank lines + defer `>` blockquotes that sit between `|` rows; verify broken-region count = 0. **(Primary fix — run this first.)**
2. `scripts/fix_obsidian_table_moji.py <file>` — reverse cp1252-of-utf8 on every non-comment line; verify mojibake-visible-left = 0.
3. `scripts/fix_obsidian_table_emoji.py <file>` — strip emoji in cells → R/Y/G (🔴→R, 🟡→Y, ✅→G). **Backup to `%TEMP%`, NOT vault** (zone-🔴). Verify emoji-in-cell = 0.
- **Header cells with emoji prefix** (e.g. `🔴Flags`) get split into `RFlags` by the strip → manually rename to plain `Flags` (patch). Watch for this.
**Hard rule:** NEVER "fix" by deleting the table or stripping emoji globally (destroys bullets/comments). Cell-only strip + blank-removal is the whole point. **Diagnose all 4 layers; one cause fixed ≠ done — Warren will report still-broken if you missed a layer.**

### BROKEN-WIKILINK INTEGRITY CHECK (2026-07-20 — vault-structure-audit Monday run)
Warren's vault has **53 unique ghost wikilinks** (500 occurrences / 99 files) at last scan. Most cluster in `10_archive/` (old analyses) + `00_DASHBOARDS.md` + `06_lusine_operations` cross-links. Two distinct classes — do NOT conflate:

1. **TRUE GHOSTS** — `[[Name]]` where NO `.md` with that basename exists anywhere (e.g. `COL_Breakdown`, `Dinh_Bien_Framework_v3`, `Lessons_Learned`, `SYSTEM_VIEW`, `Extra_Hours_Tracking_2026` — files genuinely deleted/renamed). Fix: delete the `[[..]]` or repoint to the renamed file.
2. **HTML-LINK CONVENTION** — `[[Name.html]]` targets. Per WARREN_MEMORY 2026-07-20 dashboards MUST be `file:///` URLs, not `[[wikilinks]]`. The `.html` files usually EXIST (verified: `COL_Trend_Dashboard.html`, `menu_gp_trend.html` present), so these are convention violations, NOT missing files. Fix: convert `[[x.html]]` → `file:///.../x.html`.

**⚠️ BASEPATH-RESOLUTION PITFALL:** Obsidian resolves `[[Target]]` by **note basename (filename minus .md)**, NOT folder path. A naive checker that matches exact relative paths over-reports broken links ~5x (every cross-folder `[[Name]]` looks broken though the note exists). Always build a **basename map of the whole vault** and resolve against that. Ignore placeholder tokens in templates (`wikilink`, `...`, `<file>`, `<file>.html`).
**Reusable:** `scripts/check_broken_links.py [vault_root]` — emits TRUE GHOST count + UNIQUE ghost targets + HTML-link class separated. Run it before any link-graph claim; never eyeball.

**WEEKLY HEALTH-CHECK PROTOCOL (Monday):** `vault-structure-audit --quick` dry-run covers structure/MOC; pair it with `ops_index_lint_sync.py --check-only` (Step 1, real python + Windows-native path, see pitfall #6) for lint. 🔴 Critical > 0 = fix before anything else (patch frontmatter, re-run to confirm = 0). 🟡 Warnings = hygiene, zone-🔴, do NOT auto-edit. Verify CONSISTENCY_LOG for `status: open` entries (report count only, don't dump).

### Pitfalls
1. **Folders show after correct userIgnoreFilters config → NOT a config bug.** `userIgnoreFilters` never hides the file tree (only Search/Graph). Warren reporting "vẫn hiện" after you set filters is EXPECTED — switch to dotfolder rename. Don't loop re-editing app.json.
2. **Dotfolder rename breaks hardcoded path refs.** 17+ `.py` files in Warren's vault hardcode `10_OPERATION_DATA/scripts`, `.../parsers`, `.../monthly`. Renaming breaks parsers UNLESS you bulk-update all string literals (Python script, not sed). `Path(__file__).resolve().parent` survives rename automatically. Requires Warren approval (file move = zone 🟡/🔴 per SOUL §5 file-op governance).
3. **`__pycache__` regen after rename.** If a renamed folder holds run scripts, Python recreates `__pycache__/` (non-dot) → reappears in tree. Fix: `sys.dont_write_bytecode = True` in scripts + `.gitignore` with `__pycache__/`. Verified: clean run produces zero regen.
4. **Windows reserved-name `nul` makes the WHOLE parent dir undeletable (escalation chain).** A stray `nul` (DOS device alias) in a folder breaks deletion of that folder via EVERY user-space tool:
   - `rm -rf` (git-bash) → "Device or resource busy"
   - Python `os.remove` / `shutil.rmtree` → WinError 5 (Access Denied) or WinError 32
   - `cmd /c del \\?\...nul` → exit 0 but file still listed
   - `powershell Remove-Item -Recurse -Force` (even **Admin**) → "Cannot remove ...\nul: Incorrect function" + "directory is not empty" → **FAILS**
   - WSL `rm -rf /mnt/c/...` → "No such file or directory" (9P FS hides the dir entirely)
   The dir can't be `rmdir`'d because it's "not empty" (contains the `nul` alias) and `nul` itself can't be removed by any standard tool.
   **Escalation chain that actually works (in order):**
   1. Kill the lock first: if `lusine-ops` (or any subdir) reports "used by another process", the holder is usually **Obsidian** (Smart Connections indexing) or **Explorer.exe** previewing the folder. Close Obsidian fully (Task Manager, kill `Obsidian.exe`), then `taskkill /F /IM explorer.exe; Start-Process explorer.exe`.
   2. Use **extended-path `rd`** (not `del`, not PowerShell): `cmd /c "rd /s /q \\?\C:\Users\khoans\Documents\Warren_OS_Local\vault\scripts"` — the `\\?\` prefix + `rd` (not `del`) is the one combo that handles the `nul` device alias. Run from Admin PowerShell if needed.
   3. Verify with `Test-Path` (PowerShell) or `os.listdir` — NOT `os.path.exists` (falsely True for `nul`).
   - **Also:** `os.path.exists("...nul")` falsely returns True on Windows (maps to NUL device) — always verify with `os.listdir`.
   - Stray `~` folder is a normal dir → `rm -rf` works fine (no `nul` involved).
   - Full recipe + real transcript in `references/windows-nul-and-locked-dir.md`.
5. **mv into existing dotfolder creates nesting.** `mv _private .private` when `.private` ALREADY EXISTS moves `_private` INTO `.private/_private` (nested). Check `ls -la` first; if target exists, move contents out then remove. Verify final structure with `ls -la .private/`.
6. **Hardcoded path breaks AFTER bulk-update if you miss local-var shadows + CWD-relative paths.** Bulk `.replace()` catches module-level strings, but these slip through:
   - **Local var shadow:** `regenerate_today.py` had `REVENUE_SCRIPT = VAULT_ROOT/"vault"/".scripts"/...` at module level (fixed) AND a SECOND `REVENUE_SCRIPT = VAULT_ROOT/"scripts"/...` inside `main()` → shadowed, still pointed at deleted `scripts/`. The grep/"no stale" check passed (module level was fine) but runtime still failed. **Grep the ENTIRE file for the old token, not just count occurrences.**
   - **`VAULT = Path(r"C:\...Warren_OS_Local")` + `VAULT/"vault/scripts"`** (double-root, CWD-relative assumption): `gen_today_and_send.py` did `VAULT / "vault/scripts"` → after rename should be `VAULT / "vault/.scripts"`. This is NOT `Path(__file__)`-derived — it assumes CWD-independent absolute base, so it breaks only when the script is invoked from a different working directory (exactly how Hermes/cron runs it). **Fix = derive everything from `Path(__file__).resolve().parent`**, never hardcode `vault/.scripts/...` as a string appended to a root.
   - **VERIFY FROM A DIFFERENT CWD (mandatory).** After patching, run the script from `/tmp` (or any non-vault dir): `python3 /full/path/to/script.py` with `cwd=/tmp`. If it resolves paths + imports OK → fixed. If it errors "file not found" → path still stale. This simulates how Hermes/cron actually invokes scripts and catches CWD-relative bugs that `cd vault && python script.py` hides.
   - Real transcript + the 11-check ad-hoc verify script in `references/dotfolder-path-repair.md`.
7. **Table shows raw `|||` → MULTI-LAYER, not just emoji.** The visible `|||` is Obsidian's *rendered artifact* of ANY table-parser choke. `grep "|||"` returns 0. Causes, in order of frequency this vault: (1) **blank line between `|` rows** [PRIMARY — broke both COGS + Menu GP files, 309 + 60 blanks], (2) `>` blockquote between rows, (3) emoji-in-cell, (4) mojibake (cp1252-of-utf8) inside rows. **Diagnose all 4 before fixing; fixing one ≠ done** (2026-07-20 redo: fixed emoji, declared done, Warren reported still-broken → 309 blanks remained). Use `scripts/diagnose_obsidian_table_render.py` then the 3 fix scripts in order.
8. **Workflow repeat-risk: `ops-weekly-report` SKILL.md example tables use emoji-in-cell (RED/YEL/GRN were originally 🔴🟡🟢 in §3 Watchlist / §4 KPI Rollup).** A future synthesis run following the skill literally will re-introduce the break. When generating `weekly_ops_synthesis.md` or the CONTEXT §5 diff, write cells as `RED`/`YEL`/`GRN` text; emoji allowed only in headers/bullets/free text. Warren approved "Option A" (strip emoji) on 2026-07-20 after a first draft shipped emoji-in-cell and had to be rewritten. If `ops-weekly-report` is ever unpinned, bake this into its Guardrails too.

### Decision tree (CORRECTED)
0. **Folder has hardcoded external refs (SSOT output, pipeline target, 50+ `file:///` links)?** → **CSS-snippet hide** (non-destructive). Do NOT dotfolder-rename (would break refs). **Detect refs:** `grep -rIn --include="*.py" --include="*.md" --include="*.json" -E "FOLDERNAME" . 2>/dev/null | head -60`. Count ≳10 → CSS-snippet. (Verified: `wiki/dashboards` → 50+ refs → snippet.)
1. Warren: "vault rối, ẩn đi" (junk folder, no external refs) → **go straight to dotfolder rename** (inventory → grep refs → rename → bulk-update → prevent `__pycache__` → verify → reload).
2. Optional: also keep `userIgnoreFilters` for extra Search/Graph hiding (redundant, not required).
3. Do NOT spend turns on userIgnoreFilters expecting tree-hiding — it will not work.

### 🔗 Consolidation note (for curator)
`obsidian-hide-clutter` (skill in note-taking/) is a STUB that predates this one and leads with the userIgnoreFilters approach (which fails for the file tree). This skill (`obsidian-vault-hygiene`) is the canonical, battle-tested version. Recommend **absorbing `obsidian-hide-clutter` into this skill** (or deleting it) to avoid future agents using the wrong primary method.

## References
- `references/obsidian-ignore-regex.md` — full asar excerpt + behavior notes.
- `scripts/verify_obsidian_ignore.py` — deterministic verification probe (reproduces Obsidian regex).
- `scripts/diagnose_obsidian_table_render.py` — ONE-SHOT diagnostic: counts all 4 break layers (blank-in-table, blockquote-in-table, emoji-in-cell, mojibake lines) + table-region count. Run FIRST.
- `scripts/fix_obsidian_table_blanks.py` — PRIMARY fix: remove blank lines + defer `>` blockquotes between `|` rows; verify 0 broken regions. (This was the real cause behind the 2026-07-20 `|||` reports.)
- `scripts/fix_obsidian_table_moji.py` — reverse cp1252-of-utf8 double-encode on non-comment lines; verify 0 mojibake-visible-left.
- `scripts/fix_obsidian_table_emoji.py` — cell-only emoji stripper for broken tables (emoji-in-cell → R/Y/G, backup to TEMP, verify 0 remaining).
- `scripts/check_broken_links.py` — wikilink integrity checker: basename-resolved TRUE GHOST count + HTML-link convention class separated (see BROKEN-WIKILINK INTEGRITY CHECK). Run before any link-graph claim.
- `templates/hide-folder-snippet.css` — ready-to-use CSS snippet to hide ONE folder from the explorer non-destructively (SSOT/pipeline-target folders only). Edit `data-path` to match; enable via Appearance → CSS snippets.
