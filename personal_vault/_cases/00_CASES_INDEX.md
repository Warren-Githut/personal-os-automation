---
name: 00_CASES_INDEX
type: index
status: active
domain: personal
last_updated: 2026-07-12
total_entries: 2
scope: personal_vault/_cases
index_first_rule: Always read this file before creating/updating/closing cases; do not hardcode case lists in commands
auto_update: Hermes must update this index whenever a case is created, moved, or closed
refresh_cadence: event-driven
maintained_by: Hermes (auto-sync) + Warren (case owner)
---

# 00_CASES_INDEX — Personal Cases

> Master index for active case threads under `_cases/active/`.
> Pattern: `YYYY-MM_slug.md` with frontmatter (`status`, `domain`, `opened`, `follow_up`, `priority`, `stakeholders`).

---



## 🧭 Where To Go

| Nếu cần… | Thì mở… |
|-----------|---------|
| Active cases | `active/` |
| Closed cases | `closed/` |

## Active Cases

| case_id | title | opened | domain | priority | stakeholders | tags |
|---------|-------|--------|--------|----------|--------------|------|
| `legal_quyen_tham_nom_GG` | Quyền thăm nom GG (Visitation Enforcement) | 2026-07-12 | legal | HIGH | Warren, Khanh, GG | quyền_thăm_nom, visitation, enforcement, open |

> 📂 File: `_cases/active/legal_quyen_tham_nom_GG.md`

## Closed Cases

| case_id | title | opened | closed | domain | priority | outcome |
|---------|-------|--------|--------|--------|----------|---------|
| `legal_divorce_court_GG_access` | Legal Divorce / GG Access | 2026-06-10 | 2026-07-03 | legal | HIGH | Thuận tình ly hôn. Cấp dưỡng 11M/tháng ngày 10. Quyền thăm nom được công nhận. |

> 📂 File: `_cases/closed/legal_divorce_court_GG_access.md`
