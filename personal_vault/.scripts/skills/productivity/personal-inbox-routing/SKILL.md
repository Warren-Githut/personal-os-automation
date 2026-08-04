---
name: personal-inbox-routing
description: >-
  Process items from _inbox/01_unprocessed/ in Personal_OS vault — categorize, route to correct destination,
  update frontmatter, archive originals, log changes. Handles health logs, stock data, family/legal notes,
  ideas, and unsorted items from Slack brain-dump.
trigger:
  - cron job: called by `personal-process-notes` umbrella (which is invoked by `/process-notes`)
  - manual: /process-notes when user asks to "xử lý inbox" or "process notes"
  - sub-skill: called by `personal-process-notes` orchestrator for the inbox-routing sub-task
---

# Personal Inbox Routing

## Overview

The `_inbox/01_unprocessed/` folder receives raw Slack brain-dump items. Each must be:
1. Read and categorized
2. Routed to the correct vault destination
3. Source file archived to `02_processed_archived/`
4. Destination file frontmatter updated
5. Log entry written to `30_KNOWLEDGE_BASE/wiki/log.md`
6. Timestamp file `.last_process_notes` updated

## Routing Decision Tree

Determine the item's **domain** from its filename prefix and content:

| Filename prefix | Domain | Route to |
|---|---|---|
| `T_health` or `health-log` | health | `10_PULSE/Daily_Pulse.md` — add a new date entry newest on top |
| `T_family_gg` or `V_family_gg` | family_gg | Check if info is already in `_cases/active/legal_divorce_court_GG_access.md`. If not, add timeline entry. |
| `T_trading` or stock data | trading | If weekly report → `10_PULSE/020_VNStock_Weekly_Outlook.md`. If research PDF (TCBS/VNDIRECT/broker) → check if content/data already in `021_VNStock_Macro.md`. If yes → archive as source reference dedup. If new data (no matching content in macro file) → extract key findings into `021_VNStock_Macro.md` (newest on top), then archive the PDF. |
| `stock_pending/*.json` | trading | JSON with target_file field — route to that file. Format content matching existing entry format. |
| `V_*` (voice) | varies | Read domain from frontmatter. Voice notes about court → case file. Voice requesting "transcribe and suggest" → classify and route. |
| No clear prefix | _unsorted | Classify by content: health numbers → Daily_Pulse. Family/personal → Daily_Pulse or case. Idea → `_ideas/`. |

## Step-by-Step Workflow

### 1. Inventory
```
Check 01_unprocessed/ for items.
List all files sorted by date (oldest first for chronological processing).
```

### 2. Read and Categorize
For each file:
- Read frontmatter (date, domain, type, source)
- Read content body
- Determine destination using routing tree above

### 3. Process by Type

**Health logs → Daily_Pulse.md:**
- Create a new date entry (newest on top)
- Format: `## YYYY-MM-DD` then `- GG: -`, `- Health: {sleep}h | {quality} | {weight}kg | {fast}h | BP {sys}/{dia}`, `- Money: -`, `- Mind: {1-sentence reflection}`, `- People: -`
- Each line gets `- source: \`_inbox/01_unprocessed/{filename}\``
- If today is >2 days after the health log date, add Mind note: "No update logged for X days"

**Stock/Broker data → Weekly Outlook:**
- JSON files in `stock_pending/`: extract `summary` and `entry_body`
- Format with markdown tables matching existing entries
- Add to top of section (newest on top)
- Update `entries` count in frontmatter
- Add new tickers to `tickers:` list if not already present

**Family/legal → Case file:**
- If information is a new development → add timeline entry to case file
- If information is already referenced in case file or Daily_Pulse → just archive
- If court follow-up date has passed with no update → add CRITICAL GAP alert

### 4. Frontmatter Updates

**Destination file:**
- `last_updated: YYYY-MM-DD` (today)
- `entries: N` — increment count (for cumulative files)
- `tags:` — add new domain-relevant tags if needed
- `tickers:` — add new tickers (for trading files)

### 5. Archive Protocol
```
mv 01_unprocessed/{file} 02_processed_archived/{file}
mv 01_unprocessed/stock_pending/{file} 02_processed_archived/stock_pending/{file}
```
Preserve subdirectory structure.

### 6. Log Entry
Append to `30_KNOWLEDGE_BASE/wiki/log.md`:
```
## YYYY-MM-DD
- **PROCESSED: `/process-notes` cron.** Xử lý N mục trong `_inbox/01_unprocessed/`:
  - {count} health logs → `Daily_Pulse.md`
  - {count} stock data → `020_VNStock_Weekly_Outlook.md`
  - {count} family/legal → archive (đã có trong case file)
  - {count} other → {destination}
- **FLAGGED:** {any red-flag gaps detected}
```

### 7. Timestamp
Update `_inbox/.last_process_notes` with ISO 8601 timestamp.

## Red-Flag Gap Detection

While processing, check for these patterns:

| Pattern | Action |
|---|---|
| Health log gap >3 days (no logs since last entry date) | Add note in daily pulse: "No health logs since {date}" |
| Court follow-up date passed with no update | Add CRITICAL GAP to case file status. Reset follow_up to tomorrow. |
| Daily_Pulse not updated >7 days | Capture-discipline flag (per AGENTS.md red-flag triggers) |
| Stock pending older than 7 days | Flag as stale data |

## Pitfalls

- **Don't assume all items go to Daily_Pulse.** Health logs do. Stock data does NOT — it goes to Weekly Outlook. Family notes go to case files. Read the content carefully.
- **Don't overwrite existing entries.** Daily_Pulse and Weekly Outlook use "newest on top" — always prepend, never append.
- **Don't skip frontmatter updates.** `last_updated`, `entries`, and `last_updated` on the destination file are mandatory per AGENTS.md YAML frontmatter rules.
- **Don't leave orphaned source files.** After processing, every file in `01_unprocessed/` must be moved to `02_processed_archived/` (or deleted if it was a temp/duplicate).
- **Vietnamese in vault output.** Per AGENTS.md HARD CONSTRAINT 7, write vault entries in Vietnamese có dấu. Frontmatter fields can stay English.
- **Stock pending JSONs have `target_file` field.** Use it literally — don't guess the destination. The `entry_body` field contains pre-formatted markdown.
- **Court case sensitivity.** Do NOT assume Warren knows the court date changed or the outcome. Mark as "CRITICAL GAP" rather than filling in missing data.
- **Orphaned stock_pending JSONs.** A `stock_pending/` JSON may reference data that's ALREADY in the target file (e.g. from a previous run or TCBS Research entry with same date/subject). Before routing, grep the target file for the JSON's `subject` or `date`. If found → skip write, archive to `02_processed_archived/stock_pending/`, and note "data already in target file" in the log. Do NOT duplicate entries.
- **stock_pending has `status: pending` but target file already has the entry.** Check by searching the target file for the JSON's `msg_id` or `subject` substring. This happens when a previous cron processed the email but didn't clean up the JSON.

## Verification

After processing:
1. Confirm `02_processed_archived/` has matching file count
2. Confirm destination file has correct updated frontmatter
3. Confirm `log.md` has a new entry for today
4. Confirm `.last_process_notes` timestamp is correct
5. If any items remain in `01_unprocessed/`, flag them as unprocessable with reason

## Cron Job Mode

When running as cron (no user present):
- SILENT rule: If genuinely nothing new to process, respond ONLY "[SILENT]"
- Never ask questions or request clarification
- Produce complete report as final response — system handles delivery
- Court gap detection is NOT "nothing new" — always report it
