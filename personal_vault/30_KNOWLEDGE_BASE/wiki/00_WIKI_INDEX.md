---
name: 00_WIKI_INDEX
type: index
status: active
domain: personal
last_updated: 2026-07-19
total_files: 22
scope: personal_vault/30_KNOWLEDGE_BASE/wiki
index_first_rule: Always read this file before citing personal wiki pages; if a referenced page is missing, update here instead of searching blindly
auto_update: Hermes must update this table whenever wiki files are added/removed/renamed
refresh_cadence: session_start + on every wiki ingest
related_paths:
  - 30_KNOWLEDGE_BASE/wiki/
  - 10_PULSE/00_PULSE_INDEX.md
---

# 00_WIKI_INDEX — Personal OS

> Master index. Scan Key Insights column → open right file.

---

## 01_GG/

| file | period | type | key_insights | last_updated |
|------|--------|------|---------------|--------------|
| `01_GG/aa_About_GG/02_GG_Genetic_Profile.md` | 2024-03 | reference | IQ 9/10 (top 8%), toán 9/10 (top 9%), âm nhạc 7.5; ngôn ngữ yếu 4/10 (bottom 40%); nóng tính 7.5, kỷ luật thấp 4; béo phì risk 7.5 | 2026-06-06 |
| `01_GG/aa_About_GG/03_Calendar_GG.md` | ongoing | tracking | Lịch sự kiện GG | — |
| `01_GG/aa_About_GG/01_about_GG.md` | 2026-2027 | reference | TH Minh Đạo (Lớp 1, 2026-2027), hồ sơ nhập học, info cá nhân (định danh masked) | 2026-07-14 |

---

## 03_Investing (MOVED)

> ⚠️ Stock domain đã tách sang `Stock_OS/stock_vault/30_KNOWLEDGE_BASE/wiki/03_Investing/`.
> Personal_OS không còn dữ liệu cổ phiếu. Query stock → mở Stock_OS vault.

---

## 02_Health/

| file | period | type | key_insights | last_updated |
|------|--------|------|---------------|--------------|
| `02_Health/aa_Bloodwork_Health_Baseline/000_Bloodwork_Health_Baseline.md` | 2026-06 | reference | 171cm/63kg/BMI 21.5, fasting 16:8; mỡ máu LDL cao nhưng TG/HDL tuyệt vời (0.23-0.56, nhạy insulin) | 2026-07-19 |
| `02_Health/aa_Bloodwork_Health_Baseline/100_Biomarker_Interpretation.md` | 2026-07 | reference | Cách đọc chỉ số máu (knowledge, tách khỏi data) — TG/HDL ratio: <2 tuyệt vời, >3 kháng insulin | 2026-07-19 |
| `02_Health/Morning_Routine.md` | 2026-05 | reference | Morning routine protocol — wake, weigh, fast, move, think | — |
| `aa_About_Me/01_Warren_Profile.md` | 2026-06 | reference | Personal profile — life priorities, key relationships, communication style | — |
| `02_Health/ab_Doctor_Reports/2026-06-02_personal_doctor.md` | 2026-06 | analysis | Baseline health assessment — 10 bloodwork records (2024-2026), comprehensive panel review | — |

---

## 04_Growth/

| file | type | status | key_insights | last_updated |
|------|------|--------|---------------|--------------|
| `04_Growth/Reading_Log.md` | log | active | Books + one-line takeaways | — |

---

## meta/

| file | type | status | notes | last_updated |
|------|------|--------|-------|--------------|
| `meta/DECISION_LOG.md` | log | active | Key vault decisions — rationale behind every structural change | — |
| `meta/log.md` | log | active | Wiki change log — every ingest, lint, major wiki write | — |

---



## 🧭 Where To Go

| Nếu cần… | Thì mở… |
|-----------|---------|
| Hồ sơ GG, calendar, gift tracking | `01_GG/aa_About_GG/` |
| Health baseline, doctor reports, genetics | `02_Health/` |
| VN equities thesis, BCTC, watchlist | `Stock_OS/stock_vault/30_KNOWLEDGE_BASE/wiki/03_Investing/` (đã tách) |
| Reading log, development | `04_Growth/` |
| Tất cả decisions | `DECISION_LOG.md` |
| Wiki change log | `log.md` |

## Update Protocol

- Append newest entries at the top of each section
- Update `last_updated` in the Properties block whenever this file changes
- If a referenced wiki file is missing, mark it stale here rather than silently skipping it
