---
name: "STOCK_USER"
type: "user_profile"
status: "active"
version: "2026-06-28"
created: "2026-06-28"
last_updated: "2026-06-28"
tags: [user, preferences, trading-style]
domain: "stock"
---

# USER — Stock Profile

> **Hồ sơ Warren trong context stock-profile.**
> SSOT: `00_CORE_LOGIC/STOCK_USER.md` — sync → `personal_vault/00_CORE_LOGIC/STOCK_USER.md`
> Update khi có preference mới / thay đổi. Warren approve trước khi ghi.

---

## Thông tin cơ bản

- **Tên:** Warren
- **Location:** Saigon
- **Style:** Buffett-Munger — few bets, big bets, long holds. All-in + DCA conviction.
- **Tính cách:** System-thinker, hay quên chi tiết nhỏ, skeptical cross-checker.
- **Broker chính:** TCBS. Cross-check: VPS, HSC, Vietcap.
- **Portfolio hiện tại:** Không có holdings. Đang watch: GAS + banks.

---

## Giao tiếp (stock context)

- **Ngôn ngữ:** Tiếng Việt + English terms (OCF, NI, EPS, P/E, backlog, margin, OCF...)
- **Format:** 3-5 bullet kết luận đầu. Max 5 dòng. Conclusion first.
- **Tone:** Blunt to the point of rude. Không "maybe", "however", "on the other hand".
- **Template ưa thích:**
  - "Don't buy."
  - "Data is garbage. WAIT for Q3 BCTC."
  - "Fail 2/5 integrity gate. Next."
  - "Solid. Thesis holds. Valuation is tight — wait for a 10% dip."
- **Pet peeves:**
  - Phân tích không có source
  - Recommendations không kèm risk assessment
  - Lý thuyết dài không có số
  - Advice ngoài lề không liên quan stock

---

## Yêu cầu dữ liệu

- **Confidence tags bắt buộc:**
  - `[HIGH]` = audited BCTC / user-provided verified document
  - `[MOD]` = unverified report, web search, broker report
  - `[LOW]` = estimate, training knowledge, inference with no source
- **So sánh > số tuyệt đối.** Ratios > raw. % change > snapshot.
- **Không guess, không fabricate.** Thiếu data → nói "WAIT: missing X."

---

## Trading style

- **VN equities = core** — long-term, value-based, intrinsic-value-driven
- **BTC = DCA** — opportunistic
- **Polymarket ≤5%** — speculative, mental & capital segregated
- **Không bao giờ** refill speculative buckets từ core capital
- **Long-term thesis required** cho mọi decision. No rumors. No FOMO.

---

## Stock workflow ưa thích

| Workflow | Chi tiết |
|---|---|
| **Integrity gate** | /audit [ticker] — check OCF vs NI, receivables, related-party, goodwill |
| **Valuation** | Intrinsic = P/E 5Y avg × TTM EPS [HIGH]. MOS >10%. P/B ≤ ROE×0.1 |
| **Deploy capital** | /100 score + valuation → verdict-first. Post-run=git commit |
| **BCTC ingest** | PDF → thesis + anti-thesis. 11 integrity checks, PASS≥7/11 |
| **Deep research** | 6-section analysis từ broker reports |

---

## Stock bundles & commands (stock-profile)

> **Bundle = gõ 1 lệnh `/tên-bundle` thay vì load nhiều skill riêng lẻ.**
> Tất cả bundle đều có thể gõ trực tiếp trong chat với Hermes.

### 🎯 `/stock-deploy` — Trước khi mua cổ phiếu

**Dùng khi:** Có ticker muốn research + check sức khỏe + chấm điểm trước khi xuống tiền.

| Trong bundle | Nó làm gì? |
|---|---|
| `stock-deep-research` | Research 6 mục từ broker reports + web |
| `stock-ingest` | Đọc BCTC, chạy 11 bài kiểm tra Integrity Gate |
| `stock-deploy-capital` | Chấm điểm /100 + valuation → verdict BẮN/CHỜ/TRÁNH |
| `bctc-pdf-ingest` | Đọc PDF BCTC kiểm toán → update số liệu thật |

**Cách dùng:**
- `/stock-deploy GAS` — research + score 1 ticker
- `/stock-deploy GAS HPG MWG` — nhiều ticker cùng lúc
- `/stock-deploy all` — quét toàn bộ watchlist

**Cron:** ❌ Không. Dùng theo sự kiện (khi có BCTC mới / muốn mua).

---

### 📊 `/weekly-macro` — Check bức tranh vĩ mô

**Dùng khi:** Muốn biết môi trường đầu tư đang thế nào (Chủ Nhật xem cron chạy, hoặc chủ động check).

| Trong bundle | Nó làm gì? |
|---|---|
| `macro-frameworks` | Tự động check 6 chỉ số (Brent, DXY, USD/VND, VN-Index, NHNN, VIBOR) Chủ Nhật 14h. Nếu breach threshold → append entry + Telegram. Im lặng nếu không có gì đặc biệt. |

**Cách dùng:**
- Cần làm gì đâu — cron tự chạy Chủ Nhật 14:00, báo Telegram nếu có biến động
- Gõ `/weekly-macro` nếu muốn check chủ động: Hermes show Frameworks.md

**Cron:** ✅ Chủ Nhật 14:00 (tự động, zero LLM cost, no_agent Python script)

**Lưu ý:** Polymarket bị loại khỏi bundle này — là skill riêng, dùng khi cần check prediction market odds. Gõ `polymarket` để hỏi.

---

### 🏗️ `/vault-health` — Spring cleaning vault

**Dùng khi:** Đầu tháng hoặc khi vault bừa bộn.

| Trong bundle            | Nó làm gì?                                                     |
| ----------------------- | -------------------------------------------------------------- |
| `vault-structure-audit` | Audit toàn bộ vault: folder, tag, link, frontmatter → điểm /10 |
| `tidy`                  | Dọn inbox, archive case cũ, xóa folder deprecated              |
| `vault-ops-automation`  | Đồng bộ index, sửa frontmatter, check data freshness           |
|                         |                                                                |

**Cách dùng:**
- `/vault-health` — chạy audit (dry-run, an toàn)
- `/vault-health --execute` — apply các fix

**Cron:** Đề xuất Chủ Nhật đầu tháng (chưa setup, anh bảo tôi setup).

---

### 📋 Các lệnh stock riêng lẻ (không bundle, vẫn xài được)

| Lệnh | Khi nào dùng |
|---|---|
| `/audit GAS` | Chạy Integrity Gate 5 mục cho 1 ticker |
| `deep research GAS` | Research sâu 1 ticker từ broker + web |
| `/stock-ingest` | Nhét BCTC mới vào vault (kèm PDF) |
| `stock-deploy-capital GAS` | Chấm điểm nhanh 1 ticker (không cần bundle) |
| `polymarket` | Check tỷ lệ cá cược prediction market |
| `macros` hoặc "check macro" | Xem Frameworks.md mới nhất |

## Kết nối với personal_profile

Warren là **cùng 1 người**, nhưng:

| Profile | Góc nhìn | File |
|---|---|---|
| stock-profile | Investor — VN equities, BTC, Polymarket | `STOCK_USER.md`, `STOCK_CONTEXT.md` |
| personal_profile | Con người hằng ngày — health, family, work | `PERSONAL_USER.md`, `PERSONAL_CONTEXT.md` |

**Hard rule 1 — Memory write protection:** KHÔNG tự động ghi vào STOCK_MEMORY.md, USER.md, mem0 nếu Warren không nói "ghi" hoặc approve. Chỉ append vào `personal_vault/_inbox/_stock_profile_memory_raw.md` khi có lệnh. **Built-in memory** (`memory` tool) auto-saves mặc định.

**Hard rule 2 — Personal domain cấm tuyệt đối:** KHÔNG được read/grep/search vào `30_KNOWLEDGE_BASE/wiki/02_Health/`, `10_PULSE/Daily_Pulse.md`, `10_PULSE/050_Health_Log.md`, `10_PULSE/051_Sleep_Log.md`, `00_CORE_LOGIC/PERSONAL_*`, `_cases/active/`. Đây là domain của personal_profile, stock-profile không đụng tới.
