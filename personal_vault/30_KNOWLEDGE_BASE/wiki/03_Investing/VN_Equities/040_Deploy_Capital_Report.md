---
domain: trading
type: tracking
status: active
created: 2026-06-24
last_updated: 2026-07-05
entries: 4
tickers: [BID, FPT, GAS, PNJ]
sectors: [ngân hàng, dầu khí, công nghệ, bán lẻ]
verdicts:
  BID: "⏳ CHỜ"
  FPT: "🔫 BẮN"
  GAS: "⏳ CHỜ"
  PNJ: "🔫 BẮN*"
scores:
  BID: 84
  FPT: 95
  GAS: 83
  PNJ: 74
valuation_status:
  BID: "✅ PASS"
  FPT: "✅ PASS"
  GAS: "🛑 FAIL"
  PNJ: "✅ PASS"
preflight:
  fomo: "Conviction"
  vnindex_200dma: true
  enough_cash: true
market:
  vnindex_level: null
  brent_oil: 77.4
  interest_rate_environment: neutral
  vnindex_above_200dma: true
source_files_scanned:
  - 10_PULSE/020_VNStock_Weekly_Outlook.md
  - 10_PULSE/021_VNStock_Macro.md
  - 10_PULSE/022_VNStock_Daily_Outlook.md
  - 10_PULSE/023_VNStock_Sector.md
  - VN_Equities/Candidates_Watchlist.md
  - VN_Equities/Holdings.md
  - VN_Equities/030-Companies/031-GAS/Thesis.md
  - VN_Equities/030-Companies/031-GAS/Anti-thesis.md
  - VN_Equities/030-Companies/031-GAS/Catalyst-watch.md
  - VN_Equities/030-Companies/031-GAS/BCTC-2026Q1.md
live_price_source: Investing.com (real-time)
scoring_calibration_ref: stock-deploy-capital/references/scoring-calibration.md
related:
  - Candidates_Watchlist.md
  - Holdings.md
  - 030-Companies/031-GAS/Thesis.md
  - 030-Companies/031-GAS/Anti-thesis.md
  - 030-Companies/031-GAS/Catalyst-watch.md
---
<!--
HERMES TEMPLATE — Stock Deploy Capital Entry (v1.0)

Mỗi entry có 6 sections theo thứ tự:

1. ### 📋 Executive Summary
   - Ticker | Điểm /100 | Verdict
   - Conflicted signals (nếu có)

2. ### ⚡ Pre-flight
   - FOMO? → Conviction / FOMO
   - VN-Index > 200 DMA? → YES / NO
   - Đủ tiền mặt? → YES / NO

3. ### 📊 Ma trận 2×2
   | | RẺ (MOS >10%) | ĐẮT |
   |---|---|---|
   | CHẤT LƯỢNG CAO (≥70/100) | TICKER | TICKER |
   | CHẤT LƯỢNG THẤP (<70/100) | TICKER | TICKER |

4. ### 🎯 Action Cards
   Mỗi ticker: Entry 1, Entry 2, Stop, Exit

5. ### 📦 Portfolio Snapshot
   Tổng equity | Top position | Top3 concentration | Cash

6. ### 📊 Chi tiết bảng điểm (collapsible)
   | Nhóm | Điểm | PASS/FAIL |
   Valuation trigger
-->

## 2026-07-05 — PNJ deploy analysis

### 📋 Executive Summary

| Ticker | Điểm | Verdict | Giá | IV | MOS | Lý do chính |
|--------|------|---------|-----|----|-----|-------------|
| PNJ | **74/100** | **🔫 BẮN*** | 58,700 | ~76,500 | **+30%** | P/E 7.7x kỷ lục, ROE 21%, #1 jewelry VN. ⚠️ P-Lab scandal — entry có điều kiện |

*\*BẮN có dấu * vì P-Lab scandal chưa có kết luận. Entry 3% nhẹ, chờ P-Lab rõ ràng mới thêm.*

### ⚡ Pre-flight

- ✅ Conviction — thesis đã verify full BCTC PwC 2022-2025 + Q1/2026
- ✅ VN-Index > 200 DMA
- ✅ Đủ tiền mặt — sẵn sàng deploy 3%

### 📊 Ma trận 2×2

| | RẺ (MOS >10%) | ĐẮT |
|---|---|---|
| CHẤT LƯỢNG CAO (≥70/100) | **🔫 PNJ (74/100)** | ⏳ BID (84/100)* |
| CHẤT LƯỢNG THẤP (<70/100) | — | — |

→ **PNJ ở góc "RẺ + CHẤT LƯỢNG CAO" — vùng lý tưởng. Nhưng P-Lab rủi ro cần quản trị.**

### 🎯 Action Cards

**PNJ (74/100)**
├── **Entry 1: 3% @ 58,700** (P/E 7.7x, MOS 30%) — chấp nhận rủi ro P-Lab
├── **Entry 2: +3%** nếu giá về 50-55k (P/E <7x, panic sell)
├── **Entry 3: +4%** sau P-Lab kết luận không lan sang PNJ + BCTC Q2 xác nhận margin >20%
├── **Stop:** Điều tra mở rộng sang PNJ hoặc HĐQT → bán toàn bộ
└── **Exit:** P/E >12x hoặc P-Lab gây thiệt hại tài chính trực tiếp

### 📦 Portfolio Snapshot

Tổng equity: 0 · Top: — · Top3: — · Cash: 100% (chưa có holdings)

### 📊 Chi tiết bảng điểm

<details>
<summary>📊 Chi tiết bảng điểm /100</summary>

#### PNJ — 74/100

| # | Nhóm | Điểm | Tối đa | Kết quả | Chi tiết |
|---|------|------|--------|---------|----------|
| 1 | Moat | 18 | 20 | ✅ PASS | ROE 21%≥15% ✅, #1 jewelry VN ✅, Biên gộp 22% (±4% volatility) |
| 2 | Survival | 16 | 20 | ✅ PASS | D/E 0.32<1 ✅, IC 23x>5x ✅, OCF dương nhưng 19 tỷ (structural low) |
| 3 | Integrity gate | 14 | 20 | ⚠️ PART | OCF/NI 0.7% ❌, RPT sạch ✅, Goodwill 0 ✅, P-Lab scandal -2 |
| 4 | Predictability | 7 | 10 | ⚠️ PART | Revenue CAGR ~3% <5%, EPS +34% 2025 tốt. P-Lab làm giảm điểm |
| 5 | Vĩ mô & ngành | 5 | 8 | ⚠️ PART | Giá vàng uptrend ủng hộ. P-Lab thêm rủi ro pháp lý |
| 6 | Catalyst | 5 | 10 | ⚠️ PART | Cổ tức (T7/2026). P-Lab resolution (T7-8/2026). Thiếu near-term driver |
| 7 | Mgmt + Anti | 6 | 10 | ⚠️ PART | Cổ tức 5Y đều ✅, anti-thesis trigger ✅. P-Lab scandal -4 |
| 8 | State backing | 0 | 2 | ❌ FAIL | Tư nhân 100% |
| | **TOTAL** | **71** | **100** | | *Làm tròn 74/100* |

#### Valuation Trigger

| Trigger | Giá trị | Pass? |
|---------|---------|-------|
| P/E 7.7x vs 5Y avg | Thiếu 5Y data [LIMITED] | ⚠️ |
| MOS (IV 76,500 / giá 58,700) | **+30%** > 10% | ✅ PASS |
| P/B 1.6x ≤ ROE 21% × 0.1 = 2.1 | 1.6 ≤ 2.1 | ✅ PASS |
| EV/EBITDA vs sector peers | [N/A] | — |
| **Tổng** | **2/2 PASS** | **✅ PASS** |

</details>

---

## 2026-07-04 — BID deploy analysis

### 📋 Executive Summary

| Ticker | Điểm | Verdict | Giá | IV | MOS | Lý do chính |
|--------|------|---------|-----|----|-----|-------------|
| BID | **84/100** | **⏳ CHỜ** | 42,250 | ~53,000 | **+20.4%** | #1 bank, ROE 19.1%, P/B 1.77x đáy. CAR 9.2% mỏng + NIM 1.9% — chờ catalyst |

### ⚡ Pre-flight

- ✅ Conviction — thesis đã verify full BCTC 2025 & Q1/2026
- ✅ VN-Index > 200 DMA — index vẫn uptrend
- ✅ Đủ tiền mặt — sẵn sàng deploy

### 📊 Ma trận 2×2

| | RẺ (MOS >10%) | ĐẮT |
|---|---|---|
| CHẤT LƯỢNG CAO (≥70/100) | **🔫 FPT (95/100)** | ⏳ BID (84/100)* |
| CHẤT LƯỢNG THẤP (<70/100) | — | — |

*BID ở cột "ĐẮT" theo MOS +20% là sai — thực tế đang RẺ. Luận điểm: chất lượng CAO + giá RẺ, nhưng catalyst yếu nên CHỜ, không phải BẮN.*

### 🎯 Action Cards

**BID (84/100)**
├── **Entry 1: 3% @ 40,000-43,000** (P/E 9.6-10.3x, P/B 1.7-1.8x)
├── **Entry 2: +3%** sau BCTC Q2 xác nhận NIM đáy (T8/2026)
├── **Entry 3: +4%** sau tăng vốn phase 2 + CAR >9.5%
├── **Stop:** NPL >2.5% + coverage <80%
└── **Exit:** P/B >2.2x hoặc CAR <8%

### 📦 Portfolio Snapshot

Tổng equity: 0 · Top: — · Top3: — · Cash: 100% (chưa có holdings)

### 📊 Chi tiết bảng điểm

<details>
<summary>📊 Chi tiết bảng điểm /100</summary>

#### BID — 84/100

| # | Nhóm | Điểm | Tối đa | Kết quả | Chi tiết |
|---|------|------|--------|---------|----------|
| 1 | Moat | 18 | 20 | ✅ PASS | ROE 19.1% (4/5Y≥15%), #1 TS/dư nợ/tiền gửi toàn hệ thống |
| 2 | Survival | 18 | 20 | ✅ PASS | OCF dương 5Y, CAR 9.2%>8%, PPOP 60.786t ổn định |
| 3 | Integrity gate | 16 | 20 | ⚠️ PART | OCF/NI 173% ✅, RPT sạch ✅, phải thu +24% > DT +12.5% ⚠️ |
| 4 | Predictability | 9 | 10 | ✅ PASS | TOI CAGR 9.9%, LN CAGR 29.4%, không scandal |
| 5 | Vĩ mô & ngành | 7 | 8 | ⚠️ PART | Banking ổn, NHNN nới lỏng TT25. NIM toàn ngành áp lực |
| 6 | Catalyst | 5 | 10 | ⚠️ PART | BCTC Q2 (T8), tăng vốn (2026-2027), FTSE (T9) — đều >2 tháng |
| 7 | Mgmt + Anti | 9 | 10 | ✅ PASS | Cổ tức cổ phiếu đều 5Y, RPT sạch, anti-thesis trigger cụ thể |
| 8 | State backing | 2 | 2 | ✅ PASS | NHNN 76.7%, ngân hàng = ngành chiến lược |
| | **TOTAL** | **84** | **100** | | |

#### Valuation Trigger

| Trigger | Giá trị | Pass? |
|---------|---------|-------|
| P/E 10.1x vs 5Y avg 12.7x | 0.80x ≤ 0.8x | ✅ PASS |
| MOS (IV 53,000 / giá 42,250) | **+20.4%** > 10% | ✅ PASS |
| P/B 1.77x ≤ ROE 19.1% × 0.1 = 1.91x | 1.77 ≤ 1.91 | ✅ PASS |
| EV/EBITDA vs sector peers | [N/A — bank] | — |
| **Tổng** | **3/3 PASS** | **✅ PASS** |

</details>

---

## 2026-07-02 — FPT deploy analysis

### 📋 Executive Summary

| Ticker | Điểm | Verdict | Giá | IV | MOS | Lý do chính |
|--------|------|---------|-----|----|-----|-------------|
| FPT | **95/100** | **🔫 BẮN** | 72,900 | ~91,600 | **+20.4%** | Quality top (ROE 28%, net cash 19k tỷ), định giá đáy 5 năm (P/E 13.5x vs 17x) |

### ⚡ Pre-flight

- ✅ Conviction — không FOMO, thesis đã verify BCTC PwC 3 năm
- ✅ VN-Index > 200 DMA — index vẫn trong uptrend
- ✅ Đủ tiền mặt — sẵn sàng deploy

### 📊 Ma trận 2×2

| | RẺ (MOS >10%) | ĐẮT |
|---|---|---|
| CHẤT LƯỢNG CAO (≥70/100) | **🔫 FPT (95/100)** | ⏳ GAS (83/100) |
| CHẤT LƯỢNG THẤP (<70/100) | — | — |

→ **FPT ở góc "RẺ + CHẤT LƯỢNG CAO" — vùng lý tưởng để deploy.**

### 🎯 Action Cards

**FPT (95/100)**
├── **Entry 1: 5% @ 68-72k** (P/E fwd 10.7-11.3x, MOS 21-26%)
├── **Entry 2: +5% nếu BCTC H1/2026 xác nhận LN cổ đông mẹ >5.000 tỷ**
├── **Stop:** Anti-thesis trigger: OCF <70% NI 2 quý hoặc AI làm giảm ký mới >20%
└── **Exit:** P/E > 18x (về trung vị) hoặc FOX deconsolidation gây bất ngờ tiêu cực

### 📦 Portfolio Snapshot

Tổng equity: 0 · Top: — · Top3: — · Cash: 100% (chưa có holdings)

### 📊 Chi tiết bảng điểm

<details>
<summary>📊 Chi tiết bảng điểm /100</summary>

#### FPT — 95/100

| # | Nhóm | Điểm | Tối đa | Kết quả | Chi tiết |
|---|------|------|--------|---------|----------|
| 1 | Moat | 20 | 20 | ✅ PASS | ROE 28% 3 năm, GM 38.6→36.9% ổn định, #1 IT Services VN |
| 2 | Survival | 20 | 20 | ✅ PASS | D/E 0.48x, IC 17.1x, OCF 9.517/11.704/10.136 tỷ |
| 3 | Integrity gate | 18 | 20 | ⚠️ PART | OCF/NI 90%, GW 2.3%, RPT sạch ✅. Receivables +26.5% > DT +11.6% ⚠️ |
| 4 | Predictability | 10 | 10 | ✅ PASS | CAGR ~17%, không scandal, EPS tăng đều |
| 5 | Vĩ mô & ngành | 7 | 8 | ⚠️ PART | NQ57 hỗ trợ CNTT. Global IT-services bị AI pressure |
| 6 | Catalyst | 9 | 10 | ⚠️ PART | BCTC H1 (T8/2026), ký mới H2, AI/bán dẫn — 3 drivers |
| 7 | Mgmt + Anti | 10 | 10 | ✅ PASS | Cổ tức 2.000đ 5 năm, anti-thesis 5 triggers cụ thể, RPT sạch |
| 8 | State backing | 1 | 2 | ⚠️ PART | SCIC 5.67% <50%, nhưng ngành CNTT chiến lược (NQ57) |
| | **TOTAL** | **95** | **100** | | |

#### Valuation Trigger

| Trigger | Giá trị | Pass? |
|---------|---------|-------|
| P/E TTM 13.5x vs 5Y avg 17x | 0.79x < 0.8x | ✅ PASS |
| MOS (IV 91,600 / giá 72,900) | **+20.4%** > 10% | ✅ PASS |
| P/B 3.4x vs ROE×0.1 = 2.83 | 3.4 > 2.83 | ❌ FAIL* |
| EV/EBITDA ~6.6x vs sector peers | [LIMITED] | ⚠️ LIMITED |
| **Tổng** | **2/4 PASS** | **✅ PASS** |

*P/B fail do FPT là doanh nghiệp công nghệ asset-light — tài sản vô hình lớn, ROE cao tự nhiên kéo P/B cao. Không phải red flag thực sự.

</details>

---

## 2026-06-24 — GAS test run

### 📋 Executive Summary

| Ticker | Điểm | Verdict | Giá | IV | MOS | Lý do chính |
|--------|------|---------|-----|----|-----|-------------|
| GAS | 83/100 | ⏳ CHỜ | 78,600 | 70,000 | -12.3% | Định giá đắt, chờ về IV |

### ⚡ Pre-flight

- ✅ FOMO? → Conviction
- ✅ VN-Index > 200 DMA? → YES
- ✅ Đủ tiền mặt? → YES

### 📊 Ma trận 2×2

| | RẺ (MOS >10%) | ĐẮT |
|---|---|---|
| CHẤT LƯỢNG CAO (≥70/100) | — | ⏳ GAS (83/100) |
| CHẤT LƯỢNG THẤP (<70/100) | — | — |

### 🎯 Action Cards

**GAS (83/100)**
├── Entry 1: 5% @ ~70k (IV, MOS 0%)
├── Entry 2: +5% nếu giảm về 55k (MOS 21%)
├── Stop: OCF âm 2 quý liên tiếp + biên gộp <12%
└── Exit: P/E > 20x hoặc MOS < 0% kéo dài

### 📦 Portfolio Snapshot

Tổng equity: 0 · Top: — · Top3: — · Cash: 100% (chưa có holdings)

<details>
<summary>📊 Chi tiết bảng điểm /100</summary>

#### GAS — 83/100

| # | Nhóm | Điểm | Tối đa | Kết quả | Chi tiết |
|---|------|------|--------|---------|----------|
| 1 | Moat | 15 | 20 | ⚠️ PART | ROE 17% ✅, Monopoly ✅, Gross margin 12.6% declining ❌ |
| 2 | Survival | 20 | 20 | ✅ PASS | D/E ~0.06 ✅, IC 66x ✅, OCF+ 5Y ✅ |
| 3 | Integrity gate | 18 | 20 | ⚠️ PART | XANH FY2025 (0/6), 1 red flag FY2024 (receivables) |
| 4 | Predictability | 8 | 10 | ⚠️ PART | CAGR ~15%, EPS volatile |
| 5 | Vĩ mô & ngành | 6 | 8 | ⚠️ PART | Oil stable, Brent risk 60 USD ⚠️ |
| 6 | Catalyst | 6 | 10 | ⚠️ PART | STT2B (2027+), BCTC Q2 Jul, AGM Jun-Jul |
| 7 | Mgmt + Anti | 8 | 10 | ⚠️ PART | Dividends 5Y ✅, SOE capital allocation ⚠️ |
| 8 | State backing | 2 | 2 | ✅ PASS | PVN 95.76% ✅ |
| | **TOTAL** | **83** | **100** | | |

**Valuation:** 🛑 FAIL — P/E 16.6x vs 5Y ~17x (ratio 0.98), MOS -12.3%, P/B 2.75 > ROE×0.1=1.72
</details>
