---
name: legal-document-ingest
description: "Process legal/official PDFs (court rulings, contracts, decisions) — OCR với liteparse + Vietnamese → structured field extraction → cross-reference user's verbal claims → flag discrepancies → update PERSONAL_CONTEXT → set calendar reminders."
version: 1.1.0
author: Hermes Agent
tags: [legal, court, vault, OCR, vietnamese, document-processing, calendar]
---

# /legal-document-ingest — Legal Document Processing Pipeline

## Purpose

Process Vietnamese legal/official PDF documents (court rulings, divorce decrees, custody orders, contracts) into structured vault data with cross-reference checking.

**Context:** Warren's personal domain — family law, child support, custody, property. Always Tiếng Việt có dấu.

## Trigger

User mentions any of:
- Case closed / tòa ra quyết định / ly hôn xong
- "có quyết định / phán quyết / giấy tờ tòa"
- Sends or references official PDF/JPG from court or legal proceeding
- Gives verbal numbers (amounts, dates, schedules) that should match a document

## Workflow

### Phase 1 — Document OCR & Archive

```bash
# 1. Copy PDF to vault/legal/
cp "<source.pdf>" "/c/Users/khoans/Documents/Stock_OS/stock_vault/legal/<filename>"

# 2. Parse with liteparse — ALWAYS use --ocr-language vie for Vietnamese
liteparse parse "/path/to/doc.pdf" --format text --ocr-language vie \
  -o "/path/to/doc.txt"
```

**Rule:** `--ocr-language vie` is REQUIRED for Vietnamese documents. Default `eng` garbles diacritics (ơ, ở, ă, ấ, ậ).

### Phase 2 — Structured Field Extraction

Parse the extracted text for these key-value pairs:

| Field | Extract pattern | Example |
|-------|---------------|---------|
| Document type | Header phrases | `QUYẾT ĐỊNH CÔNG NHẬN THUẬN TÌNH LY HÔN` |
| Case number | `Số: …/YYYY/QĐST-…` | 575/2026/QĐST-HNGĐ |
| Ruling date | `ngày … tháng … năm …` | 25 tháng 6 năm 2026 |
| Petitioner | `Nguyên đơn:` | Bà Phạm Vũ Phương Khanh |
| Respondent | `Bị đơn:` | Ông Nguyễn Sĩ Khoa |
| Child(ren) | `con chung là … - sinh ngày …` | Nguyễn Phạm Gia Gia, 13/02/2020 |
| Custody | `giao con chung cho …` | bà Khanh trực tiếp nuôi dưỡng |
| Support amount | `cấp dưỡng nuôi con là … đồng/tháng` | 11.000.000 |
| Due date | `cấp dưỡng vào ngày … dương lịch` | ngày 10 |
| Start date | `bắt đầu cấp dưỡng từ ngày …` | 10/7/2026 |
| Visitation | `quyền thăm nom con` | Ông Khoa có quyền thăm nom |
| Property | `Về tài sản chung:` | tự thỏa thuận / không yêu cầu |
| Debt | `Về nợ chung:` | không có |
| Late interest | `Điều 468 Bộ luật dân sự` | khoản 2 Điều 468 (10%/năm) |

### Phase 3 — Cross-Reference & Discrepancy Flagging ⚠️ (CRITICAL)

Compare the user's verbal claims against the document text:

```
User says:         "cấp dưỡng 11 triệu vào ngày 11"
Document says:     "11.000.000 đồng/tháng, vào ngày 10"
Discrepancy:       ❌ Ngày 11 (user) ≠ ngày 10 (document)
Action:            Flag IMMEDIATELY. Do not proceed with calendar/reminder
                   until user confirms which date is correct.
```

**Why:** Warren may remember approximate dates/amounts. The document is authoritative. Flags prevent wrong calendar entries or missed obligations.

Always present a clear comparison table, e.g.:

| Field | User said | Document | Match? |
|-------|----------|----------|--------|
| Amount | 11M | 11.000.000 | ✅ |
| Date | ngày 11 | ngày 10 | ❌ |

### Phase 4 — Update Vault State

After user confirms corrections:

1. **PERSONAL_CONTEXT.md** — update relevant sections:
   - Marital status: `separated` → `divorced`
   - Child support: add amount, schedule, start date
   - Case status: mark case as closed

2. **Journal entry** — log milestone in vault journal:
   - Case number, ruling date, key terms
   - PDF archived at `legal/<filename>`

3. **Raw memory log** — append to `_personal_memory_raw.md` (durable facts only):
   - Preferences established (e.g. "ngày 10 theo quyết định")
   - Corrections learned

### Phase 5 — Set Calendar / Reminders

Based on document obligations, propose calendar events:

| Obligation | Calendar event |
|-----------|---------------|
| Monthly child support | Recurring event: ngày X mỗi tháng, 09:00, "Cấp dưỡng GG — XXM" |
| Court hearing / review | One-off event |
| Enforcement deadlines | One-off event |

Use Google Calendar recurring events with Python API (google-workspace skill CLI does not support `--recurrence`):

```python
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# Load token from profile path
token_path = Path("C:/Users/khoans/AppData/Local/hermes/profiles/personal_profile/google_token.json")
creds = Credentials.from_authorized_user_file(str(token_path))
service = build('calendar', 'v3', credentials=creds)

event = {
    'summary': '💰 Cấp dưỡng GG — 11M',
    'description': 'Chuyển khoản cấp dưỡng cho GG 11,000,000 VND. Hạn: ngày 10 hàng tháng.',
    'start': {'dateTime': '2026-07-10T09:00:00+07:00', 'timeZone': 'Asia/Ho_Chi_Minh'},
    'end': {'dateTime': '2026-07-10T09:15:00+07:00', 'timeZone': 'Asia/Ho_Chi_Minh'},
    'recurrence': ['RRULE:FREQ=MONTHLY;BYMONTHDAY=10;COUNT=120'],
    'reminders': {
        'useDefault': False,
        'overrides': [
            {'method': 'email', 'minutes': 1440},   # 1 day before
            {'method': 'popup', 'minutes': 30},      # 30 min before
        ],
    },
}
service.events().insert(calendarId='primary', body=event).execute()
```

Pre-flight checklist (5 points) required before creating/deleting calendar events (see SOUL.md §6 or personal_profile_pre_edit_checklist.md §10).

## Pitfalls

- **OCR language MUST be `vie`** for Vietnamese documents. Default `eng` produces unreadable output.
- **OCR errors on names:** Vietnamese proper names (Nguyễn, Phạm, Vũ, Phương) often get garbled — compare against user-provided details.
- **Money format:** Vietnamese uses `.` as thousands separator: `11.000.000` = 11 million. NOT decimal.
- **Date formats vary:** `ngày 25 tháng 6 năm 2026` / `25/6/2026` / `ngày 25/6/2026` — normalize to YYYY-MM-DD.
- **Cross-reference is not optional:** Always compare user's verbal numbers against document before acting.
- **Calendar auth check:** Google token may be at profile path, not `~/.hermes/`. Set `HERMES_HOME` env var: `export HERMES_HOME="/c/Users/khoans/AppData/Local/hermes/profiles/personal_profile"`
- **liteparse availability:** Verify with `which liteparse` first. If not available, fall back to pymupdf (text) or pymupdf+vision (scanned).
- **PDF đôi (multi-case):** One PDF may contain multiple unrelated court decisions (e.g. divorce ruling + commercial loan case scanned together). After parsing, scan for distinct document headers (`Số: …/YYYY/…`). Extract fields ONLY from the relevant case — do not mix fields across cases. If unsure, ask Warren which case he's referring to.
- **Phân biệt luật vs thực tế:** Khi update vault về access/visitation (`quyền thăm nom`), ghi NHẸ cả hai mặt: (1) quyền theo QĐ tòa và (2) thực tế đời sống (vd "thực tế vẫn bị cản trở"). Không ghi luật suông mà bỏ qua reality.
- **Ngày bắt đầu đã qua:** Nếu ngày bắt đầu cấp dưỡng trong QĐ đã qua, set calendar từ kỳ tiếp theo. Luôn check `date.today()` vs start date trước khi tạo event.

## Vault Structure

```
stock_vault/
  legal/
    <case_type>_<date>.pdf         # Original PDF
    <case_type>_<date>.txt         # OCR text output
  _inbox/_personal_memory_raw.md   # Durable facts log
  00_CORE_LOGIC/PERSONAL_CONTEXT.md  # State update target
  _journal/                         # Milestone entries
```

## Related Skills

- `ocr-and-documents` — base PDF OCR pipeline (liteparse → pymupdf → marker-pdf)
- `capture-sleep` — similar ingest->parse->vault pattern (health domain)
- `google-workspace` — Google Calendar auth + event creation (protected skill)

## MANDATORY VERIFY GATE (rule: never trust LLM, verify everything)

After EVERY parser run that reads Excel/CSV/PDF ([DOMAIN: legal PDF (court ruling, contract)]), MUST run verify-parser-output gate BEFORE reporting numbers or committing.

1. Independent recompute (fresh script, different method).
2. Cross-assert EVERY number (giá, P&L, room, %Δ, số dư, headcount) vs LLM output.
3. Category-drop scan: count raw rows vs filtered; flag dropped (mã rỗng, dòng tổng, Loc=NaN).
4. Emit VERIFY_RESULT: PASS|FAIL + dropped count. Temp hermes-verify-*.py, clean after.
5. FAIL → LLM wrong until proven. Fix logic, re-run, re-verify.
