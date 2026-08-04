# markitdown — Microsoft File-to-Markdown Converter

> Added 2026-06-30 — Warren yêu cầu cài để xử lý file Office/PDF/HTML.
> `github.com/microsoft/markitdown` (162k ⭐)

## What it does
Converts any file → clean markdown. Supports:
- **Office**: DOCX, XLSX, PPTX
- **Web**: HTML, HTM
- **Documents**: PDF (text-based), EPUB, XML
- **Images**: JPEG, PNG, GIF, WebP, TIFF, BMP (via embedded OCR)
- **Other**: CSV, JSON, XML, ZIP archives (extracts + converts contents)

## Installation
```bash
pip install markitdown
# Version installed: 0.1.6 (latest as of 2026-06-30)
```

## Usage
```bash
# Basic: convert file to stdout
python -m markitdown "path/to/file.docx"

# Output to file
python -m markitdown "path/to/file.xlsx" --output "output.md"
```

## Integration with liteparse

| Scenario | Tool | Why |
|----------|------|-----|
| Screenshot PNG | liteparse | Better OCR for graphical content |
| Excel report .xlsx | markitdown | Native XLSX parser, extracts tables properly |
| Scanned PDF (image-based) | liteparse | OCR engine handles scanned docs |
| Text PDF | markitdown | Faster, no OCR overhead |
| Word doc .docx | markitdown | Only tool that handles .docx |
| Mixed email attachments | liteparse for images, markitdown for Office | Use each tool for its strength |

## Warren's context
- Accounting gửi Excel files → markitdown convert → Hermes phân tích số
- Supplier gửi Word/PDF quotes → markitdown extract → Hermes so sánh
- Internal reports (.pptx) → markitdown → Hermes tóm tắt nội dung

## Caveats
- XLSX: tables extract well but merged cells may lose structure
- PPTX: extracts text per-slide, loses slide layout/positioning
- PDF: only text-based PDFs (not scanned). For scanned → use liteparse first, fallback markitdown if clean text needed
- Large files (>50 pages): truncation may occur; chunk if needed
