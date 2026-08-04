---
name: bctc-pdf-ingest
description: "Ingest BCTC (báo cáo tài chính) PDF files — audited annual reports, BCTC kiểm toán hợp nhất — into existing ticker thesis files. Extract text, reconcile broker data vs audited, update Thesis.md + BCTC-Rolling.md + wiki log."
version: 1.1
tags: [trading, bctc, pdf, thesis, vnstock, personal_os]
---

# /personal-stock-ingest — BCTC PDF Ingest Pipeline

## Trigger
User invokes `/stock-ingest` or `/personal-stock-ingest` with a PDF file (BCTC kiểm toán hợp nhất, báo cáo thường niên) for a specific ticker.

## Goal
Update vault thesis files with verified audited data. Reconcile secondary sources (TCBS, broker reports) against audited statements.

## Step 1 — Identify File Type
- **BCTC kiểm toán hợp nhất**: ~30-60 pages, standalone, balance sheet + P&L + cash flow + notes
- **Báo cáo thường niên**: 80-100+ pages, business review + BCTC section at end (last 15-20 pages)
- **Broker research**: secondary source — always cross-check against audited

## Step 2 — Extract PDF Text

### Primary method: liteparse (OCR + text)
Per stock-ingest PDF Parse Rule: mọi PDF input phải đi qua liteparse trước.

```bash
liteparse parse "input.pdf" -o "output.txt"
```

**Batch mode** (nhiều BCTC cùng lúc): chain các liteparse call trong một terminal(
```bash
liteparse parse "file1.pdf" -o "out1.txt" 2>&1 | tail -1 && \
liteparse parse "file2.pdf" -o "out2.txt" 2>&1 | tail -1
```
Tested: 6 files × ~40 trang ~2 phút.

Lưu ý OCR output: liteparse OCR có noise trên chữ Việt (dấu bị méo, khoảng cách lỗi) nhưng số liệu và bảng tài chính vẫn đọc được. Khi search/extract số liệu, viết pattern linh hoạt (không hardcode exact Vietnamese string).

### Fallback: PyMuPDF (khi liteparse không available hoặc PDF có text layer)
Hermes venv path on this machine:
```
/c/Users/khoans/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe
```

**DO NOT use `python3`** — it's Windows Store Python without PyMuPDF. Verify with:
```
/c/Users/khoans/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe -c "import fitz; print('OK')"
```

Extract in 2 batches via temp scripts:
- Pages 1-20: context (management discussion, KQKD summary, segment breakdowns)
- Last 15-20 pages (or pages 70-88 for annual reports): actual BCTC (balance sheet, P&L, cash flow, audit report, notes)

## Step 3 — Read Existing Vault
Read `030-Companies/<ticker-code>/Thesis.md` and `BCTC - Rolling.md`.

## Step 4 — Extract & Reconcile

### Key data from PDF:
- **Balance Sheet**: total assets, cash + ST investments + lending, inventory (gross + provision), payables, borrowings, equity
- **P&L**: revenue, gross profit + margin, financial income, OPEX, operating profit, pre-tax profit, net profit (parent + minority), **EPS (basic + diluted)**
- **Cash Flow**: OCF, ICF, FCF, capex, dividends paid, share buybacks
- **Audit**: auditor (Big 4?), date, opinion type (unqualified, qualified, emphasis)

### Reconciliation table:
```
| Chỉ tiêu | TCBS / Broker | Audited | Sai lệch |
|----------|--------------|---------|----------|
| Revenue  | 155.928 tỷ  | 155.928 tỷ | ✅ Khớp |
| Thu nhập TC | 2.912 tỷ | 3.107 tỷ | ⚠️ +195 tỷ |
```

Common discrepancies: financial income rounding, ROE method (closing vs avg equity), cash inclusion of phải thu về cho vay.

## Step 5 — Update Files

**BCTC - Rolling.md**: Full rewrite — balance sheet breakdown, P&L, cash flow, ratios, reconciliation section. Frontmatter: last_updated, source_files, review_log.

**Thesis.md**: Targeted patches — EPS, OCF, trailing P/E, integrity gate, dự phóng actual row, review_log, frontmatter source_files.

**Wiki log.md**: Append to current date section.

## Step 6 — Language
- Vault files: Vietnamese có dấu — **KHÔNG viết tắt tiếng Việt.** Viết đầy đủ: "ngân hàng", "trung dài hạn", "Kho bạc Nhà nước", "bất động sản", "lợi nhuận", "tiền mặt", "cổ phiếu", "tài sản bảo đảm", "quản trị rủi ro". Giữ nguyên thuật ngữ tiếng Anh chuẩn (EPS, OCF, P/E, CAGR, ROE).
- Table labels: Vietnamese; values/numbers as-is
- Keywords: keep English (EPS, OCF, P/E, CAGR)

## Pitfalls
- **Hermes venv vs system python**: PyMuPDF only in Hermes venv, not `python3` (fallback method — liteparse is primary)
- **Broker report appendix ≠ enough for integrity gate**: TCBS/SSI initiation reports có balance sheet + P&L appendix (từ BCTC kiểm toán → [HIGH]) nhưng THIẾU cash flow statement và thuyết minh RPT. Kết quả: check 1 (OCF) + check 3 (RPT) không chạy được → verdict sai. Ví dụ BID 2026-07-04: broker-only = FAIL 1.5/5, full BCTC = PASS 4/5. **Luôn đòi BCTC gốc (file CBTT riêng, có cash flow + notes) để chốt integrity gate.**
- **Liteparse OCR noise**: Vietnamese diacritics get distorted. Numbers and tables remain accurate. Write search patterns flexibly — avoid exact Vietnamese string matching. See `references/ocr-noise-data-extraction.md` for pattern guide.
- **Batch parsing overhead**: 5+ BCTCs ~2 phút với liteparse. Chạy sequential bằng `&&` chain. Set terminal timeout ≥300s.
- **Annual reports are verbose**: Extract selectively — BCTC section + KQKD summary only
- **Markdown table malformation**: Re-read after each patch; misaligned tables need manual fixing
- **BCTC - Rolling.md is growing file**: Newest year on top
- **Broker rounding ≤7%**: Flag but don't alarm

## Related
- `capture-stock` skill — daily/weekly pulse entries (different pipeline)
- `stock-ingest` — BCTC analysis + thesis pipeline
- Vault path: `30_KNOWLEDGE_BASE/wiki/03_Investing/VN_Equities/030-Companies/<code>/`

## MANDATORY VERIFY GATE (rule: never trust LLM, verify everything)

After EVERY parser run that reads Excel/CSV/PDF ([DOMAIN: BCTC PDF (báo cáo tài chính)]), MUST run verify-parser-output gate BEFORE reporting numbers or committing.

1. Independent recompute (fresh script, different method).
2. Cross-assert EVERY number (giá, P&L, room, %Δ, số dư, headcount) vs LLM output.
3. Category-drop scan: count raw rows vs filtered; flag dropped (mã rỗng, dòng tổng, Loc=NaN).
4. Emit VERIFY_RESULT: PASS|FAIL + dropped count. Temp hermes-verify-*.py, clean after.
5. FAIL → LLM wrong until proven. Fix logic, re-run, re-verify.
