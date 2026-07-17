---
name: PULSE_INDEX
type: index
status: active
owner: Hermes / Warren
domain: personal
scope: 10_PULSE/
last_updated: 2026-07-02
index_first_rule: Always read this file before running /daily, /weekly, or /personal-process-logs; do not hardcode pulse file lists
auto_update: Hermes must update this index whenever a pulse file is added/removed/renamed
refresh_cadence: session_start + on every pulse append
---

# PULSE_INDEX — 10_PULSE Master Index

> Master index for all pulse log files in `10_PULSE/`.
> Auto-read by `/daily`, `/personal-morning-brief`, `/personal-process-logs`.

---

## Pulse Files

| # | file | domain | cadence | content | last_updated |
|---|------|--------|---------|---------|--------------|
| 001 | `001_GG_Communication_Guide.md` | family_gg | On-demand | Hướng dẫn trả lời GG về ly thân, câu hỏi nhạy cảm | 2026-06-02 |
| 002 | `002_GG_Milestones.md` | family_gg | On-demand | Những khoảnh khắc đáng nhớ của GG | 2026-06-02 |
| 020 | `020_VNStock_Weekly_Outlook.md` | trading | Weekly | VN stock weekly pulse — macro, sector flow, strategy | 2026-06-06 |
| 021 | `021_VNStock_Macro.md` | trading | On-demand | Active macro narratives tracking | 2026-06-08 |
| 022 | `022_VNStock_Daily_Outlook.md` | trading | Daily | Daily VN stock news headlines from VnExpress RSS | 2026-06-04 |
| 023 | `023_VNStock_Sector.md` | trading | On-demand | Sector narratives tracking | 2026-06-24 |
| 024 | `024_VNStock_Index_Events.md` | trading | On-demand | Index rebalancing & market structure events | 2026-07-02 |
| 050 | `050_Health_Log.md` | health | On-demand | Health metrics, weekly check-in, body signals | 2026-06-01 |
| — | `Daily_Pulse.md` | journal | Daily | 5 bullets/day — all domains | 2026-06-06 |
| — | `weekly_connections_log.md` | meta | Weekly | Cross-domain connections | 2026-05-29 |
| — | `Weekly_Synthesis.md` | meta | Weekly | 7-day pulse → permanent knowledge extraction | 2026-06-06 |

---

## Update Protocol

- Each pulse file = 1 growing file, **newest entry on top**
- When adding/removing a pulse file → update this table + `last_updated` in this file's frontmatter
- When appending a new entry into a pulse file → update that file's `last_updated` and reflect here if needed
- `/personal-process-logs` auto-updates `last_updated` after each run
- All `/daily`, `/weekly`, `/personal-morning-brief` commands must reference this index as the source of truth for pulse files

---



## 🧭 Where To Go

| Nếu cần… | Thì mở… |
|-----------|---------|
| Daily reflection, 5 bullets | `Daily_Pulse.md` |
| Health metrics, sleep log | `050_Health_Log.md`, `051_Sleep_Log.md` |
| VN stock pulse | `020_VNStock_Weekly_Outlook.md` |
| Cross-domain synthesis | `weekly_connections_log.md`, `Weekly_Synthesis.md` |
| Weekly review | `Weekly_Synthesis.md` |

## Cadence Legend

| Cadence | Meaning | Auto-trigger |
|---------|---------|--------------|
| Daily | Entry mỗi ngày | `/daily` |
| Weekly | Entry mỗi tuần | `/weekly`, `/personal-morning-brief` |
| On-demand | Entry khi có dữ liệu/sự kiện | Manual |
| Batch | All pulse files | `/personal-process-logs` |
