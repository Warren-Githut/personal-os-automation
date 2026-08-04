---
name: liteparse
description: 'File-to-text conversion: liteparse (OCR/images/PDFs) + markitdown (Office/HTML/PDF). Hard gate: liteparse FIRST, vision_analyze fallback ONLY after liteparse fails. Added 2026-07-04: section ref SOUL.md §3.1 (moved from §5).'
version: 0.5.1
tags: [pdf, ocr, liteparse, markitdown, file-to-text, parse]
---

# liteparse — File-to-Text Conversion (HARD GATE 🚨)

> **Enforced by SOUL.md §3.1 (Liteparse gate 🚨):** Khi Warren gửi ảnh / PDF / screenshot → Hermes phải chạy `liteparse parse` trước. CHỈ dùng `vision_analyze` khi liteparse output rỗng hoặc ko đọc được. Vi phạm = bug.
>
> **Cập nhật 2026-07-04:** Section ref §3.1 (moved from §5).
> **Cập nhật 2026-06-30:** HARD GATE + markitdown integration.
> **Cập nhật 2026-06-28:** Liteparse primary + vision fallback, cross-profile.

## Purpose

Single deterministic path for converting any file type to clean markdown text:

| Input type | Primary tool | Fallback |
|------------|-------------|----------|
| Images (PNG/JPG/JPEG/WebP/screenshots) | **liteparse** OCR | `vision_analyze` only if liteparse output empty |
| PDF documents | **liteparse** parse | `markitdown` for text-based PDFs |
| Office docs (DOCX/XLSX/PPTX) | **markitdown** | — |
| HTML | **markitdown** | — |
| Mixed (email attachments, reports) | liteparse for images/PDFs, markitdown for Office | — |

## Tools

### liteparse — OCR + PDF parsing
- Binary: `liteparse` (version pin: `2.10.1` — updated 2026-08-02 from 2.1.2; npm global, shared across ALL Hermes profiles)
- Installed: npm global (`/c/Users/khoans/AppData/Roaming/npm/liteparse`)
- Output: `<basename>.lit.txt` beside source
- OCR: enabled by default
- Workflow: `liteparse parse "<source>" -o "<source>.lit.txt"`

### markitdown — Office/HTML/PDF conversion
- Installed: `pip install markitdown` (v0.1.6+)
- Microsoft open-source tool: `github.com/microsoft/markitdown`
- Converts: DOCX, XLSX, PPTX, HTML, PDF, images → markdown
- Usage: `python -m markitdown "<path-to-file>" --output "<output-path>"`
- See `references/markitdown.md` for details

## HARD GATE Workflow

> **🚨 Đây là HARD RULE, ko phải recommendation. Vi phạm = bug (SOUL.md §3.1).**

1. **Receive file** — Warren sends image / screenshot / PDF / Office doc in chat
2. **Identify type**:
   - Image/PDF → liteparse FIRST
   - Office doc → markitdown FIRST
3. **Run primary tool** via terminal
4. **Gate check:**
   - If output exists + non-empty → proceed with `.lit.txt` content
   - If output empty or clearly unusable → try **fallback** (vision_analyze for images, the other tool for files)
   - If both fail → report blocker to Warren
5. **Do NOT** skip straight to vision_analyze without trying liteparse first

## Image OCR Preprocessing

For difficult images (heatmaps, colored tables, small text), see `references/image-ocr.md` for the 4-step PIL preprocessing pipeline before re-running liteparse.

### Pitfall: liteparse fails on MSYS `/c/...` path under git-bash (Windows)
**Symptom:** `liteparse parse "/c/Users/khoans/.../img.png" -o "..."` → `magick.exe: unable to open image '/c/Users/...' : No such file or directory`. The node binary does NOT translate MSYS-style `/c/` paths to Windows drives.
**Fix:** Pass the NATIVE Windows path: `C:/Users/khoans/.../img.png` (forward slashes OK) or `C:\Users\khoans\...`. Same for the `-o` output path.
**Verify:** if liteparse exits 0 but the `.lit.txt` output is empty, re-check the path was native, not MSYS.

### Pitfall: Python `liteparse` package API changed (v2.5.1)
**Symptom:** Code does `import liteparse; liteparse.parse(img)` → `AttributeError: module 'liteparse' has no attribute 'parse'`.
**Cause:** The pip-installable `liteparse` (PyO3 wrapper, v2.5.1) exposes the `LiteParse` **class**, not a module-level `parse()` function. The old `liteparse.parse()` form was removed.
**Fix (two working options):**
- **(a) npm CLI (canonical, matches HARD GATE):** `liteparse parse "<img>" -o "<out>.lit.txt"` via subprocess. Pass NATIVE Windows path (no MSYS `/c/`).
- **(b) Python `LiteParse` class (verified working 2026-07-13):**
  ```python
  import liteparse
  lp = liteparse.LiteParse(ocr_enabled=True)
  res = lp.parse(r"C:/path/to/img.png")          # accepts str | Path | bytes
  text = "\n".join(getattr(p, "text", "") or "" for p in res.pages)
  ```
  `res` is a `ParseResult`; each `res.pages[i]` has `.text` (and `.text_items`, `.markdown`, `.width`, `.height`). OCR text lands in `.text`.
  **PATH note:** the npm `liteparse` binary must be on PATH (`C:/Users/khoans/AppData/Roaming/npm`) for `shutil.which("liteparse")`. **Native Windows path only** — never MSYS `/c/...` (node can't expand it; yields `ENOENT ... 'C:\c\Users\...'`). When running a parser that imports a local module, set `PYTHONPATH="C:/Users/khoans/Documents/Warren_OS_Local/vault/10_OPERATION_DATA/scripts/modules"` (native form, not `/c/...`) and `LUSINE_HEADLESS=1`.
**Do NOT assume `liteparse.parse()` exists.** The npm CLI is the canonical OCR engine; the python package is a thin wrapper that drifted.

### ⚠️ Warren preference: debug liteparse, don't abandon it
If a parser or workflow "fails" on liteparse (API error, empty output, drift), **debug the call — do NOT switch to a different method or hand-feed JSON as a permanent workaround.** In session 2026-07-13 a parser called the removed `liteparse.parse()` API; the first reflex was to bypass liteparse via `--test-json`. Warren explicitly pushed back: *"tôi vẫn muốn xài liteparse... check kỹ lại"*. The correct fix was patching the parser to call the npm CLI / `LiteParse` class. Keep liteparse as the primary OCR path; fix the integration, not the tool choice. (The `--test-json` bypass is fine as a ONE-OFF for a known-bad screenshot, but the parser itself must use liteparse.)

**Related:** `vault/10_OPERATION_DATA/parsers/revenue_screenshot_parser.py` was patched (v2.x) to call the npm CLI with a python-module fallback — see `references/liteparse-python-api.md` for the verified recipe.

### Pitfall: `vision_analyze` returns 404 "No endpoints found that support image input" — NOT a broken image
**Symptom:** After liteparse output is empty, you call `vision_analyze(image_url=...)` and get `Error code: 404 - {'error': {'message': 'No endpoints found that support image input', 'code': 404}}`.
**Cause:** The active model provider (e.g. `kilocode` / tencent free tier) has NO vision capability — `vision_analyze` cannot attach the image to any model. This is a PROVIDER limitation, not a corrupt file. liteparse itself still works (it OCRs locally).
**Fix / fallback chain when vision is unavailable:**
1. Run `liteparse parse "<img>"` (terminal) — it OCRs the image locally and returns text. This is the PRIMARY path and usually sufficient.
2. If liteparse text is also empty (truly blank image), report to Warren: "Ảnh trắng / không có nội dung — liteparse + vision đều không đọc được" and ask for a re-screenshot.
3. Do NOT loop on `vision_analyze` — the 404 is deterministic for this provider; retrying wastes a turn.
### Pitfall: `vision_analyze` returns 402 "requires more credits" — also a provider limit
**Symptom:** `vision_analyze` fails with `Error code: 402 - {'error': {'message': 'This request requires more credits...', 'code': 402}}`. This happened on the `tencent/hy3:free` (kilo) provider when an image was attached.
**Cause:** Free-tier provider credit cap, NOT a corrupt image. liteparse (local OCR) is unaffected.
**Fix:** Run `liteparse parse "<img>"` (terminal) — it OCRs locally and returns text. If vision was needed for a non-OCR reason, report the credit limit to Warren rather than looping. Same class as the 404 pitfall: provider limitation, not a file problem.
### Wide-table column-region crop (technique for tables wider than ~1000px with side-by-side store columns)
When liteparse drops entire columns (e.g. a 1258px PNG with 3 store columns side by side), single-pass OCR merges/drops cells — only role names came through, all numbers and 2 store columns vanished. Fix: split vertically into N column regions, upscale 4x, OCR each separately, then merge.
```python
from PIL import Image, ImageEnhance
img = Image.open(src).convert('L'); w,h = img.size
thirds = [(0,w//3),(w//3,2*w//3),(2*w//3,w)]
for i,(x0,x1) in enumerate(thirds):
    c = img.crop((x0,0,x1,h))
    c = ImageEnhance.Contrast(c).enhance(3.0).resize((c.width*4,c.height*4), Image.LANCZOS)
    c.save(f'col{i+1}.png')
```
Then `liteparse parse col1.png -o col1.lit.txt` per column. This recovered store-column data liteparse missed in one pass.
Note: if `python3 -c "from PIL..."` fails with `_imaging` ImportError, use `python` (venv 3.11, PIL 12.2.0 works) — env-specific, verify on your machine.

### Pitfall: fabricating names/roles not in the source
liteparse/markitdown return raw text — they do NOT name people. If a parsed file shows a role (e.g. "FOH Management (ARM)") with no name, do NOT assign a name from memory or another store. Flag "source names no one" and ask Warren. In one session Hermes wrongly implied "Jack = LU7 manager" from a LU7 xlsx that named nobody — Jack is LU3 RM. Attribution errors corrupt the SSOT.

### Pitfall: search_files MISSES existing files on Windows MSYS — verify with terminal
**Symptom:** You run `search_files(target='files', pattern='*')` on a path the user gave you and get `total_count: 0`, then conclude "file/folder doesn't exist" — but it IS there (user insists, or `ls` proves it).
**Cause:** `search_files` (ripgrep-backed) intermittently fails to enumerate files under certain MSYS path layouts or when sibling `.smart-env/` index dirs exist. It is NOT a reliable "file absent" proof on this Windows host.
**Fix (HARD RULE):** When a user says a file/folder EXISTS at a path you searched and got 0 — DO NOT argue. Verify with terminal immediately:
```bash
ls -la "C:/Users/khoans/.../path/" 2>&1
find "C:/Users/khoans/.../path" -iname "*PNJ*" 2>/dev/null
```
If `ls` shows the file → your earlier search_files was wrong, not the user. Read the real file. Session 2026-07-17: user pointed at `040-PNJ/` (4 files: Thesis.md, Anti-thesis.md, BCTC-Rolling.md, Catalyst-watch.md) — search_files returned 0, `ls` returned all 4. Concluding "vault is empty / no thesis" from search_files alone wasted 3 turns and made Hermes look like it "doesn't read the vault." Terminal is the source of truth for existence.
**Same pitfall** documented in `vault-simplify-ssot` §3 (Windows MSYS tool workaround). Both skills enforce: terminal grep/find > search_files for existence checks.

### Pitfall: liteparse returns only a few words on a content-rich image
Symptom: image clearly has text (e.g. a promo/screenshot) but `liteparse parse` returns 1–3 lines or near-empty. Cause: low contrast, small font, or stylized text defeats the default OCR render pass.
Fix: run the PIL enhancement pipeline BEFORE re-parsing — `contrast ×2.5–2.8` + `resize ×3` (LANCZOS) on a grayscale copy, then `liteparse parse <enhanced.png>`. This recovered fuller text (promo time-windows, scope lines) that the raw pass dropped. See `references/image-ocr.md` for the full 4-step pipeline.
Note: if `python3 -c "from PIL..."` fails with `_imaging` ImportError, use `python` (3.11 venv) — covered in the vision-404 pitfall above.

### Pitfall: PIL ImportError on `python3` (Hermes venv) — use `python`
When preprocessing images (contrast/upscale before re-OCR), `from PIL import Image` fails on the default `python3` (Hermes agent venv, `ImportError: cannot import name '_imaging'`). Fix: invoke the 3.11 venv interpreter explicitly — `python` (not `python3`) has PIL 12.2.0 working on this machine.
Also: liteparse OCR on **stylized marketing images** (gradient bg, large display type, few words) often returns sparse/empty text (e.g. a promo poster returned only "Morning" + "Sunset happy hours"). Always try the 4-step PIL preprocess (grayscale → contrast ×2.5–3 → upscale ×3–4 → re-OCR) before concluding "image is blank". Session 2026-07-12: a LU5/LU7 promo screenshot OCR'd near-empty first pass, recovered key text ("From 10:00 AM to 11:30 AM at L'Usine Saigon Centre for all drinks & dessert") after contrast+upscale.

### So sánh & chọn output tốt nhất

## Adopt rules
- Use this skill for ALL file-to-text parsing across any Hermes workflow
- Never silently switch to `vision_analyze` without attempting liteparse first
- No other tool should be used for Warren's file parsing needs unless explicitly directed
- Never fabricate names/roles absent from parsed output — flag unknowns, ask Warren
- Use this skill for ALL file-to-text parsing across any Hermes workflow
- Never silently switch to `vision_analyze` without attempting liteparse first
- No other tool should be used for Warren's file parsing needs unless explicitly directed
