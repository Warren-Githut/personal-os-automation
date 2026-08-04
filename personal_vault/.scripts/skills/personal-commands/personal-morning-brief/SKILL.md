---
name: personal-morning-brief
description: "Daily morning brief for Warren — tự động tổng hợp vault state + thị trường + thời tiết + sức khỏe + pháp lý + inbox → 1 brief ngắn gọn, conclusion-first. Cron: hằng ngày 07:00."
version: 1.2
tags: [personal_os, daily, brief, cron, synthesis]
---

# /personal-morning-brief — Daily Morning Brief

## Purpose
Mỗi sáng lúc 07:00 — đọc toàn bộ vault state + live data (thị trường, thời tiết) → compile 1 bản tin ngắn gọn (Tiếng Việt có dấu, conclusion-first) → deliver trực tiếp cho Warren. Không ghi vào vault file — chỉ deliver.

**Trigger:** Cron job mỗi ngày 07:00 (không interactive — auto-deliver)

**Khác với các skill liên quan:**
| Skill | Cadence | Output | Ghi vào vault? |
|-------|---------|--------|----------------|
| `/personal-morning-brief` | **Daily** | Bản tin sáng cho Warren (text) | ❌ Chỉ deliver, không ghi file |
| `/personal-weekly-connections` | Weekly (Sun) | `weekly_connections_log.md` | ✅ 5 cross-domain connections |
| `/personal-context-update` | Weekly (Mon) | PERSONAL_CONTEXT.md §9 update | ✅ 3 themes cho tuần mới |
| `/personal-process-notes` | Daily | Xử lý inbox → vault files | ✅ Ghi pulse/log files |

## Protocol — 7 blocks, execute in order

### Block 0: Load session state
- Đọc `00_CORE_LOGIC/PERSONAL_CONTEXT.md` — đặc biệt §2 (Family), §4 (Health), §11 (Thinking Patterns)
- Đọc `00_CORE_LOGIC/PERSONAL_MEMORY.md` (nếu có) — áp dụng preferences/corrections
- Đọc `00_CORE_LOGIC/PERSONAL_USER.md` — Warren profile
- Đọc `00_CORE_LOGIC/STOCK_CONTEXT.md` (nếu cần market/trading context) — watchlist, catalysts, valuations

### Block 1: Pháp lý & Gia đình 🏛️
- Đọc `_cases/active/*.md` — nếu có
- **Cũng check `_cases/closed/*.md`** — closed cases có thể còn follow_up date cũ chưa dọn
- Check `follow_up` date: nếu hôm nay = follow_up → 🔴 KHẨN
- Tính days_since_last_update: nếu > 7 ngày → 🔴 Critical gap
- Tóm tắt: status, follow_up, next step

### Block 2: Sức khỏe 🏥
- Đọc **cả 3 nguồn health** (không skip dù nguồn trước có vẻ đủ):
  1. `10_PULSE/Daily_Pulse.md` — latest 3-5 entries
  2. `10_PULSE/050_Health_Log.md` — latest health metrics
  3. `10_PULSE/051_Sleep_Log.md` — latest (thường là FRESH nhất)
- **Health data source priority rule:** Với mỗi metric (weight, BP, sleep), dùng entry gần nhất. Không ưu tiên Daily_Pulse mặc định — nó có thể stale. 051_Sleep_Log thường được cập nhật hằng ngày.
- So sánh với baseline từ PERSONAL_CONTEXT.md §4
- **Flags:**
  - Cân nặng: ±2kg từ 63kg. **Sustained > 3 ngày = 🔴**, 1 ngày lẻ = 🟡
  - Huyết áp: ±10 systolic từ baseline (95-99)
  - Sleep: < 6h × 2 đêm liên tiếp
  - Fasting: > 18h kéo dài > 3 ngày
  - Workout: 0 → nhắc
  - LDL/ApoB: chưa có lab > 30 ngày → flag

### Block 3: Thị trường 📊
- **Weekend rule:** Sat/Sun → search ngày giao dịch cuối cùng (Thứ Sáu), không search "hôm nay"
- Web search: "VN-Index {ngày giao dịch cuối}", "dầu Brent giá {ngày}"
- Web search: giá GAS, PVD (search LUÔN — chi phí thấp)
- Đầu tháng/tuần → search macro (FTSE, LDR, chính sách)
- So sánh với STOCK_CONTEXT.md

### Block 4: Inbox & Pending 📥
- Kiểm tra `_inbox/01_unprocessed/` + `_inbox/02_processed_archived/stock_pending/`
- Tính days_since_creation cho file cũ nhất và mới nhất
- Item tồn > 3 ngày = 🟡, > 7 ngày = 🔴

### Block 5: Thời tiết 🌤️
- Web extract: `https://nchmf.gov.vn/kttvSite/vi-VN/1/sai-gon-tp-ho-chi-minh-w15.html`
- Nhiệt độ hiện tại, max hôm nay, xác suất mưa

### Block 6: Hôm nay priorities 🗓️
- 🔴 P0 / 🟡 P1 / 🟢 P2 từ các block trên

### Block 7: Overall assessment 💡
- 1-2 câu + confidence tag + paradox flags

## Output Format (full template — see brief-template.md for copyable version)

```
☀️ **Bản tin sáng — {Thứ, Ngày/Tháng/Năm}**

## 🏛️ 1. PHÁP LÝ {trạng thái}
| Item | Status |
|------|--------|
| {case} | 🔴🟡✅ {chi tiết} |

## 📊 2. THỊ TRƯỜNG {trạng thái}
| Chỉ số | Giá trị | Thay đổi |
|--------|---------|----------|
| VN-Index | {points} ▲▼ | {±%} |
| Dầu Brent | ${price} ▲▼ | {±%} |
| GAS | {price} ▲▼ | {±%} |
| PVD | {price} ▲▼ | {±%} |

## 🏥 3. SỨC KHỎE
| Chỉ số | Hiện tại | Baseline | Xu hướng |
|--------|----------|----------|----------|
| Cân nặng | {weight} | 63kg | 🟢🟡🔴 |

## 📥 4. INBOX & PENDING

## 🌤️ 5. THỜI TIẾT SG

## 🗓️ 6. HÔM NAY
| Priority | Việc | Lý do |
|----------|------|-------|
| 🔴 P0 | {action} | {why} |
```

## Web Search Patterns
- "VN-Index {last_trading_day}"
- "dầu Brent giá {last_trading_day}"
- "GAS cổ phiếu giá {last_trading_day}"
- "PVD cổ phiếu giá {last_trading_day}"
- Macro: "FTSE Vietnam upgrade September 2026", "LDR easing TT 25/2026 Việt Nam"

## Cross-Reference Rules
- PERSONAL_CONTEXT.md → health (§4), family (§2), thinking (§11)
- STOCK_CONTEXT.md → watchlist, valuations, catalysts
- Trust live search > vault if contradictory
- Flag discrepancies > 5%

## Signal Priority
| Signal | Weight |
|--------|--------|
| Legal gap > 7 days | Highest |
| Health sustained breach | High |
| Health single reading | Medium |
| Catalyst stacking | High |
| Paradox | Medium |
| Pending > 7 days | Medium |
| Normal | Low |

## Pitfalls
1. **CONTEXT.md không tồn tại** — Dùng PERSONAL_CONTEXT.md + STOCK_CONTEXT.md.
2. **§9 (This Week) không trong PERSONAL_CONTEXT.md** — Chỉ có trong STOCK_CONTEXT.md.
3. **Daily_Pulse có thể stale** — Check 050_Health_Log + 051_Sleep_Log.
4. **051_Sleep_Log là nguồn fresh nhất** — Paste hằng ngày.
5. **Weight: sustained > 3 ngày = 🔴, 1 ngày = 🟡**.
6. **Inbox thường empty** — Check stock_pending/ riêng.
7. **Weekend: search ngày giao dịch cuối, không "hôm nay"**.
8. **Vault data > 7 ngày cần verify live**.
9. **Confidence untagged = LOW**.
10. **SILENT protocol** — Không có gì mới → "[SILENT]".
11. **Closed cases: stale follow_up** — Check `_cases/closed/*.md`.
12. **Stock_pending tồn lâu** — Tính backlog age.

## Related Skills
- `personal-weekly-connections`, `personal-context-update`, `personal-process-notes`
- `capture-sleep`, `stock-capture`, `personal-inbox-routing`

## MANDATORY VERIFY GATE (rule: never trust LLM, verify everything)

After EVERY parser run that reads Excel/CSV/PDF ([DOMAIN: vault aggregation (sleep, finance, journal)]), MUST run verify-parser-output gate BEFORE reporting numbers or committing.

1. Independent recompute (fresh script, different method).
2. Cross-assert EVERY number (giá, P&L, room, %Δ, số dư, headcount) vs LLM output.
3. Category-drop scan: count raw rows vs filtered; flag dropped (mã rỗng, dòng tổng, Loc=NaN).
4. Emit VERIFY_RESULT: PASS|FAIL + dropped count. Temp hermes-verify-*.py, clean after.
5. FAIL → LLM wrong until proven. Fix logic, re-run, re-verify.
