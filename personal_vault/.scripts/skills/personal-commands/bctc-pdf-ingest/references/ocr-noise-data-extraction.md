# OCR-Noise Data Extraction — Vietnamese BCTC

## Vấn đề
Liteparse OCR trên BCTC tiếng Việt bị méo dấu, sai khoảng cách, và lẫn ký tự. `Lợi nhuận sau thuế` có thể thành `Loi nhuan sau thue`. Không thể dùng exact string matching.

## Giải pháp: Số liệu là chân lý

### Nguyên tắc
- **Số liệu luôn chính xác trong OCR** — dấu chấm phân cách hàng nghìn, số nhiều chữ số luôn đúng
- **Tiếng Việt bị méo** — không dùng exact match, dùng fuzzy hoặc anchor bằng số

### Pattern 1: Anchor bằng số biết trước
Khi đã biết một con số từ broker report (vd TCBS: LNST 11.232 tỷ):
```
Search raw OCR cho: 11.232
→ Tìm được dòng chứa: ... 11.232.339.450.734
→ Trích xuất số đầy đủ
```

### Pattern 2: Search bằng từ khóa lõi
```python
# Thay vì:
if "Lợi nhuận sau thuế" in line:
# Dùng:
if "sau thue" in line.lower() or "loi nhuan" in line.lower():
```

### Pattern 3: Extract bằng regex số tiền
```python
import re
# Bắt số dạng: 13.043.632.833.797
nums = re.findall(r'\d{1,3}(?:\.\d{3})+(?:\.\d{3})?', line)
```

### Pattern 4: Batch multi-file — dùng file gần nhất làm reference
File BCTC mới nhất có 2 cột số (current year + prior year). Đây là nguồn tin cậy nhất để verify cross-year data.

**Kỹ thuật "one-file verification" (FPT session 2026-07-02):** Không cần extract full text từ 5+ file. Chỉ cần:
1. Lấy multi-year data từ broker report (TCBS/SSI — đã có 3-5 năm history)
2. Extract **file BCTC mới nhất** (có 2 cột: 2025 + 2024)
3. Verify số 2024 từ BCTC với số 2024 từ TCBS → nếu khớp, cả dãy TCBS đáng tin
4. Chỉ extract thêm file cũ khi có mismatch >5%
→ Tiết kiệm 80% thời gian parse. Đã test thành công với FPT (6 files → chỉ cần 2025 file).

**Pattern 5: Integrity Gate data extraction từ OCR**
Khi chạy Integrity Gate 11 checks, các chỉ tiêu cần extract từ BCTC:
| Check | Tìm gì trong OCR | Pattern |
|-------|------------------|---------|
| OCF | "Luu chuyen" + "thuan" + "hoat dong kinh doanh" | Regex số cuối dòng `20` trong CF |
| Receivables | "Phai thu" + "ngan han" | Số dòng 130 trong Balance Sheet |
| Goodwill | "Loi the thuong mai" | Số dòng 269 |
| D/E | "Vay va no" + "ngan han" + "dai han" vs "Von chu so huu" | Dòng 320+338 vs 410+440 |
| Interest | "Chi phi lai vay" | Tìm trong P&L hoặc CF note

### Luồng xử lý khuyến nghị
1. Liteparse batch → 6 files ~2 phút
2. Đọc OCR file mới nhất → extract số bằng regex
3. Map số tìm được vào chỉ tiêu bằng heuristic (dòng gần section header nào)
4. Cross-check với broker report data — nếu match → [HIGH]
5. Nếu lệch >5% → dùng audited BCTC làm chân lý cuối

### Ví dụ FPT session (2026-07-02)
- 6 liteparse files: 2021-2025 + Q1/2026
- OCR output: 2.354-3.657 lines/file, số đúng nhưng text méo
- Cross-check với TCBS report: **tất cả số liệu khớp**
- Không cần extract exact text — chỉ cần số từ OCR + tên chỉ tiêu từ TCBS

### Integrity Gate extraction hack (FPT case study — industrial co.)

Các chỉ tiêu Integrity Gate nằm ở những section cố định trong BCTC hợp nhất **của công ty sản xuất/phi tài chính**:

| Check | Section | Dòng đánh dấu | Số cần lấy |
|-------|---------|---------------|-----------|
| OCF | Cash Flow (cuối file) | `Luu chuyen tien thuan tir hoat dong kinh doanh` | Dòng cuối OCF section |
| NI | P&L | `Loi nhuan sau thue` | Dòng 60 |
| LN cổ đông mẹ | P&L | `Co dong cong ty me` | Dòng 61 |
| Tổng TS | Balance Sheet | `TONG TAI SAN` | Dòng 270 |
| VCSH | Balance Sheet | `VON CHU SO HU'U` | Dòng 400 |
| Vay ngắn hạn | Balance Sheet | `Vay va no thue tai chinh ngan han` | Dòng 320 |
| Phải thu | Balance Sheet | `Cac khoan phai thu ngan han` | Dòng 130 |
| Goodwill | Balance Sheet | `Loi the thuong mai` | Dòng 269 |

**Mẹo:** Đọc từ cuối file lên. Cash flow section ở cuối Balance Sheet. Dùng `read_file offset=<total-200>` để bắt đầu từ CF section.

### Integrity Gate extraction hack (BID case study — bank)

**Cấu trúc BCTC bank khác biệt so với công ty sản xuất.** Các chỉ tiêu nằm ở vị trí khác. Tham khảo BID BCTC 2025 (138 trang, 8025 lines OCR):

| Check | Search pattern | Line range (BID) | Note |
|-------|---------------|-------------------|------|
| OCF (subtotal) | `"Luu chuyen tien thuan tir hoat dong kinh doanh"` (first match) | ~642 | Trước thay đổi vốn LĐ |
| OCF (total) | `"Luu chuyen tien thuan tir hoat dong kinh doanh"` (second match) | ~666 | Sau thay đổi vốn LĐ |
| NI | `"Loinhuan sau thue"` | ~591 | |
| TOI | `"Tong thu nhap hoat dong"` | ~579 | Tổng thu nhập hoạt động |
| PPOP | `"Loi nhuan thuan tir hoat dong kinh doanh"` + context | ~584 | LN trước dự phòng |
| Provision | `"Chi phi du phong rui ro tin dung"` | ~586 | |
| Total assets | `"TONG TAI SAN"` | ~421 | |
| Equity | `"TONG VON CHU SO"` | ~469 | |
| Accounts receivable | `"Tai san Co phai thu"` | ~413 | Khác với "phải thu ngắn hạn" của industrial |
| Interest/fees receivable | `"lai, phi phai thu"` | ~415 | Theo dõi riêng |
| NPL Group 3 | `"Sub-standard"` (English) | ~6262 | English section dễ đọc hơn |
| NPL Group 4 | `"Doubtful"` | ~6263 | |
| NPL Group 5 | `"Loss"` | ~6264 | |
| RPT | `"BEN LIEN QUAN"` hoặc `"Related parties"` | ~3520 (VN) | Note số khác nhau mỗi bank |

**Lưu ý:** Các line number mang tính tham khảo (thay đổi theo bank). Luôn search pattern thay vì hardcode line number.

**English section dễ OCR hơn.** Khi BCTC >5000 lines, grep bằng English pattern (Sub-standard, Doubtful, Loss, Related parties) cho kết quả chính xác hơn Vietnamese bị méo dấu.

## Khi nào dùng fallback
- OCR không ra số cho 1 chỉ tiêu → lấy từ broker report [MOD] thay vì bỏ trống
- Luôn ưu tiên audited BCTC [HIGH] khi verify được