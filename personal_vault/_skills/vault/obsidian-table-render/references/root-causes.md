# Root Causes — Obsidian Table Render Failures (2026-07-20 post-mortem)

## The 3 real causes (Warren sees raw `| |` in Obsidian)

1. **Emoji inside a table cell** — `🔴 🟡 ✅ ⏳ 💰` between `|`. Obsidian
   refuses to render, prints raw pipes. Hard rule `WARREN_MEMORY.md` dòng 413.
   Fix: replace with letters **R / Y / G** or plain words (`Pending`). Keep
   emoji in bullets / headers / HTML comments (fine there).

2. **Blank line OR `>` blockquote line between two table rows.** Obsidian
   treats the gap as end-of-table → splits it → raw pipes. (`WARREN_MEMORY.md`
   dòng 430, GrabFood parser hit this.) Fix: delete the inter-row line;
   if the `>` note is needed, move it AFTER the last row / outside the table.

3. **cp1252-of-UTF-8 mojibake** — text like `ThÃ¡ng` (should be `Tháng`),
   `Ä'Ã¡n vá»‹` (= `Đơn vị`), `Î”%` (= `Δ%`), `ðŸ”´` (= `🔴`). Caused by
   UTF-8 bytes decoded as cp1252 then re-encoded. Not a render-breaker
   by itself, but corrupts cells. Reverse:

   ```python
   def reverse(s):
       try:
           return s.encode('cp1252').decode('utf-8')
       except Exception:
           b = bytearray()
           for ch in s:
               try: b += ch.encode('cp1252')
               except Exception: b.append(ord(ch) & 0xFF)
           return bytes(b).decode('utf-8')
   # apply ONLY to non-comment lines; never touch inside <!-- -->
   ```

## The 4319 false-positive lesson (the BIG one)

A whole-vault lint found **4319 issues**. ~80% were FALSE POSITIVES:
- `USER.md` / `CONTEXT.md` / `*_INDEX.md` use intentional emoji/symbols
  INSIDE cells as content (★ star-ratings in LTO, `→` arrows in indexes,
  `≥`/`≤`/`−`/`≈` math symbols). These do NOT break Obsidian and must
  NOT be "fixed".
- The shipped lint uses `EMOJI_MIN = 0x2190` (so it DOES flag `→` U+2192
  and ✅❌⚠⏳ — because `→` inside a cell also breaks Obsidian), but EXCLUDES
  box-drawing `U+2500–257F` and does NOT flag `★` (U+2605). Do NOT "raise to
  U+1F000" — that would miss the `→`-in-cell breaker. Intentional `→`/`★` in
  core/index files mostly sit in bullets/headers (outside `|`), so they don't
  break render; only flag them when between `|`. Always read the actual script
  before assuming its threshold.

**RULE:** When a scan lights up the whole vault, DO NOT auto-mutate hundreds
of files. (1) Sanity-check the lint threshold against intentional content.
(2) Scope fixes to the file(s) Warren actually reported. (3) Mutating ANY
vault file/dir is **zone 🔴** — ask Warren before bulk-editing. This is
also a `safenet` Kill-Criterion hit (over-broad automation). Push back:
*"Bố, lint bắt 4319 nhưng 80% là emoji Bố cố ý dùng, con chỉ sửa file Bố báo thôi."*

## Parser-author pitfall (cogs_parser.py v3.4)

`build_entry()` had `flag_emoji(pct)` returning `🔴/🟡/✅` → broke every
month's table; and `| ⏳ Pending | 🔴 |` in the Menu Price Action table.
Fix: return `'R'/'Y'/'G'` letters; write `Pending` without emoji. Wire
`vault_table_render_lint.py` into the Monday 09:00 vault lint so regressions
are caught before Warren opens Obsidian.

## Verify recipe (per file)
```bash
REALPY="C:/Users/khoans/AppData/Local/Python/pythoncore-3.14-64/python.exe"
V="C:/Users/khoans/Documents/Warren_OS_Local/vault"
"$REALPY" "vault/.scripts/vault_table_render_lint.py" "$V"
# expect: CLEAN for the fixed file; if issues, they are real picture-emoji/blank-in-table
```
## The 2-layer-miss trap (2026-07-20 — why Warren sent it back)

First pass on `03_COGS_Supplier_Monthly_Log.md` fixed emoji-in-cell + mojibake
and reported "done". Warren opened Obsidian: **still raw pipes**. Root cause
I had MISSED: **309 blank lines sitting between table rows** (hand-pasted
block 05/06, each row followed by a blank). That single layer was the real
breaker; emoji+mojibake were secondary. Same on `14_Menu_GP_Monthly_Tracker.md`
(60 blanks + 2 blockquotes between rows).

**Lesson to carry forward:** when Warren reports "bảng ko hiện", run the lint
and READ ALL THREE counters (emoji / blank / blockquote / mojibake) before
claiming done. Fix every layer that is non-zero, then re-run lint → 0. Saying
"fixed" after touching only 1–2 layers wastes a round-trip and Warren calls it
out ("check kỹ lại con"). The lint's `blank_inside_table` count is the one most
often overlooked — treat a non-zero blank count as the prime suspect.

Backup before mutating: copy to `%LOCALAPPDATA%\\Temp\\` (outside repo, no vault rác).
