# CONTEXT.md Section Audit Map (2026-07-25)

> Hermes đọc CONTEXT.md đầu mỗi session (line 11). Warren KHÔNG mở file này.
> Nguyên tắc: xóa chỉ ảnh hưởng Hermes function, không ảnh hưởng Warren (Bố dùng Telegram).
> Source: session simplify audit 2026-07-25 (trước commit `3147bc9`).

| Section | Ai cần | Loại | Verdict |
|---------|--------|------|---------|
| §1 WARREN Profile | Con | state | GIỮ |
| §2 Store Snapshot | Con | state | GIỮ |
| §2.5 Store Leaders | Con | SSOT (leaders) | GIỮ |
| OPS CALENDAR (rỗng) | — | dead | **XÓA** (đã xóa) |
| §3 Vault Architecture | Con | map | GIỮ; sửa `scripts/`→`.scripts/` |
| §3.5 Glossary | Con | domain SSOT | GIỮ (con cần định nghĩa Party Size/Straddle/🟡SỚM) |
| §3.5 MANPOWER SSOT | Con | domain SSOT | GIỮ (đọc Manpower_Master, KHÔNG đoán) |
| §3.5 CPH SSOT | Con | domain SSOT | GIỮ (vacant=0 KHÔNG phải bug) |
| §3.5 DATA SSOT | Con | mirror WARREN_MEMORY | **GỘP → 1 dòng ref** |
| §4A Data Inflows | Con | tra khi ingest | GIỮ |
| §4B 16 jobs | Con | cron SSOT | GIỮ (từ jobs.json) |
| §4C Command Quick Map | Con/Bố | redundant vs `using-agent-skills` (đã gom 12 Matt technique + bảng cầm tay) | **XÓA** (đã xóa) |
| §5 W29 (stale W30) | Con | state | GIỮ; đổi title "LAST CLOSED W29" |
| §6A Decision Style | Con | cognitive | GIỮ |
| §6B Cognitive Patterns | Con | cognitive | GIỮ |
| §6C Comm Preferences | Con | mirror SOUL §4 | **GỘP → ref** (đã làm) |
| §6D Trusts/Questions | Con | unique | GIỮ |
| §6E Active Constraints | Con | stale (moratorium) | **GỘP**: xóa moratorium, giữ OIL |

## Lessons
- "Viết cho ai đọc?" là câu hỏi SAI khi file là Hermes-load. Đúng: "xóa ảnh hưởng function không?"
- Redundant vs SKILL (không phải vs SSOT file) = safe delete. §4C trùng `nonit-using-agent-skills` router → Bố duyệt xóa.
- Domain SSOT (Glossary/MANPOWER/CPH) = KEEP — xóa là con mất định nghĩa, sẽ đoán bậy.
- Cron-doc: CONTEXT §4B là SSOT cho cron NHƯNG phải sync từ `cron/jobs.json` (16 jobs thực). Đừng viết từ ký ức.
- Menu GP: jobs.json có `menu-gp-accumulate` weekly → file cũ ghi "monthly manual" là SAI, sửa thành weekly auto.
