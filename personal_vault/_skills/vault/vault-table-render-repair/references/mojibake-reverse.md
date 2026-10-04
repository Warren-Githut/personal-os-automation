# Mojibake reverse — cp1252-of-UTF8

## Symptom
Vault file shows double-encoded UTF-8 where Vietnamese / symbols should be:
- `ThÃ¡ng`  → `Tháng`
- `Ä'Ã¡n vá»‹` → `Đơn vị`
- `Î”%` → `Δ%`
- `ðŸ"´` → `🔴`   (emoji also rots, so lint won't see it as emoji — it's garbage bytes)

## Cause
UTF-8 bytes were decoded/round-tripped as cp1252 (Windows-1252). The fix is to
re-encode as cp1252 then decode as utf-8 — this reconstructs the original.

## Safe reversal (display lines only — NEVER inside HTML comments / code blocks)
```python
def fix_line(line):
    try:
        return line.encode('cp1252').decode('utf-8')
    except (UnicodeEncodeError, UnicodeDecodeError):
        return line   # not mojibake, leave untouched

out = []
for l in lines:
    if '<!--' in l:
        in_comment = True
    out.append(l if in_comment else fix_line(l))
    if '-->' in l:
        in_comment = False
```

## Verification (do not skip)
After reversal, spot-check 3 lines read as correct Vietnamese (`Tháng`, `Đơn vị`,
`Giá cũ`). If they still look wrong, the file was not cp1252-of-utf8 — stop and
ask Warren; do not blind-reverse.

## Session example (2026-07-20)
`03_COGS_Supplier_Monthly_Log.md` blocks 06/05 had 130 mojibake lines. Reverse
restored Vietnamese; the now-revealed `🔴`/`⏳` emoji then needed the breaker-2
strip (R/Y/G). Order: (1) reverse mojibake, (2) strip emoji-in-cell, (3) remove
blank-in-table. All three layers required for clean render.
