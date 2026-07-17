---
domain: trading
tags: [trading, watchlist, candidates, VN-equities, fundamental, entry-pending]
type: tracking
status: active
last_updated: 2026-07-17
tickers: [BID, FPT, GAS, HPG, MWG, NLG, PNJ, PVD, VCB]
source_files:
  - "BCTC kiểm toán hợp nhất (EY, Deloitte, PwC) — các năm"
  - "TCBS Research first coverage reports"
  - "BCTC tự tổng hợp từ các nguồn"
  - "MWG BCTC Q1/2026 (BCTC hợp nhất giữa niên độ tự lập, ký 24/04/2026)"
related: [Holdings.md, Watchlist.md, 030-Companies/031-GAS/Thesis.md, 030-Companies/032-NLG/Thesis.md, 030-Companies/034-PVD/Thesis.md, 030-Companies/035-HPG/Thesis.md, 030-Companies/036-MWG/Thesis.md, 030-Companies/037-FPT/Thesis.md, 030-Companies/038-BID/Thesis.md, 030-Companies/039-VCB/Thesis.md, 030-Companies/040-PNJ/Thesis.md]
review_log:
  - 2026-07-04: Thêm VCB — BCTC kiểm toán EY 2025 + Q1/2026. Integrity Gate 9.5/11. Chất lượng TS số 1. P/E 16.1x, P/B 2.3x. Chờ entry 55-58k.
  - 2026-07-04: Thêm BID — TCBS initiation + full BCTC audit. Integrity Gate 10/11. P/B 1.6x đáy 5 năm. Chờ catalyst tăng vốn + BCTC Q2.
  - 2026-05-24: Khởi tạo watchlist với GAS
  - 2026-06-02: Thêm NLG
  - 2026-06-08: Thêm PVD
  - 2026-06-20: Thêm HPG — chờ integrity gate + composite
  - 2026-06-22: Thêm MWG — DMX IPO catalyst
  - 2026-06-23: Chuẩn hóa frontmatter + review_log + source_files. Sửa YAML pipe error. Thêm propagation rule vào stock-ingest skill
  - 2026-06-23: Ingest MWG Q1/2026 — EPS 1.849đ, LNST 2.758 tỷ (+78%), run-rate 11.030 tỷ
  - 2026-07-02: Thêm FPT — TCBS initiation + Integrity Gate 10/11, P/E forward 12x đáy 5 năm
  - 2026-07-05: Thêm PNJ — BCTC kiểm toán PwC 2022-2025 + Q1/2026. Integrity Gate 8/11. P/E 7.7x, EPS 7.652đ. Giá 58.700.
---

# Candidates Watchlist — Danh sách Theo dõi

Danh sách cổ phiếu VN tiềm năng rút gọn đang chờ vào lệnh. Nguồn: sàng lọc hàng tháng + định giá theo quý.

**Chú thích:**
- 🟢 XANH: Giá ≤ giá trị nội tại, sẵn sàng nghiên cứu entry
- 🟡 VÀNG: Định giá hợp lý, chờ pullback
- 🔴 ĐẮT: Giá cao hơn đáng kể so với nội tại, chờ điều chỉnh
- ⏳ CHỜ: Integrity gate chưa pass — cần BCTC hoặc catalyst xác nhận trước

| Mã | Ngành | Trạng thái | Định giá nội tại | Giá | Upside | Ngày thêm | Thesis | Ghi chú |
|---|---|---|---|---|---|---|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| BID | Ngân hàng | 🔴 ĐẮT | ~50.000-53.000 | 38.800 | +16-23% | 2026-07-04 | [[030-Companies/038-BID/Thesis]] | Integrity Gate 10/11. #1 TS, ROE 19.1%. P/B 1.6x đáy 5 năm. CAR 9.2% mỏng — đang giải quyết qua tăng vốn. Chờ catalyst BCTC Q2 + tăng vốn phase 2. |
| VCB | Ngân hàng | 🔴 ĐẮT | ~63.000-67.000 | 58.500 | +2-8% | 2026-07-04 | [[030-Companies/039-VCB/Thesis]] | Integrity Gate 9.5/11. Chất lượng TS số 1. NPL 0.97%. P/E 16.1x, P/B 2.3x. Premium định giá. Chờ pullback 55-58k. |
| FPT | CNTT | 🟡 VÀNG | ~90.000-95.000 | 67.000 | +18-25% | 2026-07-02 | [[030-Companies/037-FPT/Thesis]] | Integrity Gate 10/11, P/E forward 12x = đáy 5 năm. ROE 28%, net cash 19.000 tỷ. Stock-deploy: 95/100 🔫 BẮN. |
| NLG | BĐS | 🟡 VÀNG | ~23.100 | 24.900 | -11% | 2026-06-02 | [[Thesis/NLG]] | P/B 1,0x (book). Earnings comp cao hơn 16%. SOTP ~33k cần land bank dd |
|| GAS | NL (khí) | 🟡 VÀNG | ~70.000 | 75.300 | -13% | 2026-05-24 | [[Thesis/GAS]] | Moat độc quyền, tiền nhàn rỗi kéo định giá, theo dõi Q2 OCF |
|| PNJ | Bán lẻ (trang sức) | 🟡 VÀNG | ~65.000-76.500 | 58.700 | +11-30% | 2026-07-05 | [[030-Companies/040-PNJ/Thesis]] | Integrity Gate 8/11. #1 jewelry VN. EPS 7.652đ. P/E 7.7x. ⚠️ P-Lab scandal — chờ điều tra trước khi entry. IV giảm từ 85k xuống 76.5k (P/E 10x). |
| PVD | Dầu khí (khoan) | 🟡 VÀNG | ~31.000 | 19.600 | -1% | 2026-06-08 | [[Thesis/PVD]] | XANH (0/6). FCF âm. IV sát giá. Forward P/E 12,5x hấp dẫn. Chờ pullback <28k. |
| HPG | Thép | 🟡 VÀNG | ~31.500 | 21.900 | +34% | 2026-06-20 | [[030-Companies/035-HPG/Thesis]] | BCTC - Rolling đã cập nhật Q1/2026 gốc; entry trigger chờ integrity gate + composite xác nhận |
| MWG | Bán lẻ | 🟡 VÀNG | ~75-88k | 76.700 | 0% | 2026-06-22 | [[030-Companies/036-MWG/Thesis]] | DMX IPO T8/2026 + BHX hòa vốn. P/E fwd 12-14x, **trailing 16,3x** (EPS 4.774đ). **Q1/2026: EPS 1.849đ, LNST 2.758 tỷ (+78%). Run-rate 11.030 tỷ.** Biên gộp 20,9% (+100bps). Đã mua 816 tỷ CP quỹ. Chờ pullback. |

---

## Research Queue — Deep Dive cần làm trước khi quyết định entry

| Ticker  | Task                                                | Trạng thái | Ghi chú                                                                               |
| ------- | --------------------------------------------------- | ---------- | ------------------------------------------------------------------------------------- |
| VCB | Chờ BCTC Q2/2026 xác nhận NIM bền vững + CAR ổn định | ⏳ Chờ | Integrity Gate 9.5/11. Thesis tạo. P/E 16x — không rẻ. Cần entry 55-58k |
| BID | Chờ BCTC Q2/2026 xác nhận NIM đáy + CAR cải thiện | ⏳ Chờ | Integrity Gate 10/11. Thesis OK. Cần Q2 confirm trend |
| FPT | BCTC H1/2026 xác nhận EPS trajectory + FOX impact                   | ⏳ Chờ      | Chờ BCTC bán niên T8/2026. Cần LN cổ đông mẹ >5.000 tỷ H1 |
| NLG     | Land bank SOTP (Waterpoint, Akari, Cần Thơ, Mizuki) | ⬜ Chưa làm | Cần xác nhận intrinsic từ đất                                                         |
| PNJ | BCTC PwC 2022-2025 + Q1/2026 ingest | ✅ Xong     | Integrity Gate 8/11. EPS 7.652. P/E 7.7x. Rủi ro OCF + margin. Chờ BCTC Q2. |
| GAS     | OCF phục hồi sau Q1, kiểm tra bền vững biên LNG     | ⬜ Chưa làm | Q2 OCF là key metric                                                                  |
| PVD     | BCTC Deloitte 2025 verify + ingest                  | ✅ Xong     | EPS=1.541, FCF=-1.617, BCTC - Rolling.md tạo                                          |
| PVD     | Q1/2026 ingest + backlog confirm                    | ✅ Xong     | DT 3.401 tỷ +126% YoY, backlog Q2 chưa có                                             |
| HPG     | Integrity gate + composite score                    | ⏳ Chờ      | Chờ BCTC hoặc thêm catalyst                                                           |
| MWG     | DMX IPO timeline + ERA expansion confirm            | ⬜ Chưa làm | Catalyst đã track, cần update khi có tin mới                                          |
| MWG     | BCTC audited 2025 ingest                            | ✅ Xong     | EPS 4.774đ, OCF 6.096 tỷ, biên gộp 19,9% (23/06/2026)                                 |
| **MWG** | **BCTC Q1/2026 ingest**                             | **✅ Xong** | **EPS 1.849đ, LNST 2.758 tỷ (+78%), run-rate 11.030 tỷ. Biên gộp 20,9% (23/06/2026)** |

---

## Thesis Templates

Mỗi candidate thêm vào watchlist cần tạo thesis file tại `Thesis/{TICKER}.md` theo cấu trúc của GAS.md (bull case, bear case, BCTC summary, 5 phương pháp định giá, entry trigger).

---

*Theo dõi chủ động. Next action: NLG SOTP → GAS OCF → MWG catalyst theo dõi.*
