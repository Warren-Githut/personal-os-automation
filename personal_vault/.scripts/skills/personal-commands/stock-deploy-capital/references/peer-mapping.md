---
name: Peer Mapping (VN + SEA)
type: reference
status: active
version: 1.0
last_updated: 2026-07-19
tags: [peer, valuation, benchmarking, SEA]
domain: stock
---

# Peer Mapping — Benchmark Định Giá 3 Nhà Đầu Tư

> Dùng trong `stock-deploy-capital` (full + `--light`) để so sánh ticker mục tiêu với **2 peer Việt Nam + 2 peer Đông Nam Á** cùng ngành.
> Mục đích: Lynch PEG/PEGY và Damodaran SOTP cần context ngành — giá trị không nằm trong chân không, mà nằm trong tương quan với đối thủ cùng ngành trong khu vực.
>
> ⚠️ **Tag [MOD]:** Ticker SEA là con chọn theo knowledge, CHƯA web-verify. Khi chạy `--light`, Hermes phải `web_search` confirm giá/tỷ lệ mới nhất rồi mới tính. Bố có thể sửa tên peer ở file này bất cứ lúc nào.

## Cấu trúc so sánh

Với mỗi ticker mục tiêu, Hermes:
1. Xác định ngành (từ `Thesis.md` hoặc `Candidates_Watchlist.md`)
2. Lấy 2 VN peer + 2 SEA peer từ bảng dưới
3. Tính các ratios so sánh: P/E, P/B, ROE, EPS growth (3-5 năm), PEG
4. Đánh giá: target đang RẺ / NGANG / ĐẮT vs peer cùng tốc độ tăng trưởng
5. Ghi vào section 5D (Peer Comp) của output

## Bảng Peer theo ngành

### 1. Đầu khí (Oil & Gas)
| Loại | Mã | Tên | Sàn | Ghi chú |
|------|-----|-----|-----|---------|
| VN | GAS | PV GAS | HOSE | Độc quyền hạ tầng khí |
| VN | PVS | PTSC | HOSE | Dịch vụ khoan/giàn |
| SEA | PTTEP | PT Marcou Energy | SET (Thái) | SOE Thái, lớn nhất khu vực |
| SEA | MEDC | Medco Energi | IDX (Indo) | Private, đa dạng hóa |

### 2. Ngân hàng (Banking)
| Loại | Mã | Tên | Sàn | Ghi chú |
|------|-----|-----|-----|---------|
| VN | BID | BIDV | HOSE | Big 4, SOE |
| VN | VCB | Vietcombank | HOSE | Chất lượng tài sản số 1 |
| SEA | BCA | Bank Central Asia | IDX (Indo) | ROE cao, quản trị tốt |
| SEA | SCB | Siam Commercial Bank | SET (Thái) | Private lớn nhất Thái |

### 3. Bán lẻ / Trang sức (Retail)
| Loại | Mã | Tên | Sàn | Ghi chú |
|------|-----|-----|---------|
| VN | PNJ | Phú Nhuận Jewelry | HOSE | #1 trang sức VN |
| VN | MWG | Thế Giới Di Động | HOSE | Điện máy + Bách Hóa Xanh |
| SEA | CRC | Central Retail | SET (Thái) | TTTM + food retail |
| SEA | MAPI | Mitra Adiperkasa | IDX (Indo) | Bán lẻ đa ngành (Starbucks Indo,etc) |

### 4. Bất động sản (Real Estate)
| Loại | Mã | Tên | Sàn | Ghi chú |
|------|-----|-----|---------|
| VN | NLG | Nam Long | HOSE | Nhà ở vừa túi tiền |
| VN | NVL | Novaland | HOSE | BĐS cao cấp (rủi ro cao) |
| SEA | SIRI | Sansiri | SET (Thái) | Dev nhà ở Thái |
| SEA | BSDE | Bumi Serpong Damai | IDX (Indo) | KCN + nhà ở |

### 5. Công nghệ / IT (Technology)
| Loại | Mã | Tên | Sàn | Ghi chú |
|------|-----|-----|---------|
| VN | FPT | FPT Corp | HOSE | DX + outsourcing |
| VN | CMG | CMC Corp | HOSE | Hạ tầng IT |
| SEA | SE | Sea Limited | NYSE (Singapore) | Mã hóa NGC, thương mại, fintech |
| SEA | GOTO | GoTo Gojek Tokopedia | IDX (Indo) | Super-app |

## Quy tắc so sánh (linh hoạt theo ngành — Bố chọn C)

- **Đầu khí / Ngân hàng:** So P/B vs ROE là trọng tâm (tài sản nặng). PEG ít ý nghĩa hơn (chu kỳ).
- **Bán lẻ:** PEGY là trọng tâm (tăng trưởng + cổ tức). Peer SEA giúp thấy chu kỳ vàng.
- **BĐS:** P/B vs book value, so NAV/SOTP. Peer SEA giúp benchmark thanh khoản.
- **Công nghệ:** P/E cao tự nhiên (asset-light) → so P/E growth-adjusted vs SEA (SE, GOTO thường lỗ → dùng P/S hoặc EV/Sales).

## Khi thiếu peer (fallback)
- Nếu ngành chưa có trong bảng → Hermes `web_search "<ngành> top players Vietnam Thailand Indonesia"` → đề xuất 2+2, tag [MOD], ghi vào review_log của output.
- Nếu SEA peer không có BCTC public → ghi "N/A", chỉ so 2 VN peer.

## Nguồn
- [MOD] Con chọn từ knowledge vùng Đông Nam Á. CHƯA web-verify ticker/price.
- Khi chạy thực tế: `web_search` hoặc `web_extract` để lấy P/E, P/B, ROE, growth mới nhất của 4 peer trước khi tính PEG/SOFP.
