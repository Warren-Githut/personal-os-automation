---
name: gsheet-safe-edit
description: Safe GSheet cell patch (A1+readback). For Bố 'sửa GSheet'.
version: 1.0.0
trigger: "sửa GSheet / update row / patch cell / ghi lại số / reconcile GSheet vs SQL"
category: productivity
related_skills: [obsidian-vault-hygiene, warren-parser-gate, verify-parser-output]
---

# gsheet-safe-edit — Safe Cell Patching in Known Sheets

> Mutating production GSheet data is a **Zone 🔴** operation. Even when Bố pre-approves ("apply ghi dùm bố"), the agent MUST dry-run, show OLD→NEW diff, write, then re-read to confirm. Hidden pitfalls below have caused silent partial writes and range errors.

## Workflow (4 steps, each is a completion gate)

### S1. Resolve column indices from the LIVE header — never assume names
Header arrays (e.g. `ops_col.HEADER_44`) are the SSOT for column position. **Do NOT guess column names.**
```python
import ops_col as O
H = O.HEADER_44
for i,v in enumerate(H):
    if any(k in v.lower() for k in ['net','rev','revenue','cov']):
        print(i, repr(v))
IDX_NET = H.index("Revenue")       # col 3 (net revenue lives here, NOT "Net_Revenue")
IDX_COV = H.index("Actual_Covers") # col 43
```
**Pitfall (2026-07-25):** a fix script assumed `HEADER_44.index("Net_Revenue")` → returned `None` (column absent) → would `TypeError` on live write. Always print the discovered indices.

### S2. Convert index → A1 letter for the update range
`values().update(range=...)` requires **A1 notation** (`'Tab'!D437`), NOT a header-name string. `O.HEADER_44[3]` returns `"Revenue"` → range `'Tab'!Revenue437` → **HttpError 400 "Unable to parse range"**.
```python
def col_letter(idx: int) -> str:
    s = ""; idx += 1
    while idx:
        idx, r = divmod(idx - 1, 26)
        s = chr(65 + r) + s
    return s
NET_LET, COV_LET = col_letter(IDX_NET), col_letter(IDX_COV)  # 3->'D', 43->'AR'
```

### S3. Non-adjacent columns → separate update calls
If target cells are NOT contiguous (Revenue col 3 vs Covers col 43), a single `body={"values":[[net, cov]]}` over range `D437:AR437` writes only the **first N contiguous cells** (D,E) — the distant column (AR) is NEVER touched. **Fix: one update call per column.**
```python
svc.spreadsheets().values().update(
    spreadsheetId=SID, range=f"'{TAB}'!{NET_LET}{ridx}",
    valueInputOption="USER_ENTERED", body={"values": [[new_net]]}).execute()
svc.spreadsheets().values().update(
    spreadsheetId=SID, range=f"'{TAB}'!{COV_LET}{ridx}",
    valueInputOption="USER_ENTERED", body={"values": [[new_cov]]}).execute()
```

### S4. Dry-run → live → readback (Zone 🔴 discipline)
```python
# 1) DRY: print OLD vs NEW for each matched row, NO write
# 2) LIVE: only if Bố approved, write
# 3) READBACK: re-GET the row, assert new values present
```
Always print `row#{ridx}: Revenue {old} -> {new:,} | Covers {old} -> {new:,}`.

## Pitfalls
- **Header name mismatch** — inspect `HEADER_*` before indexing; names drift (`Revenue` ≠ `Net_Revenue`).
- **A1 notation required** — `range` takes letters, not column names.
- **Non-adjacent columns** — wide-range + 2-value body writes only leading contiguous cells. Use per-column calls.
- **dotfolder blind** — `vault/.scripts` is a `.dotfolder`; `search_files` can't see it. Use `terminal` grep to find scripts.
- **Readback skip** — never trust "execute() succeeded"; re-GET to confirm both cells changed.
- **Cross-source surprise** — Bố's chat-pasted numbers may be a *brain-dump typo*, not the GSheet value. The GSheet live value can already be ~correct. Report the REAL old→new diff, not the assumed one.

## references/
- `references/gsheet_cell_patch_template.py` — known-good ad-hoc patcher (dry/live + readback) for 07_COL_Weekly_Log. Copy + edit TARGET dict.
