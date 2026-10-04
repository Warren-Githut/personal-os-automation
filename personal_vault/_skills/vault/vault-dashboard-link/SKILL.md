---
name: vault-dashboard-link
description: "Insert a clickable file:/// link to a dashboard HTML into a vault .md tracker/log, with target verification and hidden-comment / broken-index-link pitfalls. Use when Warren asks to 'thêm clickable link', 'cho bố 1 link', 'link này clickable', or 'make link clickable' on a vault .md pointing at a dashboard."
version: 1.0.0
author: Hermes
trigger: "Warren: 'thêm clickable link', 'cho bố 1 link', 'link này clickable', 'make link clickable' on a vault .md file"
category: vault
---

# vault-dashboard-link — Add clickable dashboard links to vault .md files

## When to use
Warren repeatedly asks to add a clickable link at the TOP of an operational tracker/log `.md` file, pointing to a dashboard HTML (Chart.js). Recurring across GrabFood, COL, Wastage, Wage/CPH, P&L files. This is a class of task, not a one-off.

## Steps
1. **Read top of target .md** (`read_file`, first 40 lines) to see frontmatter + structure (title, any `<!-- -->` block).
2. **Verify the dashboard HTML ACTUALLY EXISTS on disk.** NEVER trust the pasted path blindly — Warren sometimes omits a subfolder (pasted `../../10_OPERATION_DATA/13_PL_Dashboard.html` but real file is `10_OPERATION_DATA/._assets/13_PL_Dashboard.html`).
   - Use `terminal`: `ls -la "<path>"` then `find "<vault_root>/vault" -iname "*Dashboard*.html"` to discover the real location.
   - ⚠️ Do NOT use `search_files` (target=files OR content) — on Windows MSYS it returns false IO errors ("The system cannot find the file specified") even when the file exists. Known false-negative trap (SOUL §6 Pitfalls). Trust `terminal ls`/`find` only.
3. **Check for an EXISTING link hidden in an HTML comment.** Some trackers (e.g. `07_COL_Weekly_Log.md`) already contain a `file:///...html` line — but INSIDE a giant `<!-- HERMES TEMPLATE ... -->` block (opened line 36, closed line 730). Obsidian hides comment content → link not clickable. Always grep for `.html`/`file://` in the target and confirm whether it's inside `<!-- -->`. Insert the new link OUTSIDE any comment (right after frontmatter, before the comment opens).
4. **Insert the link at the TOP** — immediately after the frontmatter closing `---`, BEFORE any `<!--` template comment or `# Title`. This is the KEY placement rule (Warren 2026-07-27, Google Review dashboard):
   - ❌ WRONG: link ở CUỐI file (dưới entry cũ) → Bố phải cuộn xuống mới thấy, nonfriction FAIL.
   - ✅ RIGHT: link ngay đầu, Bố mở file là click được.
   ```markdown
   > 📊 **[Dashboard Name](file:///C:/Users/khoans/Documents/Warren_OS_Local/vault/.../Foo_Dashboard.html)** — xem chart xu hướng. Mở bằng Chrome/Edge.
   ```
   - **Mở bằng Chrome/Edge note BẮT BUỘC** (ANCHORS A16): Obsidian block `<script>` → KHÔNG render Chart.js. Dashboard HTML PHẢI mở ở browser thật (`file:///`), không dùng Obsidian. Bố dễ quên → luôn ghi nhắc.
   - Use Vietnamese label (e.g. "Google Review CX Dashboard", "GrabFood Trend Dashboard", "COL Trend Dashboard", "CPH Dashboard", "P&L Dashboard"). Keep `file:///` (3 slashes) with absolute Windows path.
   - **Update week-range text** in the link label when the dashboard data advances (e.g. "W20–W29" → "W20–W30") so Bố knows it's current.
5. **Patch uniqueness**: the `patch` tool uses fuzzy matching and rejects short old_strings with "Found N matches". Include enough surrounding context (next unique line — e.g. the `# Title` or template header line) to make old_string unique.
6. **Fix broken links in the index too.** When the dashboard path was wrong/mislocated, also check `30_KNOWLEDGE_BASE/wiki/00_DASHBOARDS.md` (the dashboard index table) for the same broken `[[...]]` wikilink and fix it in the same pass. Warren expects this ("nhân tiện con fix cái link trong 00_dashboards luôn").
7. **Do NOT commit/push** unless Warren says "commit push" — then run SOUL §5.3 COMMIT-PUSH gate (self-check Q1 SSOT / Q2 automation, print, wait for approval).

## Pitfalls
- **search_files false-negative (Windows)**: returns IO error for existing files. Always verify dashboard existence via `terminal ls`/`find`.
- **Hidden-comment trap**: a prior dashboard link inside `<!-- -->` is invisible/unclickable in Obsidian. New link must sit outside the comment.
- **Pasted path may be incomplete**: auto-discover real path with `find -iname`. The P&L dashboard lives in `10_OPERATION_DATA/._assets/` (hidden junk folder per SOUL §5.2), NOT `wiki/` like the others (GrabFood/COL/CPH/Wastage are in `30_KNOWLEDGE_BASE/wiki/...`). Links into `._assets/` still work but are off-standard — flag to Warren and OFFER to relocate to `wiki/01_P&L_Budget/` (zone 🟡, needs approval; would also change cron gen script path).
- **patch fuzzy-match "Found N matches"**: widen old_string context (include following unique line).
- **Don't blindly create a duplicate link** if one already exists OUTSIDE a comment — check first.
- **Don't trust `search_files` empty result as "file missing"** — it's a false negative on Windows. `terminal find` is the source of truth.
- **🔴 PLACEMENT — link PHẢI ở TOP, KHÔNG ở cuối file (Warren 2026-07-27):** Trước sửa, Google Review dashboard link nằm ở DÒNG 107 (cuối file, dưới entry W29 cũ). Bố phải cuộn xuống mới thấy → nonfriction FAIL. Fix: move link lên ngay sau `---` frontmatter (trước entry W30). Luôn ưu tiên TOP placement mọi dashboard link mới.
- **🔴 Obsidian KHÔNG render Chart.js (ANCHORS A16):** Dashboard HTML có `<script>` → Obsidian block. Link PHẢI mở bằng Chrome/Edge (`file:///`), không click trong Obsidian. Luôn ghi "Mở bằng Chrome/Edge" trong link label.
- **Update week-range trong label:** Khi dashboard data tiến (vd W29→W30), sửa text "W20–W29" → "W20–W30" trong link label để Bố biết current.

## Example — Google Review CX Dashboard (2026-07-27)
Target: `vault/10_OPERATION_DATA/05_Google_Review_Weekly_Log.md`
Dashboard HTML: `vault/30_KNOWLEDGE_BASE/wiki/05_google_review/dashboard.html`
Correct TOP placement (after frontmatter `---`):
```markdown
---

> 📊 **[Google Review CX Dashboard](file:///C:/Users/khoans/Documents/Warren_OS_Local/vault/30_KNOWLEDGE_BASE/wiki/05_google_review/dashboard.html)** — Avg★ & Reviews/1k theo tuần (W20–W30). Mở bằng Chrome/Edge.

<!-- HERMES TEMPLATE ... -->
```
Remove any old link at the bottom of the file (grep for `dashboard.html` to find stragglers).

## Verification
- `terminal ls` the target HTML → exists (non-zero size, recent mtime).
- `read_file` the edited .md → link present, OUTSIDE any `<!-- -->`, correct absolute `file:///` path.
- If index was fixed: `terminal grep` confirms `00_DASHBOARDS.md` link no longer points at a missing path.

## Notes
- Obsidian renders `file:///C:/...` markdown links as clickable, opening in the default browser (not inside Obsidian) — correct for HTML dashboards.
- Folder `._assets/` is a dotfolder (hidden from Obsidian UI) but `file:///` links into it still resolve fine.
