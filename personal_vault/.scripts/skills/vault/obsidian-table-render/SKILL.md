---
name: obsidian-table-render
description: "Diagnose and fix Obsidian markdown tables that fail to render (show raw '| |' pipes instead of a grid). Covers the 3 real root causes — emoji-in-cell, blank/blockquote lines between rows, and cp1252-of-UTF-8 mojibake — plus a scoped lint script and the critical scope-discipline rule (do NOT auto-nuke the whole vault; most 'issues' are intentional emoji in core/index files). Trigger: Obsidian shows raw pipes for a .md vault table, or before committing any parser that writes markdown tables."
version: 1.0.0
author: Hermes
trigger: "Obsidian renders '| |' raw pipes instead of a table; or before shipping a parser that emits markdown tables."
category: vault
---

# /obsidian-table-render — Fix tables that won't render in Obsidian

> Warren (non-IT) sees raw `| |` in Obsidian when a markdown table is malformed. This is the canonical procedure, root-caused from the 2026-07-20 COGS Supplier Log + Menu GP Tracker fixes, and a 4319-issue whole-vault lint false-positive that taught the scope lesson.

## 🚨 THE 3 ROOT CAUSES (always one of these)

Obsidian renders a `|`-delimited block as a table ONLY if: every row is contiguous, separators use `|---|`, and cells contain no "picture" emoji. Breaks happen when:

1. **Emoji inside a table cell** — 🔴 🟡 ✅ ⏳ 💰 etc. sit between `|`. Obsidian refuses to render and prints raw pipes. `WARREN_MEMORY.md` dòng 413 hard rule. → Replace with letters **R / Y / G** (red/yellow/green) or plain words (`Pending`).
2. **Blank line OR `>` blockquote line between two table rows.** Obsidian treats the gap as end-of-table → splits it → raw pipes. (GrabFood parser hit this, `WARREN_MEMORY.md` dòng 430.) → Delete the inter-row line; if the `>` note is needed, move it AFTER the last row / outside the table.
3. **cp1252-of-UTF-8 mojibake** — text like `ThÃ¡ng` (should be `Tháng`), `Ä'Ã¡n vá»‹` (= `Đơn vị`), `Î”%` (= `Δ%`). Caused by UTF-8 bytes decoded as cp1252 then re-encoded. Not a render-breaker by itself, but corrupts cells. → Reverse: `s.encode('cp1252').decode('utf-8')`. See `references/root-causes.md`.

## PROCEDURE (always verify on disk first — never guess)

1. **Diagnose** with the bundled lint: `python vault/.scripts/vault_table_render_lint.py <vault_root>` (or skill `scripts/vault_table_render_lint.py`). Reports per-file: `blank_inside_table`, `blockquote_inside_table`, `emoji_in_cell` (the shipped script flags codepoints ≥ U+2190 except box-drawing U+2500–257F — so `→`/✅/❌/⚠/⏳ break, but `★` does not), and `col_mismatch`.
2. **Fix emoji-in-cell** → R/Y/G letters. Keep emoji in bullets / headers / HTML comments (Obsidian is fine there).
3. **Fix blank/blockquote-in-table** → delete the inter-row blank line; if a `>` note is needed right after the last row, keep it but ensure a blank line follows it so Obsidian closes the table.
4. **Fix mojibake** → run the cp1252 reverse on non-comment lines ONLY (NEVER touch inside `<!-- -->` blocks — they may intentionally contain sample pipes/arrows).
5. **🔴 VERIFY-THEN-CLAIM gate:** fix ALL THREE layers (emoji + blank/blockquote + mojibake) before reporting done. Re-run lint → expect `0` for the target file's real (non-comment) tables. Also `grep`/`sed` a sample table region shows contiguous `|` rows with no blank between. Do NOT tell Warren "fixed" until lint = 0. (2026-07-20: I missed the blank-in-table layer twice and Warren had to send it back — embed this.)

## ⚠️ SCOPE DISCIPLINE — THE BIG LESSON (2026-07-20)

A whole-vault lint found **4319 issues**. ~80% were **FALSE POSITIVES**:
- `USER.md` / `CONTEXT.md` / `*_INDEX.md` use intentional emoji/symbols INSIDE cells as content (★ star-ratings in LTO, `→` arrows in indexes, `≥`/`≤`/`−`/`≈` math symbols). These do NOT break Obsidian and must NOT be "fixed".
- The lint's first version used `EMOJI_MIN = 0x2190`, which wrongly flagged `→` (U+2192) and `★` (U+2605). Correct threshold: flag only `ord(ch) >= 0x1F000` OR `ch in {'✅','❌','⚠️','⏳'}` (the empirically-observed breakers). Arrows/math/stars are fine.

**RULE:** When a scan lights up the whole vault, DO NOT auto-mutate hundreds of files. (1) Sanity-check the lint threshold against intentional content — the shipped script uses `EMOJI_MIN = 0x2190` (flags `→`/✅/❌/⚠/⏳) but EXCLUDES box-drawing (U+2500–257F) and does NOT flag `★`(U+2605); intentional `→`/`★` in core/index files mostly sit in bullets/headers (outside tables) so they don't break render. (2) Scope fixes to the file(s) Warren actually reported. (3) Mutating ANY vault file/dir is **zone 🔴** — ask Warren before bulk-editing. This is also a `safenet` Kill-Criterion hit (over-broad automation). Push back: *"Bố, lint bắt 4319 nhưng 80% là emoji Bố cố ý dùng / nằm ngoài bảng, con chỉ sửa file Bố báo thôi."*

## FOR PARSER AUTHORS (luso-parsers / cogs_parser / menu_gp_parser)

If you write a parser that emits markdown tables, **never put emoji in a cell**. `cogs_parser.py` v3.4 had `flag_emoji(pct)` returning `🔴/🟡/✅` → broke every month's table. Fix: return `'R'/'Y'/'G'` letters. Same for `⏳ Pending` in the Decision column → just write `Pending`. Wire `vault_table_render_lint.py` into the Monday 09:00 vault lint so regressions are caught before Warren opens Obsidian.

## Pitfalls
- **🚨 DECLARE-VICTORY-TOO-EARLY (the 2026-07-20 repeating mistake).** Warren said "vẫn ko hiện bảng, check kỹ lại" after I fixed ONLY emoji + mojibake and MISSED the 309 blank-lines-inside-table layer. The blank-in-table layer is the most common and the easiest to overlook. **Fix ALL 3 layers, then verify on disk (re-run lint → 0 issues) BEFORE telling Warren it's done.** Saying "fixed" after touching only 1–2 layers = wrong, costs a round-trip, and Warren calls it out. Same for the reverse: never tell Warren a file is clean until lint reports 0 for its real (non-comment) tables.
- **Guessing the cause** — always run the lint / `grep` first; the 3 causes look identical from Warren's screenshot.
- **Over-broad lint → false positives** — the SHIPPED script uses `EMOJI_MIN = 0x2190` with a box-drawing exception (U+2500–257F allowed). It DOES flag `→` (U+2192) because `→` inside a cell breaks Obsidian render, but does NOT flag `★` (U+2605) — verify against the actual script before assuming a threshold. Intentional `→`/`★` in core/index files are usually OUTSIDE tables (bullets/headers), so they don't break render; only flag them when they sit between `|`.
- **Editing inside `<!-- -->`** — template comments intentionally contain pipes/arrows; reversing mojibake or stripping there corrupts the template.
- **Auto-nuking the vault** — zone 🔴; ask first. The lint is a REPORT tool, not an auto-fix.
- **Forgetting mojibake** — if emoji-in-cell + blank-line fixes don't make the table render, check for `Ã`/`â` garbage (cp1252 double-encode); reverse it.
- **`>` note immediately after last row** — a blockquote right after the final `|` row is fine IF a blank follows it (`|row|` → `>note` → blank → text closes the table). Do NOT strip the note; just ensure a blank line separates it from the following content. The lint must reset `in_table` on `>` (not flag it) to avoid false `blockquote_inside_table` on valid notes.

## Support files
- `scripts/vault_table_render_lint.py` — the scoped lint (run on a vault root; exit 1 if real issues found).
- `references/root-causes.md` — exact repro + the cp1252 reverse snippet + the 4319 false-positive post-mortem.
