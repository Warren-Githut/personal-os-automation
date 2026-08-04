# Real-World Routing Patterns

## Observed 2026-06-23 Session

### Session Context
- Cron job (no user present)
- Last process: 2026-06-02 (21 days gap)
- Items found in `01_unprocessed/`: 7
- Domain split: 3 health, 1 stock pending, 3 family/legal

### Pattern: Health Log via Slack
File pattern: `YYYY-MM-DD_T_health_health-log-june-N.md`
Frontmatter: `date`, `source: slack`, `domain: health`, `type: T`
Content format (single line):
```
Health log june N: :hospital: Health: {sleep}h | quality {Q} | {weight}kg | {fast}h | Huyết áp: {sys}/{dia}
```
**Route:** Daily_Pulse.md — create new date entry with 5 bullets.
**Edge case:** Multiple files arrive at once → process oldest first, newest on top.

### Pattern: TCBS / Broker Research PDF (Source Document)

File: `TCBS_MSCI_review2026_Vietnam_VN-1.pdf` (or similar `<broker>_<topic>_<country>_<version>.pdf`)
Companion: `TCBS_MSCI_review2026_Vietnam_VN-1.lit.txt` (OCR/literate text extraction from the same PDF)

**Characteristics:**
- No frontmatter — raw PDF source, not a vault note
- Content: Broker research report about market classification, macro events, sector analysis
- Date-coded in filename (e.g. `review2026` = published 2026)
- Often lands in inbox alongside already-processed email summaries of the same report

**Route (dedup-first):**
1. Read the `.lit.txt` companion for extractable content (or read first 100 lines of the PDF text via OCR extraction)
2. Search `021_VNStock_Macro.md` for matching topic keywords (e.g. "MSCI", "FTSE", "nâng hạng", broker name, date)
3. If matching content already exists → **archive only** (data already captured via Bonnejed email or other pipeline)
4. If content is genuinely NEW → create a brief entry in `021_VNStock_Macro.md` (newest on top), then archive the PDF
5. Archive destination: `02_processed_archived/` (same folder as other processed items)

**Pitfall:** TCBS emails are often processed via Bonnejed → stock_pending JSON → macro file before the PDF even arrives in the inbox. Always check the macro file first; 90% of the time the data is already there. Never create a duplicate entry.

### Pattern: Bonnejed Weekly Stock JSON

File: `stock_pending/YYYY-MM-DD_HHMM_Bonnejed_{hash}.json`
Key fields:
- `summary` → macro context + sector highlights + ticker catalysts
- `entry_body` → pre-formatted markdown for the target file
- `target_file` → `020_VNStock_Weekly_Outlook.md`
- `tickers` → array to merge into frontmatter

**Route:** Extract `summary.thi_truong`, `summary.vi_mo`, `summary.nganh`, and `summary.tickers`. Format into structured markdown matching existing entries (tables for sector highlights + watchlist). Append `entry_body` at appropriate position.

**Do NOT:** Use `[...]` placeholders from the template — replace with real data from `summary`.

### Pattern: Voice Transcript about Court
File: `YYYY-MM-DD_V_family_gg_toa_hoa_giai_ly_hon.md`
Frontmatter: `source: voice`, `domain: family_gg`, `type: V`
Content: Raw transcript + extracted facts (court address, room, judge name, schedule)

**Route:** If case file already has this data → archive only. If new → add timeline entry to `_cases/active/legal_divorce_court_GG_access.md`.

### Pattern: "Transcribe and Suggest" Voice File
File: `YYYY-MM-DD_V_undetectable_transcribe_x_status_suggest_list.md`
This is a request to process a voice note, not the data itself. The transcription is embedded.

**Route:** Extract the transcribed info → route the extracted data (not the request itself). The request is satisfied by processing.

### Pattern: GG Capture (Text from Slack)
File: `YYYY-MM-DD_T_family_gg_capture_gg_{description}.md`
Frontmatter: `source: slack`, `domain: family_gg`, `type: T`
Content: Emotional/parenting moment about GG.

**Route:** Already in Daily_Pulse via `/capture-gg` → archive only. If not yet captured → add to Daily_Pulse.

### Frontmatter Update Templates

**Daily_Pulse.md:**
```yaml
# Only update:
last_updated: YYYY-MM-DD
```

**020_VNStock_Weekly_Outlook.md:**
```yaml
# Update:
last_updated: YYYY-MM-DD
entries: N     # increment
# Optionally append new tickers:
tickers: [...existing..., NEW_TICKER]
```

**Case file:**
```yaml
last_updated: YYYY-MM-DD
follow_up: YYYY-MM-DD   # reset if past due
```

### Archive Structure
```
02_processed_archived/
├── YYYY-MM-DD_T_health_health-log-*.md
├── YYYY-MM-DD_V_family_*.md
├── YYYY-MM-DD_T_family_*.md
└── stock_pending/
    └── YYYY-MM-DD_HHMM_Bonnejed_*.json
```
