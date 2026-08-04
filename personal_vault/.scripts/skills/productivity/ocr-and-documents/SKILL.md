---
name: ocr-and-documents
description: "Extract text from PDFs/scans — priority: liteparse (OCR sẵn) → pymupdf → marker-pdf."
version: 2.5.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [PDF, Documents, Research, Arxiv, Text-Extraction, OCR, Vision-Fallback, liteparse]
    related_skills: [powerpoint]
---

# PDF & Document Extraction

For DOCX: use `python-docx` (parses actual document structure, far better than OCR).
For PPTX: see the `powerpoint` skill (uses `python-pptx` with full slide/notes support).
This skill covers **PDFs and scanned documents**.

## Step 1: Remote URL Available?

If the document has a URL, **always try `web_extract` first**:

```
web_extract(urls=["https://arxiv.org/pdf/2402.03300"])
web_extract(urls=["https://example.com/report.pdf"])
```

This handles PDF-to-markdown conversion via Firecrawl with no local dependencies.
Only use local extraction when: the file is local, web_extract fails, or you need batch processing.

## Step 2: PDF Parsing Priority (STRICT ORDER)

**CRITICAL RULE — do NOT skip to marker-pdf without checking liteparse first.**

| Priority | Tool | Scanned PDF? | OCR? | Install size | Speed |
|----------|------|-------------|------|-------------|-------|
| 🥇 1st | **liteparse** | ✅ Yes | ✅ Built-in OCR | ~50MB (Node.js) | ~1-2s/page (51s cho 43 trang) |
| 🥈 2nd | **pymupdf** | ❌ No (text only) | ❌ | ~25MB | Instant |
| 🥉 3rd | **marker-pdf** | ✅ Yes | ✅ Surya OCR | ~3-5GB (PyTorch + 1.35GB model) | ~1-14s/page + model download |

**Rule:** Try liteparse FIRST for ALL PDFs. Only fall back to marker-pdf if:
1. liteparse is not installed (`which liteparse` fails)
2. liteparse errors on the file
3. Warren explicitly says to use marker-pdf

---

## liteparse (FASTEST — priority #1)

**Check availability:**
```bash
liteparse --version    # Must be 2.1.2+
```

**Usage:**
```bash
liteparse parse input.pdf -o output.lit.txt
```

**OCR is enabled by default** — even scanned/image-based PDFs work:
- 43-page scanned PDF: **51 seconds total** (extract + OCR render + OCR text)
- No model download needed, no PyTorch, no HuggingFace cache
- Output: plain text `.lit.txt` next to source file

**Canonical install path (Windows):**
- `/c/Users/khoans/AppData/Roaming/npm/liteparse` (npm global install)
- `/c/Users/khoans/AppData/Local/Programs/Python/Python312/Scripts/liteparse` (pip install — legacy)

**Gate check:** If output file is missing or empty → stop and report blocker. Do not silently fall back.

---

## pymupdf (lightweight — text-only PDFs)

```bash
pip install pymupdf pymupdf4llm
```

**Via helper script:**
```bash
python scripts/extract_pymupdf.py document.pdf              # Plain text
python scripts/extract_pymupdf.py document.pdf --markdown    # Markdown
python scripts/extract_pymupdf.py document.pdf --tables      # Tables
python scripts/extract_pymupdf.py document.pdf --images out/ # Extract images
python scripts/extract_pymupdf.py document.pdf --metadata    # Title, author, pages
python scripts/extract_pymupdf.py document.pdf --pages 0-4   # Specific pages
```

**Inline:**
```bash
python3 -c "
import pymupdf
doc = pymupdf.open('document.pdf')
for page in doc:
    print(page.get_text())
"
```

---

## marker-pdf (last resort — heavy OCR)

Only use when liteparse is unavailable or fails. First run downloads ~1.35GB surya OCR model.

```bash
# Check disk space first
python scripts/extract_marker.py --check

pip install marker-pdf
```

**Via helper script:**
```bash
python scripts/extract_marker.py document.pdf                # Markdown
python scripts/extract_marker.py document.pdf --json         # JSON with metadata
python scripts/extract_marker.py document.pdf --output_dir out/  # Save images
python scripts/extract_marker.py scanned.pdf                 # Scanned PDF (OCR)
python scripts/extract_marker.py document.pdf --use_llm      # LLM-boosted accuracy
```

**CLI:**
```bash
marker_single document.pdf --output_dir ./output
marker /path/to/folder --workers 4
```

### Scanned PDF First-Run Pitfalls

**⏱ First run = model download + OCR, expect 10-20 minutes:**
- marker-pdf downloads surya OCR model ~1.35GB + layout model ~200MB on first use
- Download speed: typically 2-4 MB/s on Vietnamese internet → **10-15 minutes just for download**
- After download, OCR processes ~1-14 seconds/page on CPU
- **ALWAYS warn the user upfront:** "This is a scanned PDF. First run requires downloading a 1.35GB OCR model (~10-15 mins). I'll run it in the background."
- The model is cached after first download — subsequent runs process instantly

**🔧 Use background mode to avoid timeout:**
```python
terminal("marker_single scanned.pdf --output_dir ./out", background=True, notify_on_complete=True, timeout=1800)
```
- Default terminal timeout (180s) will kill model downloads — set timeout ≥1800s or use background=True
- Poll progress with `process(action="poll", session_id="...")`

**📁 CLI path on Windows:**
- marker_single installs to `Python312/Scripts/`, may NOT be in PATH
- Full path: `/c/Users/khoans/AppData/Local/Programs/Python/Python312/Scripts/marker_single`
- Verify: `which marker_single` or `pip show marker-pdf | grep Location`

**🖼 Vision Fallback (while marker downloads):**
When marker-pdf is still downloading models (10-15 min), extract key pages as images and use vision_analyze:

```python
import fitz
doc = fitz.open("scanned.pdf")
for i in [0, 3, 4]:  # Cover, balance sheet, P&L
    page = doc[i]
    pix = page.get_pixmap(dpi=200)
    pix.save(f"page_{i+1}.png")
    # If vision errors (413), reduce to dpi=100 ~600KB
```

Then: `vision_analyze(image_url="page_3.png", question="Read balance sheet numbers...")`

---

## Vision Fallback (universal — works without any local tool)

When no local PDF parser is available, or the PDF is problematic:

1. Export pages as PNG images using PyMuPDF (fitz)
2. Start at 200 DPI; if 413 error, reduce to 100 DPI
3. Use `vision_analyze` to read the data
4. Cross-verify with any other available source (broker reports, TCBS data, etc.)

**Best for:** Balance sheets, income statements, key data tables
**Limits:** Images >800KB may be rejected; some models don't support vision

---

## Arxiv Papers

```
# Abstract only (fast)
web_extract(urls=["https://arxiv.org/abs/2402.03300"])

# Full paper
web_extract(urls=["https://arxiv.org/pdf/2402.03300"])

# Search
web_search(query="arxiv GRPO reinforcement learning 2026")
```

## Split, Merge & Search

pymupdf handles these natively — use `execute_code` or inline Python:

```python
# Split: extract pages 1-5 to a new PDF
import pymupdf
doc = pymupdf.open("report.pdf")
new = pymupdf.open()
for i in range(5):
    new.insert_pdf(doc, from_page=i, to_page=i)
new.save("pages_1-5.pdf")
```

```python
# Merge multiple PDFs
import pymupdf
result = pymupdf.open()
for path in ["a.pdf", "b.pdf", "c.pdf"]:
    result.insert_pdf(pymupdf.open(path))
result.save("merged.pdf")
```

```python
# Search for text across all pages
import pymupdf
doc = pymupdf.open("report.pdf")
for i, page in enumerate(doc):
    results = page.search_for("revenue")
    if results:
        print(f"Page {i+1}: {len(results)} match(es)")
        print(page.get_text("text"))
```

No extra dependencies needed — pymupdf covers split, merge, search, and text extraction in one package.

---

## Pitfalls (collected 2026-06-23)

- **Do NOT skip liteparse.** It has built-in OCR (43 scanned pages in 51s). Installing marker-pdf just because pymupdf returns empty text is wrong — liteparse comes first.
- **Duplicated sections:** The old version of this skill had the "Scanned PDF First-Run Pitfalls" section twice. Clean version now has one copy.
- **Vision API limits:** Images >800KB get 413 error. Export at dpi=100 for ~600KB. Some models (404 error) don't support vision — check model capability first.

## Notes

- `web_extract` is always first choice for URLs
- pymupdf is the safe default for text-based PDFs
- **liteparse is the #1 choice for ALL local PDFs** — text or scanned
- marker-pdf is for OCR, scanned docs, equations, complex layouts — last resort
- Both helper scripts accept `--help` for full usage
- marker-pdf downloads ~2.5GB of models to `~/.cache/huggingface/` on first use
- For Word docs: `pip install python-docx` (better than OCR — parses actual structure)
- For PowerPoint: see the `powerpoint` skill (uses python-pptx)