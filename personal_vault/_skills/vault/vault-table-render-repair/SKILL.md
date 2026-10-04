---
name: vault-table-render-repair
description: Diagnose and fix Obsidian markdown tables that fail to render (show raw ||| pipes) in Warren's vault. Covers the three breaker classes — blank/blockquote lines inside a table, emoji inside a table cell, and column-count drift — plus the cp1252-of-UTF8 mojibake that often travels with them. Use when a vault .md shows broken tables, or when a parser/crawler is suspected of emitting render-breaking markdown. Includes a reusable lint script and the safe fix sequence. Also governs the default scope (report-only lint + auto-fix only the 2 parser-owned rolling logs; core/_growth/_archives are zone red — ask first).
---

# Vault Table Render Repair

## When to use
- A vault `.md` shows `|||` raw pipes instead of a rendered table in Obsidian.
- Warren reports "bảng không hiện", "toàn |||", "sai font" on a tracker/log file.
- After a parser/crawler run, tables in `10_OPERATION_DATA/*.md` (or elsewhere) stop rendering.
- You are writing/auditing a parser that emits markdown tables (prevent regressions).

## The three breaker classes (root causes)
Obsidian renders a markdown table only while consecutive lines all start with `|`. Any interruption breaks it.

| # | Breaker | Why it breaks | Symptom |
|---|---------|---------------|---------|
| 1 | **Blank line OR `>` blockquote between two `\|` rows** | Obsidian closes the table at the first non-`\|` line; the rest prints as raw `\| \|` | big blocks of `|||` |
| 2 | **Emoji / pictograph INSIDE a cell** (`\| 🔴 \|`) | Obsidian fails to parse the cell, dumps raw pipes | `|||` around the emoji row |
| 3 | **Column-count drift** (a row has different `\|` count than the header) | mis-aligned / broken render | shifted columns or raw pipes |

WARREN_MEMORY carries the standing rules: `d413` (emoji-in-cell → strip to R/Y/G) and `d415` (blank-in-table breaks render). This skill is the operational how-to.

### Emoji scope — IMPORTANT false-positive trap
Only these glyphs actually break Obsidian table cells: 🔴 🟡 ✅ ⏳ ⚠️ ❌ 🟢 and the broad pictographic range (codepoint ≥ U+1F300). Ordinary symbols do NOT break render and must be left alone:
- arrows `→ ← ↑ ↓` (U+2190–21FF)
- box-drawing `─ │ ┌` (U+2500–257F)
- stars `★ ☆` (U+2605/2606)
- math `≥ ≤ ≈ × ÷ −`
- `*` bullet chars

**Pitfall (2026-07-20 session):** a first-pass linter set `EMOJI_MIN = 0x2190` (arrows) as "emoji", which falsely flagged every `→` mapping cell — producing 4319 phantom issues across the vault. Fix: detect only a whitelist (`BREAKING_EMOJI`) plus `o >= 0x1F300`, never the arrow block. See `scripts/vault_table_render_lint.py`.

## Diagnostic sequence (NEVER guess — verify on disk)
1. Run the lint script on the suspect file (or whole `10_OPERATION_DATA`):
   ```
   py vault/.scripts/vault_table_render_lint.py <folder-or-file>
   ```
   Exit 1 = issues (prints `## path (N)` + `Lnn: message`). Exit 0 = clean.
2. Separately check for mojibake (see below) — lint does NOT catch encoding rot.
3. Classify: which of the 3 breakers, and in which table region.

## Fix procedures
### Breaker 1 — blank / blockquote inside table
- **Blank line**: delete the blank line that sits between two `|` rows. Tables want rows contiguous; a blank BEFORE the first data row (after header) is tolerated by Obsidian, but a blank BETWEEN data rows is not.
- **`>` blockquote note after last row**: Obsidian treats a `>` immediately after a `|` row as table continuation. Fix = ensure a blank line SEPARATES the note from the table: `| last row |` then `> note` then a blank line. I.e. the `>` must not be the very next line after a `|` row without a blank; safer: put a `---` or blank line, then the note.
- Safe automation: a script that, while inside a table region, drops blank lines and defers `>` lines to after the last row works — but verify the result renders (Obsidian closes table on first non-`|` line, so a `>` right after the last row with no blank is still "inside").
- **`>` blockquote WRAPPING THE WHOLE table/list (distinct mode — 2026-07-26):** If EVERY line of a table or bullet list carries a `> ` prefix (e.g. copied verbatim from a handoff/chat that used `>` to quote the block), Obsidian treats the ENTIRE block as one blockquote and does NOT parse it as a table → prints raw `| | |`. This is different from "blockquote BETWEEN rows" (where the table is top-level but interrupted). **Fix:** strip the `> ` prefix from every line of the pasted block BEFORE writing to vault. Rule: markdown tables + bullet lists MUST be top-level (no `>` wrapper) to render. Reserve `>` for single-line callouts (e.g. `> 📊 link`), never wrap multi-line tables/lists. (`vault-edit-discipline` carries the same lesson under its blockquote-wrap pitfall.)

### Breaker 2 — emoji in cell
- Replace cell emoji with letters/text per WARREN_MEMORY d413:
  - 🔴 → `R`, 🟡 → `Y`, ✅ → `G`
  - ⏳ Pending → `Pending`
  - Keep emoji in bullets, headers, and HTML comments — only strip inside `| ... |`.
- **At the parser source** (prevent recurrence): make the emitter return `R/Y/G` instead of emoji. Example from `cogs_parser.py`:
  ```python
  def flag_letter(pct):
      if pct >= 13: return "R"
      if pct >= 5: return "Y"
      return "G"
  ```
  and the Menu-Price-Action row emits `| ... | Pending | {flag_letter(pct)} |` (no emoji).

### Breaker 3 — column drift
- Find the header `| a | b | c |` count, then fix the offending row to match. Usually a missing/extra `|` or an unescaped `|` inside a cell value.

## Mojibake (sai font) — often travels with breaker tables
Symptom: `ThÃ¡ng` (for `Tháng`), `Ä'Ã¡n vá»‹` (for `Đơn vị`), `Î”%` (for `Δ%`), `ðŸ"´` (for `🔴`). Cause: UTF-8 bytes were decoded as cp1252 (double-encode). Reverse ON DISPLAY LINES ONLY (never inside HTML comments / code blocks):
```python
try:
    fixed = line.encode('cp1252').decode('utf-8')
except (UnicodeEncodeError, UnicodeDecodeError):
    fixed = line   # not mojibake, leave as-is
```
Verify the reversal actually produced Vietnamese (spot-check 3 lines) before writing. See `references/mojibake-reverse.md`.

## Default operating mode (scope governance — zone 🔴)
Warren's vault has thousands of legacy render issues across core/_growth/_archives/_cases. Do NOT bulk-fix.
- **Lint = report-only.** It scans and lists; it does not auto-mutate.
- **Auto-fix ONLY** the 2 rolling-log files the parsers own: `10_OPERATION_DATA/03_COGS_Supplier_Monthly_Log.md` and `10_OPERATION_DATA/14_Menu_GP_Monthly_Tracker.md`.
- **core/ (`_CORE_LOGIC`), _growth, _archives, _cases** = zone 🔴. Ask Warren per-file before touching. A blanket "fix all" there destroys intentional `→`/`★`/`≥` glyphs he uses on purpose.
- After any fix, re-run lint on the touched file → must show 0 issues.

## Verification checklist (before commit)
- [ ] Lint on touched file = 0 issues
- [ ] Mojibake reversed + spot-checked (Vietnamese reads correctly)
- [ ] Emoji-in-cell → R/Y/G only; no emoji left inside any `| ... |`
- [ ] Parser source (if edited) still compiles; dry-run emits R/Y/G not emoji
- [ ] Commit-push self-gate (SOUL §5.3) passed; push via ephemeral token, not stored creds

## See also
- `scripts/vault_table_render_lint.py` — the reusable scanner (copy or invoke directly)
- `references/obsidian-table-breakers.md` — condensed breaker reference
- `references/mojibake-reverse.md` — cp1252-of-utf8 reverse recipe + worked example
- WARREN_MEMORY.md d413 / d415 (standing vault rules)
