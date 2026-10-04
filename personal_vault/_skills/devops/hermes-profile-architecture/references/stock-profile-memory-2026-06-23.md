# stock-profile MEMORY.md — 2026-06-23

Designed via `interview-me` methodology (see SKILL.md → MEMORY.md Design Methodology).

## Process

| Phase | Decision |
|-------|----------|
| Vault path | Root dir + allowed subfolders (not per-file paths) |
| Tool commands | 4 tool/command entries, 1-2 lines each |
| Pulse rules | 4 bullet rules — diacritics, newest first, read-before-write, full YAML frontmatter |
| YAML schema | 1 line listing shared fields across all pulse files |
| Language | English (facts) |
| Format | Bullet sections, no prose |

## Final MEMORY.md

```
VAULT_ROOT = C:/Users/khoans/Documents/Stock_OS/stock_vault
ALLOWED: 10_PULSE/020_VNStock_Weekly_Outlook, 021_VNStock_Macro,
         022_VNStock_Daily_Outlook, 023_VNStock_Sector,
         024-029 (future), 30_KNOWLEDGE_BASE/wiki/investing,
         00_CORE_LOGIC

PULSE RULES:
- Vietnamese with diacritics. Newest entry on top.
- Read latest entry + frontmatter before writing (structural consistency).
- Append after closing ```. Never write inside template.
- Full aggregate YAML frontmatter at file top — auto-update on every change.

TOOL COMMANDS:
- stock-deep-research = deep research 1 ticker (6-section analysis)
- stock-capture = scan _inbox/01_unprocessed/ → append to pulse
- stock-ingest = BCTC PDF ingestion → thesis + anti-thesis
- scripts/stock_capture.py = Python script (manual run)

YAML SCHEMA (shared across all pulse files):
domain, type, status, created, last_updated, tags, brokers, tickers,
sources, report_dates, entries, weeks (weekly only)
```

## Key Insights

- **Read-first discipline** is the single most important pulse rule — prevents template/structure drift without hardcoding a template
- **No template hardcoding** — templates change over time, facts should not. "Read latest entry before write" adapts automatically
- **Tool commands in MEMORY.md, not skill descriptions** — saves context because MEMORY.md is always in the prompt
- **971 bytes used** — well under 2,200 limit, room to grow