---
name: stock-deploy-capital
description: "Toàn cảnh trước khi xuống tiền — quét vault + live giá → điểm /100 + valuation trigger → verdict BẮN/CHỜ/TRÁNH. Trigger: 'stock-deploy-capital [ticker|sector|all]'"
version: 1.0.1
tags: [stock, deploy, allocation, synthesis, scoring]
---

# stock-deploy-capital

## Overview

1 lệnh duy nhất tổng hợp TOÀN BỘ dữ liệu từ vault (pulse + wiki thesis + BCTC + watchlist + holdings) → chấm điểm chất lượng /100 + valuation trigger riêng → output verdict-first (BẮN / CHỜ / TRÁNH) + ma trận 2×2 + action cards.

**Không gán xác suất %. Không suy ra "mua" từ điểm số. LLM báo cáo số liệu + pass/fail. Warren tự quyết định.**

## Trigger

```
stock-deploy-capital              → tất cả tickers trong vault (full mode: /100 + pre-flight + valuation 3-người)
stock-deploy-capital GAS          → 1 ticker
stock-deploy-capital GAS HPG MWG  → nhiều ticker
stock-deploy-capital ngân hàng     → cả sector (match tên thư mục trong 020-Sectors/)
stock-deploy-capital --light PNJ  → tư vấn nhanh (skip /100 + pre-flight), chạy valuation 3-người + peer + auto-ghi Catalyst-watch.md
```

> **--light mode (chính là lệnh /an Bố muốn, hợp nhất, KHÔNG tạo lệnh riêng):**
> - Skip chấm điểm /100 + skip pre-flight (FOMO gate)
> - Chỉ chạy valuation module 3-người + peer comp
> - Output: quan điểm giá trị + khung giá mua + có nên xuống tiền không
> - Tự động ghi đề xuất vào `030-Companies/{NNN}-{TICKER}/Catalyst-watch.md` (như PNJ 2026-07-19) — thêm section Entry Trigger + review_log + Required Conditions (nếu chưa đạt điều kiện)
> - Dùng khi: "giá rớt, con nghĩ sao?" — không ingest BCTC mới
> - ⚠️ **GUARD:** Nếu ticker chưa có `Thesis.md` / BCTC trong vault → báo "Cần ingest BCTC trước (`/stock-ingest [ticker]`)", KHÔNG tính PEG rỗng. `--light` chỉ tư vấn trên data ĐÃ có.
> - ⚠️ `--light` KHÔNG thay thế quyết định mua — chỉ quan điểm giá trị. Quyết định xuống tiền vẫn cần full mode + pre-flight.
```

> **`--light` (alias `--an`):** Dùng khi Warren hỏi nhanh "giá rớt, con nghĩ sao". SKIP chấm điểm /100 + SKIP pre-flight gate. Chỉ chạy **Valuation Framework 5A-5E + peer comp** → verdict miệng + **GHI `Catalyst-watch.md`** (như PNJ 2026-07-19). Không ingest BCTC, không tạo Thesis mới. Mọi tickers vẫn phải có đủ 3 nhà đầu tư (xem section Valuation Framework).

## Scan Scope

### Pulse (4 files gần nhất)
```
10_PULSE/020_VNStock_Weekly_Outlook.md
10_PULSE/021_VNStock_Macro.md
10_PULSE/022_VNStock_Daily_Outlook.md
10_PULSE/023_VNStock_Sector.md
```

### Wiki/Investing
```
30_KNOWLEDGE_BASE/wiki/03_Investing/
├── VN_Equities/
│   ├── Candidates_Watchlist.md
│   ├── Holdings.md
│   ├── 030-Companies/{NNN}-{ticker}/        ← số prefix (031-GAS, 032-NLG...)
│   │   ├── Thesis.md
│   │   ├── Anti-thesis.md
│   │   ├── Catalyst-watch.md
│   │   └── BCTC-*.md
│   └── 020-Sectors/{sector}/*.md    ← chỉ khi ticker thuộc sector đó
└── Frameworks.md
```

> **Scan thực tế:** Dùng `find` hoặc `ls` để match thư mục chứa ticker. Không hardcode path `030-Companies/{ticker}/` — dùng wildcard `find 030-Companies/*{TICKER}*/` vì thư mục có số prefix (031-GAS, 032-NLG...)

### Live giá
- `mcp_smart_fetch` CafeF hoặc TCBS cho giá hiện tại
- Nếu fetch fail → báo lỗi rõ: "Không fetch được giá [TICKER]. Vào cập nhật thủ công rồi chạy lại."
- **Không bịa giá. Không fallback sang số cũ trong vault cho mục đích tính MOS.**

## Scoring Model (/100 — chất lượng nội tại)

| # | Nhóm | Trọng số | PASS khi |
|---|---|---|---|
| 1 | Moat | 20 | ROE ≥15% 4/5 năm, Gross margin stable ±5%, Top 3 thị phần |
| 2 | Survival | 20 | D/E <1, Interest coverage >5x, OCF dương 5 năm liên tiếp |
| 3 | Integrity gate | 20 | OCF vs NI divergence <30%, Receivables ≤ revenue growth, Goodwill <30% equity, RPT sạch |
| 4 | Predictability | 10 | Revenue CAGR >5% 5Y, không scandal/restatement, EPS ổn định |
| 5 | Vĩ mô & ngành | 8 | Ngành uptrend/neutral, lãi suất thuận lợi, không chính sách bất lợi đang chờ |
| 6 | Catalyst | 10 | ≥2 driver cụ thể, timeline <6 tháng, không phụ thuộc 1 yếu tố duy nhất |
| 7 | Management, Ownership & Capital Allocation + Anti-thesis | 10 | Capital allocation (buyback timing, bolt-on vs empire), insider ownership thật, institutional vs retail hype, mgmt compensation (equity vesting vs cash bonus), tenure qua ≥1 chu kỳ, cổ tức 5 năm liên tiếp, anti-thesis có trigger cụ thể + có con số, RPT sạch. **CỘNG ĐIỂM:** +2/10 nếu insider THỰC MUA ≥100 tỷ (tiêu chí #9 `management-quality-checklist.md`, SSOT `030-Companies/100_Compliance/Internal_Dealing.md` — actual-only, đăng ký không tính) |
| 8 | State backing | 2 | State ownership >50% hoặc ngành chiến lược (năng lượng, ngân hàng, hạ tầng) |
| | **Tổng** | **100** | |

### Quy tắc chấm điểm
- Mỗi nhóm: PASS toàn bộ = full điểm. PASS 1 phần = điểm tỉ lệ. FAIL toàn bộ = 0.
- **Nhóm 7 (Management, Ownership & Capital Allocation):** chi tiết 8 tiêu chí PASS/FAIL tại `references/management-quality-checklist.md` (SSOT — capital allocation, insider ownership, institutional vs retail, normalized earnings, customer concentration, compensation, tenure, patience). Mỗi tiêu chí binary; 1 sub-criteria fail = cả tiêu chí fail. Điểm tỉ lệ = số tiêu chí PASS / 8 × 10.
- **Thiếu BCTC → SKIP ticker đó.** Output: "SKIP — cần BCTC Q[X]/[Year]."
- **Thiếu 5Y data → ghi rõ:** "Thiếu dữ liệu 5 năm — điểm nhóm X dựa trên dữ liệu có sẵn [LIMITED]."
- Sub-chỉ số breakdown cho từng nhóm → xem `references/scoring-calibration.md`. Bao gồm cả edge cases: ngân hàng (P/B thay P/E, LDR thay D/E, ROE benchmark 12%), BCTC cũ >6 tháng, không đủ 5Y data.

## Valuation Framework — Bảng Ngưỡng Theo Ngành (tra cứu nhanh)

> Chi tiết 5A-5E ở section ngay dưới (BẮT BUỘC từ 2026-07-19). Bảng này là ngưỡng mua mặc định theo ngành để Hermes tra nhanh — Bố sửa nếu cần.

| Ngành | Trọng tâm | Ngưỡng MUA (mặc định) |
|-------|-----------|----------------------|
| Đầu khí / Ngân hàng | P/B vs ROE, Munger 15x | P/B ≤ ROE×0.1, PEGY < 1,5, MOS > 15% |
| Bán lẻ (PNJ/MWG) | PEGY + peer SEA | PEGY < 1,2, P/E < 12x, MOS > 25% |
| BĐS (NLG/NVL) | P/B vs book, SOTP/NAV | P/B < 1,0x book, MOS > 30% |
| Công nghệ (FPT/CMG) | P/E growth-adj, asset-light | P/E < 15x forward, PEG < 1,5 (dùng P/S nếu lỗ) |



> **Warren method chính thức:** kết hợp **Buffett-Munger (Owner Earnings) + Peter Lynch (PEG/PEGY) + Damodaran (SOTP/DCF)**. Định giá **linh hoạt THEO NGÀNH** (không one-size-fits-all). Mọi ticker PHẢI có đủ 3 góc độ — thiếu = pipeline chưa xong. Gold standard template: `031-GAS/Thesis.md` section 5 (5A-5E đầy đủ).

### 5A. Buffett-Munger — Owner Earnings
| Bội số | Công thức | Vai trò |
|--------|-----------|---------|
| 10x (bảo thủ) | 10 × TTM EPS | Floor |
| 15x (công bằng moat) | 15 × TTM EPS | Baseline IV |
| 20x (lạc quan) | 20 × TTM EPS | Ceiling |
> Ngành đặc thù: Ngân hàng dùng **P/B** thay P/E (book = tài sản chính). Đầu khí/dầu khí nhạy giá hàng hóa → luôn kèm stress test (xem 5E).

### 5B. Peter Lynch — PEG / PEGY (BẮT BUỘC)
- **PEG** = P/E ÷ tăng trưởng EPS (%)
- **PEGY** = PEG + Dividend Yield (%) — QUAN TRỌNG cho VN (có cổ tức)
- Ngưỡng **linh hoạt THEO NGÀNH**:
  - Tăng trưởng (FPT, MWG, retail): PEGY < 1,0 hấp dẫn; < 1,5 công bằng
  - Giá trị/defensive (ngân hàng, đầu khí, điện): PEGY < 1,5 ổn; < 2,0 chấp nhận
  - Cyclical (thép HPG, BĐS NLG): PEG ít nghĩa khi EPS âm/biến động → ưu tiên P/B + owner earnings

### 5C. Damodaran — SOTP / DCF
- SOTP theo từng mảng (ngân hàng, đầu khí, bán lẻ có mảng rõ)
- DCF 5 năm = sanity check, độ tin cậy [THẤP] nếu WACC nhạy

### 5D. Peer Comparison (BẮT BUỘC — 2 VN + 2 SEA)
- Mỗi ticker: chọn **2 peer VN + 2 peer Đông Nam Á** cùng ngành
- So sánh: P/E, P/B, ROE, PEGY, tăng trưởng EPS
- Mục đích: phân biệt **structural (ngành) vs idiosyncratic (công ty)** — xem skill `stock-peer-benchmark`
- Peer list theo ngành: (FPT→CMG/MWG VN + GOTO/SEA; ngân hàng→BID/VCB + BCA/Mandiri; đầu khí→GAS/PVD + PTTEP/Medco) — Warren bổ sung khi chạy

### 🔴 Peer-comp Firecrawl-BLOCKED fallback (thực tế 2026-08-02)
Khi Firecrawl credit cạn (web_search/web_extract trả 401/Payment Required) → Warren thường PASTE screenshot bảng định giá ngành (firecrawl/stockinsights: "Định giá ngành Tài chính" có cột Giá/P/E/P/B/EPS/BVPS/Tỷ suất cổ tức).
- **QUY TRÌNH:** liteparse OCR ảnh → extract P/E, P/B, EPS, BVPS → tính ROE = EPS/BVPS → bảng P/B-ROE peer.
- KHÔNG dùng vision_analyze (mất cột, số không chuẩn). liteparse ra bảng sạch.
- Ghi rõ `[MOD-image]` cho mọi số từ screenshot. Thiếu peer (ảnh không có HCM/VND) → ghi `[LIMITED]`, hỏi Warren ảnh tiếp theo.
- Peer CTCK VN thực tế có sẵn từ ảnh: SSI, VCK(VPS), VPX(VPBank Sec), TCX(Kỹ Thương Sec). HCM/VND thường vắng → cần ảnh riêng.

### 5E. Tổng hợp + Stress Test
- IV tổng hợp = trung bình có trọng số 3 method
- Stress test BẮT BUỘC cho ngành nhạy cảm (đầu khí→giá dầu Brent, ngân hàng→NPL/CAR, vàng→giá vàng)

### Chuẩn hóa Template (HARD RULE)
- Mọi `Thesis.md` PHẢI có section "5. Định Giá" với 5A-5E (như GAS). 5 ticker thiếu (NVL, FPT, BID, VCB, PNJ) phải viết lại.
- `stock-ingest` PHẢI generate section 5 này khi tạo Thesis mới.
- ⚠️ **Đừng claim "thiếu PEG/thiếu method" khi chưa check GAS template chuẩn + scan toàn bộ 030-Companies.** Lỗi 2026-07-19: con claim PEG chưa có, thực tế GAS đã có 5B.

## Output Format (VERDICT-FIRST)

### Chat — HTML Dashboard
Render HTML template `templates/report-dashboard.html` với các placeholder được thay bằng số liệu thực tế.

Template gồm:
1. **Header** — ngày + thẻ VERDICT (🔫/⏳/🛑)
2. **Pre-flight** — 3 câu binary (conviction, VN-Index, cash)
3. **Verdict strip** — 3 cột BUY/WAIT/AVOID
4. **Ma trận 2×2** — xếp ticker vào 4 quadrant
5. **Action cards** — mỗi ticker có entry 1, entry 2, stop, exit
6. **Portfolio snapshot** — equity, concentration, cash
7. **Chi tiết** — collapsible bảng điểm /100 từng nhóm (click để xem)

> **Template file:** `templates/report-dashboard.html` là **HTML thật** (render artifact cho chat). CSS + JS + placeholders `[BUY_TICKER]` ... được resolve bằng string replace. **Không** phải .md.

Hiển thị bằng cách render HTML artifact trong chat (output `<details>` hoặc inline HTML).

### Vault — Markdown
```
=== STOCK-DEPLOY-CAPITAL: DD/MM/YYYY ===

🔫 BẮN: GAS (85/100) — MOS 15%, P/E 14.2 vs 5Y 18.5
⏳ CHỜ: HPG (78/100) — MOS 3%, cần giảm thêm 8% về 25.5
🛑 TRÁNH: NVL (42/100) — Fail integrity gate (OCF/NI divergence 45%)

=== PORTFOLIO ===
⚠️  Chưa có holdings — tiền mặt 100%

=== MA TRẬN 2×2 ===
                    RẺ (MOS>10%)         ĐẮT
CHẤT LƯỢNG CAO     🔫 GAS (85/100)       ⏳ HPG (78/100)
(≥70/100)
CHẤT LƯỢNG THẤP    🎲 PVD (55/100)       🛑 NVL (42/100)
(<70/100)

=== ACTION CARDS ===
GAS (85/100)
├── Entry 1: 5% @ 72k (MOS 15%)
├── Entry 2: +5% nếu giảm về 65k (MOS 25%)
├── Stop: Anti-thesis trigger = OCF < 0 2 quý liên tiếp
└── Exit: P/E > 22 hoặc MOS < 0%

=== CHI TIẾT ===
[Warren gõ "detail GAS" để xem bảng điểm chi tiết từng nhóm]
```

### Detail view (khi Warren gõ "detail [TICKER]")
```
GAS — 85/100
├── Moat:            18/20 — ROE 22% (PASS), Gross margin 35% (PASS), #1 gas distribution (PASS)
├── Survival:        20/20 — D/E 0.4 (PASS), Interest coverage 28x (PASS), OCF+ 5Y (PASS)
├── Integrity gate:  18/20 — OCF/NI divergence 12% (PASS), RPT sạch (PASS), Goodwill 5% (PASS)
├── Predictability:   9/10 — CAGR 8% (PASS), no scandal (PASS)
├── Vĩ mô & ngành:    7/8  — Dầu khí ổn định, lãi suất neutral
├── Catalyst:          5/10 — LNG hub Q3/2026, cổ tức 15% (2 drivers, <6 tháng)
├── Mgmt, Ownership & Cap-Alloc:      8/10 — Capital allocation sạch, insider nắm thật, anti-thesis: "nếu nhà nước giảm sở hữu <51%"
└── State backing:    2/2  — PVN sở hữu 96%

Valuation: ✅ PASS — P/E 14.2 < 0.8×18.5, MOS 15%, P/B 2.1 ≤ ROE 22%×0.1=2.2
```

## Pre-flight Gate (hỏi trước khi show output)

> **Bị SKIP hoàn toàn khi chạy `--light` (`--an`).** Mode tư vấn nhanh không cần pre-flight.

Trước khi chạy scan + tính điểm, hỏi Warren 3 câu binary dùng **`clarify` tool với multiple choice**. Không dùng raw text — clarify tool bắt Warren chọn, tránh trả lời mơ hồ.

Choices gộp lại thành 4 combos:
1. `"✅ Conviction | ✅ VN-Index >200 DMA | ✅ Đủ tiền mặt"`
2. `"✅ Conviction | ✅ VN-Index >200 DMA | ❌ Chưa đủ tiền mặt"`
3. `"❌ FOMO | ✅ VN-Index >200 DMA | ✅ Đủ tiền mặt"`
4. `"❌ FOMO / Không rõ — dừng lại"`

```
=== PRE-FLIGHT ===
1. Bạn đang FOMO hay conviction?     [ ] FOMO  [x] Conviction
2. VN-Index trên 200 DMA?            [x] YES   [ ] NO
3. Đủ tiền mặt để mua?               [x] YES   [ ] NO — còn ___ tỷ
```

- Nếu **bất kỳ câu nào là NO/FOMO/thiếu tiền** → dừng, không chạy tiếp. Output: "Pre-flight fail — giải quyết [vấn đề] trước."
- Nếu 3/3 PASS → chạy scan + output đầy đủ.
- Lưu pre-flight answers vào report.

## Save Output

### Chat
Hiển thị đầy đủ verdict + ma trận + action cards.

### Vault — Markdown (growing file)
```markdown
30_KNOWLEDGE_BASE/wiki/03_Investing/VN_Equities/040_Deploy_Capital_Report.md
```

- **File `.md` duy nhất, growing, newest entry on TOP.**
- Cấu trúc file:
  1. YAML frontmatter
  2. `<!-- HERMES TEMPLATE -- Stock Deploy Capital Entry (v1.0) -->` — **HTML comment block** ở đầu content, định nghĩa 6 sections theo thứ tự + format mẫu. Template này để Hermes luôn đọc trước khi write/edit.
  3. Entry mới nhất (markdown, theo đúng thứ tự sections trong template)
  4. Entry cũ hơn bên dưới
- Template format = HTML comment (`<!-- ... -->`), dạng này hiển thị được trong Obsidian edit mode nhưng ẩn khi render.
- Entry format: theo 6 sections trong template — Executive Summary, Pre-flight, Ma trận 2×2, Action Cards, Portfolio Snapshot, Chi tiết bảng điểm (collapsible `<details>`).

## Post-run

Sau khi show output:
1. Hỏi: "Muốn drill-down ticker nào không? (detail [TICKER])"
2. **Web research & logback (nếu deploy verdict là 🔫 BẮN):** Search web để xác nhận luận điểm, phát hiện rủi ro chưa biết (ví dụ: The Great Rotation, FTSE Russell EM upgrade). Log kết quả vào **3 chỗ**:
   - `030-Companies/{NNN}-{TICKER}/Catalyst-watch.md` — thêm catalyst mới + macro risks section
   - `030-Companies/{NNN}-{TICKER}/Thesis.md` — update bull case, entry trigger, BCTC actuals nếu có Q mới
   - `10_PULSE/022_VNStock_Daily_Outlook.md` — pulse entry mới ghi nhận phát hiện
3. Hỏi: "Muốn lưu quyết định hôm nay vào DECISION_LOG.md không?"
4. Nếu Warren chọn BUY → remind cập nhật Holdings.md sau khi khớp lệnh.
5. **Git commit:** Stage tất cả file đã sửa (040_Deploy_Capital_Report.md + Catalyst-watch + Thesis + Daily), commit với message `feat(trading): deploy capital [TICKER] - [score]/100 [verdict]`. (Không ghi vào `_kilo/` — thư mục này đã xóa khỏi vault.)

## Scorecard Review Gate (QA output /100 trước khi gửi — PASS/FAIL)

Mọi output /100 + verdict là artifact cần adversarial review — đừng tự tin dù số học tổng đúng. Rubric 5 trục (SỐ LIỆU · FORMAT · LOGIC · CONSISTENCY/anchors · COMPLETENESS) + ví dụ PNJ 2026-08-01: `references/scorecard-review-checklist.md`.

8 lỗi kinh điển (đều là lỗi thật của PNJ 2026-08-01):
1. **Ngưỡng PHẢI theo `references/scoring-calibration.md` (đã patch 01/08/2026: divergence CHỈ tính chiều NI vượt OCF; OCF >> NI = PASS — kế toán bảo thủ, fix 25/06/2026 theo stock-ingest; jewelry ngưỡng OCF/NI ≥30%)** — PNJ TTM OCF/NI 65,6% → divergence 34% → 3,5/7 (nửa), KHÔNG phải 0/7 theo logic tuyệt đối cũ, cũng không full. Cấm invent threshold riêng; nếu calibration chưa đúng → PATCH calibration kèm backup (`_archives/skills/*.bak`) + sync SKILL.md, đừng tự chấm theo cảm tính.
2. **Check OCF/NI TỪNG NĂM, không chỉ kỳ mới nhất** — PNJ: 2024 OCF/NI 3,9%, 2025 0,7% (divergence 96-99%) → Integrity 20/20 sai.
3. **OCF add-back không bằng tiền** — OCF 1.990 tỷ gồm 1.228 tỷ trích lập dự phòng (865,5 tỷ scandal) → không claim "dòng tiền thật" khi chưa loại add-back.
4. **"5 năm" phải có 5 mốc dữ liệu** — thiếu → ghi [LIMITED]. Receivables dùng quý MỚI NHẤT (PNJ 97→193 tỷ = +99%, không phải "giảm").
5. **Mgmt điểm theo 8 tiêu chí SSOT `references/management-quality-checklist.md`** — cấm trộn legacy (cổ tức 5 năm, anti-thesis trigger, control nội bộ) vào checklist; thiếu Ownership Structure/Normalized Earnings/Patience/One-Line = không traceable.
6. **Action card tự nhất quán với dữ kiện ĐÃ công bố** — stop "mua lại >100% DT" nhưng T7 đã 237% → stop breach → verdict phải TRÁNH, không CHỜ; entry price phải < giá hiện tại (entry ≤36.000 khi giá 31.000 = vô nghĩa).
7. **A3: mọi số mang tag [HIGH]/[MOD]/[LOW]** — output không tag = FAIL ngay.
8. **Valuation phải normalized + forward + sensitivity** — P/E TTM chứa dự phòng one-off không được claim "rẻ" tuyệt đối; PEG growth ex-dự phòng [MOD] "không bền vững" → check value trap; thiếu 5D peer (2VN+2SEA — thiếu peer VN #2 thì ghi [LIMITED]) + stress test ngành = FAIL completeness.
9. **Entry tiers KHÔNG chồng exit line** — Entry 3 ≤25.000 vs Exit "giá <25.000" = mua và bán cùng 1 giá (FAIL vòng 2 PNJ). Entry thấp nhất phải nằm TRÊN exit line, hoặc bỏ tier + ghi "không mua dưới exit line".
10. **Không redefine trigger sau sự kiện (moving goalposts)** — dữ kiện mới (mua lại T7 = 237% DT) vượt ngưỡng stop cũ → nói rõ "đã price vào verdict" + giữ trigger cho kỳ TỚI; đổi cửa sổ (T7→T8-9) phải giải thích tường minh trong file, không âm thầm.
11. **Phân tách "tiền mới" vs "vị thế cũ"** — verdict CHỜ cho tiền mới (cổng scandal đóng) ≠ câu trả lời cho vị thế cũ (giữ có điều kiện + sẵn sàng exit). Ghi cả 2 rõ ràng, không gộp 1 verdict cho 2 quyết định khác nhau.

**Vault cross-check bắt buộc khi review:** `030-Companies/*{T}/Thesis.md` frontmatter `integrity_score` (PNJ vault 7/11 vs output 20/20 = mâu thuẫn), `Anti-thesis.md` (status "đang THẮNG" vs verdict CHỜ), `BCTC - Rolling.md` quý mới nhất, `Holdings.md`/review log số lượng cp (PNJ 1.700 cp @ 50.400 vs output 2.300 cp @ 47.018 = lệch). Vault nằm ở `$HOME/Documents/Stock_OS/stock_vault/` — tìm bằng wildcard, không hardcode.

## Pitfalls

- **🔴 Thêm tín hiệu scoring mới (insider / ESG / dividend...):** xem `references/adding-scoring-signal-playbook.md` — chuỗi 6 file cần chạm + pitfalls (cross-profile guard, actual-vs-registered, ad-hoc 2-step trigger). Worked example: Insider Actual Buy (2026-08-02).
- **🔴 Scoring scheme thay đổi → PHẢI sync `references/scoring-calibration.md` cùng lúc (bài học 01/08/2026):** Khi sửa scoring model trong SKILL.md (đổi tên nhóm, đổi criteria, đổi trọng số) → file `references/scoring-calibration.md` (sub-index breakdown được SKILL.md trỏ tới) PHẢI patch trong CÙNG bundle. Reviewer-node bắt lỗi thật: patch nhóm 7 "Management + Anti-thesis" → "Management, Ownership & Capital Allocation" trong SKILL.md mà calibration vẫn giữ scheme cũ → mâu thuẫn nội bộ, reviewer FAIL vòng 1. Rule: mọi thay đổi scoring = audit cả 2 file (SKILL.md + scoring-calibration.md) + backup cả 2 (`_archives/skills/*.bak`).
- **Không bịa giá:** Live fetch fail → SKIP valuation cho ticker đó, không dùng giá cũ.
- **Thiếu BCTC:** SKIP ticker, không chấm điểm dựa trên dữ liệu không đầy đủ.
- **Không gán xác suất:** Không nói "xác suất thành công 90%". Chỉ báo PASS/FAIL + điểm số.
- **Pre-flight bắt buộc:** Không skip. Không show output nếu FOMO hoặc thiếu tiền.
- **Report file:** File `.md` tại `VN_Equities/040_Deploy_Capital_Report.md`. Không tạo file mới — prepend entry mới vào dưới template comment, trên entry cũ. Update frontmatter entries count + metadata.
- **Detail on-demand:** Output chính không show bảng điểm chi tiết. Chỉ show khi Warren yêu cầu "detail [TICKER]".
- **Ma trận 2×2:** Luôn có trong output. Mỗi ticker mapped vào đúng quadrant dựa trên điểm ≥70 + MOS >10%.
- **Valuation khi thiếu dữ liệu 5Y P/E:** Nếu không có đủ 5 năm BCTC để tính P/E 5Y avg, dùng intrinsic value từ Thesis.md (nếu có) làm giá trị tham chiếu cho MOS. Ghi rõ `[LIMITED]` và không dùng P/E 5Y avg ratio trigger — chỉ MOS + P/B check.
- **Peer SOT + backfill:** `references/peer-mapping.md` là single source cho 2VN+2SEA peers. Khi framework thay đổi (thêm 5A-5E / peer comp), PHẢI audit + backfill TẤT CẢ `Thesis.md` hiện có — đừng assume thesis cũ đã compliance. Phiên 2026-07-19: NVL/FPT/BID/VCB/PNJ thiếu section 5 → backfill thủ công (template đồng bộ: GAS có sẵn 5B PEGY, làm gold standard).
- **DILUTED CANONICAL (Warren directive 2026-08-01):** Khi công ty phát hành thêm CP / split / thưởng CP → LUÔN lấy số CP PHA LOÃNG làm chuẩn chính thống cho MỌI định giá (EPS, P/E, IV, BVPS, Munger). KHÔNG chỉ dùng basic. Bố: *"công ty phát hình cổ phiếu, split, pha loãng ra, nên con lấy số pha loãng cho chính thống luôn ha"*.
  - Tính: `cp_diluted = cp_before + phát_hành`. `EPS_diluted = EPS_basic × (cp_before / cp_diluted)`. Annualized = `EPS_6T_diluted × 2`.
  - PVD 27/07/2026: phát hành 371,86tr cp → 555,88tr → **927,74tr**. EPS diluted annualized **756** vs basic 1.262. P/E diluted @18.100 = **23,9x** (vs basic 14,4x) → đổi verdict VÀNG→**ĐẮT**. IV composite revised ~15.000 (từ 31.000).
  - Áp dụng mọi ticker có event pha loãng trong kỳ (dù event sau ngày lập BCTC — impact forward EPS). Ghi rõ `[HIGH]` nguồn CBTT.

- **Giá SSOT = cron Telegram daily (bài học PNJ 02/08/2026):** Mọi tính toán dùng giá (deal size insider, MOS, P/E) PHẢI lấy từ cron `stock-price-daily` (Entrade/Yahoo, 15:30 T2-T6, sync `Holdings.md` / `Candidates_Watchlist.md`). KHÔNG dùng giá trade-confirmation cũ (giá Bố mua ngày X đã lỗi thời). Web search hết credit → dùng giá vault, KHÔNG bịa. Quy tắc format block vault (decision-first + clickable cross-ref) → `references/vault-block-format.md`.

- **🔴 SSOT COMPLIANCE PATH CHECK (bài học VBB 2026-08-02):** Khi ghi `100_Compliance/Internal_Dealing.md` (insider SSOT) → LUÔN dùng path ROOT `stock_vault/100_Compliance/` (KHÔNG phải `030-Companies/100_Compliance/` hay `30_KNOWLEDGE_BASE/.../100_Compliance/`). Trước `write_file` → chạy `git ls-files | grep "100_Compliance"` (KHÔNG dùng `search_files` — unreliable MSYS, trả rỗng dù file tồn tại). Nếu đã có → MERGE, không tạo mới (tránh 2 bản trùng tên ở 2 path, Bố mở thấy bản sai → tưởng quên ghi).

## Related Skills

- `stock-capture` — ghi tin vào pulse
- `stock-deep-research` — phân tích chuyên sâu 1 ticker
- `stock-ingest` — BCTC → thesis
- `interview-me` — dùng để thiết kế skill này

## MANDATORY VERIFY GATE (rule: never trust LLM, verify everything)

After EVERY parser run that reads Excel/CSV/PDF ([DOMAIN: deploy scoring (capital, allocation)]), MUST run verify-parser-output gate BEFORE reporting numbers or committing.

1. Independent recompute (fresh script, different method).
2. Cross-assert EVERY number (giá, P&L, room, %Δ, số dư, headcount) vs LLM output.
3. Category-drop scan: count raw rows vs filtered; flag dropped (mã rỗng, dòng tổng, Loc=NaN).
4. Emit VERIFY_RESULT: PASS|FAIL + dropped count. Temp hermes-verify-*.py, clean after.
5. FAIL → LLM wrong until proven. Fix logic, re-run, re-verify.
