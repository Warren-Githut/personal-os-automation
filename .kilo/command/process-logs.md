---
model: deepseek-obsidian/deepseek-v4-pro
description: "Personal log parsing pipeline (auto-detect → select → run → insight check → commit) adapted for ORION+Deepseek toolchain — health, daily pulse, and trading domains."
updated: 2026-06-02
---

# /process-logs (Personal_OS)
# v1.0 | 2026-06-02
# Personal adaptation of the L'Usine /process-logs pipeline.
# Auto-detects inbox files, selects domain parser, runs extraction,
# surfaces wiki-worthy insights, and commits changes.

---

## Usage

```
/process-logs                    # Full flow: scan → select → run → insight check → commit
/process-logs --inventory        # List available parsers and their status
/process-logs --dry-run          # Preview what would be parsed, no writes
```

`--inventory` is safe to run anytime — no files are read or modified.

---

## AUTO-DETECT FLOW

When Warren types `/process-logs`, ORION follows this order:

### Step 1 — Scan inbox
```
list_files(path="_inbox/"):
- *health*.*, *sleep*.*, *weight*.*, *fast*.* → Health log parser
- *stock*.*, *market*.*, *VNIndex*.*, *.csv       → Trading parser
- *pulse*.*, *daily*.*                             → Daily Pulse parser
- *.* (anything else)                               → Ask Warren
```

### Step 2 — Ask Warren
If files match known patterns → list and ask confirm:
```
Found in _inbox/:
  [1] health_data.csv       → run Health parser (050_Health_Log)
  [2] VNIndex_screener.csv  → run Trading parser (020_VNStock_Weekly_Outlook)

Run all? [Y/n] or type number to select:
```

If no files → ask:
```
No new files found in _inbox/.
Which parser do you want to run?
  [1] Health Log       — 050_Health_Log.md (on-demand)
  [2] Daily Pulse      — Daily_Pulse.md (daily)
  [3] Trading/Stock    — 020_VNStock_Weekly_Outlook.md (weekly)
  [4] Connections Log  — weekly_connections_log.md (weekly)
```

### Step 3 — Run parser
Since Personal_OS has no dedicated Python parser scripts yet, ORION processes files directly:

- **CSV/Excel files** → `pandas.read_csv()` / `pandas.read_excel()` → extract key metrics
- **Images (screenshots)** → `lit parse <path>` (OCR) → extract text
- **Text/MD files** → Read tool → parse structured entries
- **PDFs** → `lit parse <path>` → extract text

If Warren selects ≥2 parsers → run in parallel (multiple tool calls in same message).
If Warren selects 1 → run normally, preview output, confirm before writing.

### Step 4 — Cleanup
After successful write → ask Warren if they want to delete source files from `_inbox/`.

---

## Parser Registry

| # | Parser | Script | Source | Output Log | Frequency | Status |
|---|--------|--------|--------|------------|-----------|--------|
| 1 | Health Log | *(none — ORION direct)* | Inbox files, voice notes, manual entry | `050_Health_Log.md` | On-demand | ⚠️ No script |
| 2 | Daily Pulse | *(none — ORION direct)* | Inbox files, Slack notes | `Daily_Pulse.md` | Daily | ⚠️ No script |
| 3 | Trading/Stock | *(none — ORION direct)* | CSV exports, screenshots, notes | `020_VNStock_Weekly_Outlook.md` | Weekly | ⚠️ No script |
| 4 | Connections Log | *(none — ORION direct)* | Inbox files, voice notes | `weekly_connections_log.md` | Weekly | ⚠️ No script |

> **Note:** Personal_OS does not yet have dedicated Python parser scripts under `scripts/`.
> All parsing is done by ORION directly using available tools (pandas, liteparse, Read).
> As the vault matures, parser scripts can be added to `personal_vault/scripts/` — mirroring
> the L'Usine pattern where each parser is a standalone Python script triggered by ORION.

---

## Flag Logic (Health)

| Flag | Condition | Action |
|------|-----------|--------|
| 🔴 | Sleep < 6h or > 9h (persistent 3+ days) | Flag trend, suggest check-in |
| 🔴 | Weight change > 2kg in 1 week | Flag anomaly |
| 🟡 | Fasting < 14h (if intermittent fasting active) | Monitor |
| 🟡 | Sleep 6–6.5h or 8.5–9h | Mild flag, monitor |
| 🟢 | All metrics in healthy range | No action |
| ⚠️ | Missing metric for > 7 days | Flag gap in tracking |

## Flag Logic (Trading)

| Flag | Condition | Action |
|------|-----------|--------|
| 🔴 | Position exceeds stop-loss | Suggest review thesis |
| 🔴 | New buy without thesis page | Flag missing wiki |
| 🟡 | Sector rotation detected | Flag for weekly review |
| 🟢 | Portfolio within plan | No action |

## Log vs Wiki

- **Log (10_PULSE/)** = data + flags + 1-line insight per flag
- **Wiki (30_KNOWLEDGE_BASE/wiki/)** = deep analysis → use `/ingest` afterwards
- ⚠️ **Wiki writes NEVER auto-fire from /process-logs.** Warren must explicitly confirm.

---

## WIKI INSIGHT CHECK (auto after all parsers complete)

*Purpose: After all log entries are written, surface potential wiki-worthy insights for Warren to review. NEVER auto-write to wiki.*

After all parsers finish and logs are written, ORION scans the output and presents:

```
POTENTIAL WIKI INSIGHTS (from this run)

If there are 🔴 flags or noteworthy insights:
  [1] [parser name] | [flag/insight 1-line] | Confidence: [HIGH/MOD]
  [2] [parser name] | [flag/insight 1-line] | Confidence: [HIGH/MOD]

Which to /ingest into wiki? Type number (1, 2...) or "none".
```

**Rules:**
- Only surface items with 🔴 flags OR clear trend breaks vs previous period.
- Each suggestion must include a confidence tag [HIGH/MOD/LOW].
- If Warren selects a number → ORION triggers `/ingest [filename] [domain]` with the corresponding raw file. Do NOT write wiki directly.
- If Warren says "none" → skip. No wiki touched.
- If no noteworthy insights → skip this block silently.

---

## Error Handling

| Error | Handling |
|-------|----------|
| No parser script exists | ORION processes directly (no Python script needed) |
| No files in inbox | Show parser selection menu |
| File fails to parse (corrupt) | Flag ⚠️, ask skip or retry |
| Month/week already has entry | Ask overwrite or merge |
| Abnormal health/trading data | Flag ⚠️, do not crash |

---

## POST-OP: PULSE_INDEX Update

After all parsers complete and logs are written:

1. Read `10_PULSE/PULSE_INDEX.md`
2. Update `last_updated` for each pulse file that was modified
3. Update `last_updated` in frontmatter to today

### Parser-to-PULSE_INDEX mapping

| Parser | PULSE_INDEX Section |
|--------|---------------------|
| Health Log | Health section |
| Daily Pulse | Daily Pulse section |
| Trading/Stock | Trading section |
| Connections Log | Connections section |

---

## --inventory Mode

When Warren runs `/process-logs --inventory`, ORION displays:

```
/process-logs --inventory

Personal_OS Parser Registry
========================================
  [1] Health Log       — 050_Health_Log.md       | Script: none (ORION direct)    | On-demand
  [2] Daily Pulse      — Daily_Pulse.md          | Script: none (ORION direct)    | Daily
  [3] Trading/Stock    — 020_VNStock_Weekly      | Script: none (ORION direct)    | Weekly
  [4] Connections Log  — weekly_connections_log  | Script: none (ORION direct)    | Weekly
========================================

Pipeline status: All parsers operational (ORION direct mode)
Scripts directory: personal_vault/scripts/ — empty (no Python parsers yet)
Source vault: Personal_OS/personal_vault/

Hint: Run /process-logs (without --inventory) to start a processing session.
```

---

## Integration Notes

- **Related commands:** `/daily` (Daily_Pulse.md only), `/weekly` (weekly summary), `/ingest` (wiki ingestion)
- **Dependencies:** pandas, openpyxl, liteparse (all available in Personal_OS environment)
- **PULSE_INDEX.md:** Auto-updated with `last_updated` after each run
- **Git commit:** After all writes confirmed, stage and commit with descriptive message
- **Related L'Usine command:** `Warren_OS_Local/.kilo/command/process-logs.md` — this is the personal adaptation

---

v1.0 | 2026-06-02 | Personal_OS adaptation: health/daily/trading domains, ORION-direct parsing, --inventory flag
