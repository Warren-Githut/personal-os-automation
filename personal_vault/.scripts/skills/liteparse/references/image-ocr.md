# Image OCR via liteparse

> Added 2026-06-26 — Warren hỏi "sao k dùng liteparse" khi Hermes mất công OCR thủ công.

## Use case

liteparse handles **images** (PNG, JPG) via built-in OCR, not just PDFs. When user gửi screenshot chứa error message, terminal output, chat log → dùng liteparse thay vì:

- ❌ `vision_analyze()` — cần vision-capable model. **Tất cả model DeepSeek (Flash, V4 Pro, etc.) đều KHÔNG support `image_url`** → sẽ fail với lỗi: `unknown variant 'image_url', expected 'text'`. Đừng thử fallback — dùng liteparse preprocessing thay vì vision_analyze.
- ❌ `pytesseract` — cần Tesseract engine (chưa install trên máy này)
- ❌ PIL ASCII conversion — không reliable

## Nguyên tắc FIRST PASS

> Warren rule (2026-06-26): "khi đọc png, jpeg, pdf thì phải dùng tool liteparse để đọc OCR và extract text trước nhé, rồi mới fall back về những cái khác. nhớ đó."

**liteparse luôn là first pass.** Nếu output trắng hoặc quá ít → preprocessing (xem pipeline bên dưới) → liteparse lại. Chỉ khi liteparse thất bại hoàn toàn sau preprocessing mới báo lỗi cho user. Không tự ý chuyển sang tool khác.

## Workflow

```bash
liteparse parse "<source_image.png>" -o "<output>.txt"
```

- Output: file `.txt` chứa OCR-extracted text
- liteparse version: `2.1.2` (`liteparse --version`)
- Supports: PNG, JPG, JPEG, BMP, TIFF

## Example (this session, 2026-06-26)

```bash
liteparse parse "C:\Users\khoans\AppData\Roaming\Hermes\composer-images\composer_2026-06-26_02-53-56-383_06ab5a.png" -o "C:\Users\khoans\AppData\Roaming\Hermes\composer-images\composer_ocr_output.txt"
```

Result: `"Không hiểu cú pháp. Gõ /help để xem hướng dẫn."`

## Caveats

- Vietnamese diacritics đôi khi bị lỗi nhẹ (VD: `á` → OCR ra `a'`). Vẫn đọc được.
- PNG alpha channel (RGBA) vẫn xử lý được.

## Pitfalls & Gotchas (real-world, 2026-07-09)

### Gotcha 1 — Dùng `python` chứ KHÔNG `python3` cho PIL trên Windows host này
- Pipeline tiền xử lý bên dưới gốc dùng `python3 -c "..."`. Trên máy Warren (Windows/git-bash), `python3` resolve về interpreter có PIL **ABI-incompatible** → lỗi `cannot import name '_imaging' from 'PIL'`.
- **FIX:** Dùng `python` (Hermes venv 3.11.15, PIL 12.2.0 OK) cho mọi one-liner PIL tiền xử lý. `which python` → `…/hermes-agent/venv/Scripts/python`.
- Symptom nhanh: gặp `_imaging` ImportError → đổi `python3` thành `python` là xong.

### Gotcha 2 — Bảng số nhiều cột ngang (manpower / staffing grid) → liteparse bở hơi
- Ảnh dải ngang (vd 1258×286, 3 cột store × 4 role) chứa toàn số: liteparse thô chỉ bắt được tên role, **rụng sạch số và 2/3 cột**.
- Đã thử: grayscale+contrast+sharpen+3x, binary threshold, desaturate, crop 3 cột rồi OCR riêng → vẫn rác (số mâu thuẫn giữa các bản, ví dụ SA 5 vs 7).
- **Không lãng phí thêm lượt.** Fallback chuẩn khi gặp bảng số nhiều cột:
  1. Hỏi user **paste text bảng** thẳng vào chat (nhanh nhất, chính xác 100%), HOẶC
  2. Yêu cầu file gốc **Excel/CSV** thay vì screenshot → parse bằng markitdown / script.
- Chỉ ép OCR khi ảnh là text thuần (chat log, terminal, error) — trường hợp đó liteparse thô ~95% ổn.

## Preprocessing cho ảnh khó (heatmap, bảng màu, chữ nhỏ)

> Added 2026-06-26 — heatmap "Month-on-month growth %" từ email CFO: OCR thô bắt được ~30% dữ liệu. Sau 5 lần preprocessing khác nhau → bắt được ~80%.

Khi liteparse trả về output quá ít hoặc noise (VD: bảng heatmap có nền màu, chữ số nhỏ trong ô), đừng chấp nhận kết quả đầu tiên. Thử tuần tự các bước preprocessing bên dưới — mỗi bước tạo một file riêng, chạy liteparse, so sánh output.

### Pipeline chuẩn (thử theo thứ tự)

```bash
python -c "
from PIL import Image, ImageEnhance, ImageFilter, ImageOps
img = Image.open(r'<source>.png')
# Step 1: Grayscale + contrast boost + sharpen + scale 3x
gray = img.convert('L')
enhanced = ImageEnhance.Contrast(gray).enhance(3.0)
sharp = enhanced.filter(ImageFilter.SHARPEN)
w, h = sharp.size
scaled = sharp.resize((w*3, h*3), Image.LANCZOS)
scaled.save(r'<out>_processed.png')
# Step 2: Binary threshold (nếu nền sáng, chữ tối)
bw = gray.point(lambda x: 0 if x < 140 else 255, '1')
bw_scaled = bw.resize((w*3, h*3), Image.NEAREST)
bw_scaled.save(r'<out>_bw.png')
# Step 3: Desaturate + sharpen + contrast + scale 3x (giữ màu gốc)
desat = img.copy()
for enc in [ImageEnhance.Sharpness, ImageEnhance.Contrast, ImageEnhance.Color]:
    desat = enc(desat).enhance(2.0 if enc != ImageEnhance.Color else 0.0)
desat = desat.resize((w*3, h*3), Image.LANCZOS)
desat.save(r'<out>_sharp.png')
# Step 4: Red channel isolate + invert + scale 3x (heatmap có nền màu)
r, g, b, a = img.split()
r_inv = ImageOps.invert(r)
r_inv = r_inv.resize((w*3, h*3), Image.LANCZOS)
r_inv.save(r'<out>_red.png')
"
```

Sau mỗi bước, chạy:
```bash
liteparse parse "<processed>.png" -o "<processed>.lit.txt" --preserve-small-text --format markdown
```

### So sánh & chọn output tốt nhất

- Đọc từng file `.lit.txt` bằng `read_file`
- Output nào có nhiều số nhất, ít noise nhất → dùng để tổng hợp
- Với bảng dữ liệu, cross-reference các output để fill gap — mỗi lần OCR có thể bắt được các ô khác nhau
- Luôn đánh dấu `[LOW]` cho số từ OCR noise, `[HIGH]` cho số xuất hiện nhất quán qua nhiều lần parse

### Khi nào preprocessing không cần thiết

- Screenshot text thuần (chat log, terminal, error message) → liteparse thô đã đủ (~95% accuracy)
- PDF tài liệu text → liteparse parse thẳng, không cần ảnh hóa

### Gotcha 3 — Ảnh promo/marketing (chữ stylized, nền nhiều hình) OCR gần trắng
- Ảnh post promo (vd "Sunset Happy Hour", "Morning Kickstart") thường có ÍT text, chữ to/stylized, nền decorative → liteparse thô trả về rỗng hoặc 1-2 từ.
- **FIX đã verify 2026-07-12:** grayscale + contrast 2.8× + upscale 3× rồi liteparse → bắt được keyword ("Sunset happy hours", "From 10:00 AM to 11:30 AM at L'Usine Saigon Centre for all drinks & dessert").
- Dùng `python` (không `python3`) cho PIL one-liner (xem Gotcha 1).
- Nếu vẫn rỗng → báo user ảnh trắng / nhờ paste text, đừng loop vision (model này không có vision).

## Quick workflow

Khi cần OCR ảnh:
1. `liteparse parse "<image>" -o "<image>.lit.txt"`
2. `read_file("<image>.lit.txt")` → lấy text
3. Action dựa trên text
4. Cleanup temp `.lit.txt` nếu muốn
