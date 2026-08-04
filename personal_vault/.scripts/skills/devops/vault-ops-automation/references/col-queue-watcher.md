# COL Queue Watcher — Full Protocol

> Complete reference for the LLM-driven COL brain dump processor.
> Cron schedule: on-demand (triggered when raw entries appear in col_queue.json)

## Queue Location

```
vault/_inbox/col_queue.json
```

Structure:
```json
{
  "pending": [
    {
      "id": "COL-YYYYMMDD-HHMMSS",
      "status": "raw",
      "raw_text": "...",
      "source": "Telegram",
      "received_at": "ISO timestamp"
    }
  ],
  "history": [
    // done | stale | blocked | pending_approval entries moved here
  ]
}
```

## Pipeline Overview

| Step | Action | Tool |
|------|--------|------|
| 1 | Reformat brain dump | Manual text transformation per rules below |
| 2 | Dry-run | `ops_col.py "REFORMATTED" --dry-run` |
| 3 | Send Telegram preview | `_send_telegram.py` via urllib, token from `.env` |
| 4 | Update queue JSON | Move pending→history, add processed fields |
| 5 | Cleanup stale | Mark older pending_approval / duplicates as stale |

## Step 1 — Reformat Rules (detail)

### Date normalization
| Raw | Reformatted |
|-----|-------------|
| `June 26` | `26 JUN 26` |
| `26/06` | `26 JUN 26` |
| `28 June 26` | `28 JUN 26` |
| `26 JUN 26` (already correct) | keep |

### Store codes
| Raw | Reformatted |
|-----|-------------|
| `lu5`, `lu7`, `lu3` | `LU5`, `LU7`, `LU3` |
| `LU[3]` | `LU3` |

### Revenue numbers
| Raw | Reformatted |
|-----|-------------|
| `30.401.000` | `30,401,000` |
| `44.168.500` | `44,168,500` |

### Block headers
Each store section starts with: `LUx Actual Working Hour (DD MON YY)` on its own line.

### Role names (7 canonical, this order)
1. `FOH Management (RM, ARM, Shift Manager)`
2. `FOH Floor Lead (Captain, Supervisor)`
3. `FOH Service Agent (Service Agent, Retail Agent)`
4. `FOH Bar Team (all barista positions)`
5. `BOH Leader (Sous Chef, CDP)`
6. `BOH Cook (Commis/Demi)`
7. `Cleaner`

### Hours cleanup
- Strip trailing `h`: `16h` → `16`
- Remove `Total:` lines entirely
- Preserve decimals: `18.5` stays `18.5`

### Trainee folding
| Raw | Fold into |
|-----|-----------|
| `FOH Sup LU3 trainee: N` | FOH Floor Lead += N |
| `Bar Trainee LU3: N` | FOH Bar Team += N |

### Revenue line (add at end)
```
REVENUE (NET): LU3: XX,XXX,XXX LU5: XX,XXX,XXX LU7: XX,XXX,XXX
```

### LU5 bill calculation (only if no explicit revenue)
- Bill line: `Guest: N / AC: XXX,XXX`
- Revenue = Guest × AC
- Only applied for LU5 — other stores ignore Guest/AC

## Step 2 — Dry-Run

**Command:**
```bash
python3 C:\Users\khoans\Documents\Warren_OS_Local\vault\scripts\ops_col.py "REFORMATTED_TEXT" --dry-run
```

**⚠️ CLI quirk:** `--dry-run` MUST come AFTER the text. The script's argument parser checks `sys.argv[1] != '--dry-run'` and only reads text when True. Passing `--dry-run` first triggers the usage message instead.

**What to check in output:**
- Parsed date + day of week
- CPH month used (column `cph_used` in logs)
- Each store: revenue, COL%, status (Pass/Fail)
- Warnings: "Da ton tai trong sheet" = duplicate
- Trend vs last week

**Duplicate detection:** If all 3 stores show "Da ton tai trong sheet" with matching COL%, the data has already been processed. Mark entry as stale with `superseded_by` referencing the done entry.

## Step 3 — Telegram Preview

**Bot token path:** `C:\Users\khoans\AppData\Local\LUsineWorkBot\.env`
**Chat ID:** `2117653672`

**Token format:** `TELEGRAM_BOT_TOKEN=8394552936:AA...` (46 chars total)
**Utility script:** `vault/scripts/_send_telegram.py "message"` — reads token without printing it, uses urllib.

**Message format (normal):**
```
📊 COL DD/MM/YYYY — Preview
CPH: 202605 (fallback)

LU3: Rev=44,168,500 | 140.5h | COL=15.80% | 🟢 Pass
LU5: Rev=35,357,000 | 107.5h | COL=15.74% | 🟢 Pass
LU7: Rev=47,839,400 | 146h | COL=14.28% | 🟢 Pass

⛔ CHUA APPEND — Go ok.
```

**Message format (duplicate):**
```
⚠️ COL DD/MM/YYYY — DUPLICATE

So lieu nay da duoc xu ly va append truoc do.

CPH: 202605

LU3: Rev=44,168,500 | 140.5h | COL=15.80% | 🟢 Pass
LU5: Rev=35,357,000 | 107.5h | COL=15.74% | 🟢 Pass
LU7: Rev=47,839,400 | 146h | COL=14.28% | 🟢 Pass

⛔ KHONG APPEND — Duplicate, da co trong sheet
📥 Tu dong danh dau STALE
```

**Emoji legend by COL%:**
- `🟢` COL ≤ 15% → strong Pass
- `🟡` COL 15–20% → Pass
- `🔴` COL > 20% → Fail

## Step 4 — Queue Update (JSON)

After processing, update the entry in `col_queue.json`:

1. Remove from `pending` array (splice by index)
2. Insert at position 0 of `history` array

Entry fields to add:
```json
{
  "status": "stale",
  "preview": "📊 COL 28/06/2026 — Preview...",
  "reformatted_text": "LU3 Actual Working Hour (28 JUN 26)\nFOH Management...",
  "stores_data": [
    { "store": "LU3", "revenue": "44,168,500", "hours": "140.5", "col": "15.80%", "status": "Pass" }
  ],
  "dry_run_result": {
    "cph_used": "202605",
    "cph_note": "May 2026 (fallback)",
    "date": "20260628",
    "day": "Sunday",
    "lu3": { "revenue": 44168500, "hours": 140.5, "col": 15.8, "status": "Pass" }
  },
  "processed_at": "ISO timestamp"
}
```

For **duplicate entries**, also add:
```json
{
  "superseded_by": "COL-YYYYMMDD-HHMMSS",
  "staled_at": "ISO timestamp",
  "note": "Duplicate — same brain dump da duoc xu ly va append (COL-..., approved HH:MM)"
}
```

For **blocked entries** (can't parse, missing data):
```json
{
  "status": "blocked",
  "blocked_reason": "LU5: Thieu revenue — ...",
  "blocked_at": "ISO timestamp"
}
```

## Step 5 — Cleanup Stale

Check `history` for other `pending_approval` or `raw` entries for the SAME date. If found:
- Mark older entry as `"stale"`
- Add `superseded_by` pointing to the newer entry
- Add `staled_at` timestamp
- Move from pending to history if not already there

Also mark stale any entries flagged as duplicate (same revenue numbers + same date as an already-done entry).

## Edge Cases

| Situation | Action |
|-----------|--------|
| Parse fails completely | Send Telegram: "Da nhan [col] nhung khong parse duoc." Mark as blocked with reason |
| Partial data (FOH only, no BOH) | Still process what's available. Send Telegram noting partial data |
| All stores already in sheet (matching COL%) | Mark as duplicate/stale. Send Telegram with DUPLICATE notice |
| Some stores in sheet, some new | Process new stores only. Note in Telegram which were skipped |
| Google Auth expired (sheet API fails) | Use vault fallback CPH. Note in Telegram. Retry later after re-auth |
| LU5 missing revenue with Guest+AC data | Calculate: Guest × AC = Revenue. Only for LU5 |
| No CPH for current month | Fall back to latest complete previous month (e.g. 202605 for June) |
| Store has 0h for a role | Still include in reformatted text as `: 0` |
