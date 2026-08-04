---
name: personal-case-lifecycle
description: "Quản lý vòng đời case files trong personal vault — mở case mới, cập nhật timeline, đóng case (update → move → index)."
version: 1.0.0
author: Hermes
tags: [personal, vault, case-management, workflow, legal]
---

# Personal Case Lifecycle — Vault Case Management

> Thao tác với case files trong `stock_vault/_cases/`. Áp dụng cho mọi case
> (legal, health, finance, etc.) sau khi có kết quả hoặc cần cập nhật.

## Cấu trúc Vault

```
_cases/
  00_CASES_INDEX.md      # Master index — auto-sync bởi Hermes
  active/                 # Case đang mở — mỗi case 1 file
  closed/                 # Case đã đóng
```

## File Format

```yaml
---
status: OPEN | CLOSED
domain: legal | health | finance | ...
opened: YYYY-MM-DD
closed: YYYY-MM-DD          # CHỈ khi CLOSED
priority: high | medium | low
stakeholders: [Warren, ...]
tags: [tag1, tag2, ...]
last_updated: YYYY-MM-DD
outcome: "..."              # CHỈ khi CLOSED — mô tả ngắn kết quả
---
```

## Quy trình ĐÓNG CASE 🚨 (dễ quên bước)

Khi một case được giải quyết (tòa ra QĐ, hoà giải xong, etc.), Hermes phải làm
**ĐỦ 4 bước — không thiếu bước nào:**

### Bước 1 — UPDATE case file (trong `active/`)

```bash
# Frontmatter changes:
status: OPEN → CLOSED
# Thêm:
closed: YYYY-MM-DD
outcome: "Mô tả ngắn kết quả cuối cùng"
tags: +closed
```

Prepends timeline entry mới ở đầu section `## Timeline (newest on top)`:

```markdown
### YYYY-MM-DD -- ✅ CASE CLOSED: [kết quả chính]
**Source:** [nguồn]
**Type:** kết quả chính thức

**Kết quả cuối cùng:**
- [điểm 1]
- [điểm 2]
- ...
```

### Bước 2 — MOVE file từ `active/` → `closed/`

```bash
cp "active/<slug>.md" "closed/<slug>.md" && rm "active/<slug>.md"
```

> `mv` không dùng được trên Windows cross-filesystem. Dùng `cp + rm`.

### Bước 3 — UPDATE index `00_CASES_INDEX.md`

- **Remove** khỏi Active Cases table
- **Add** vào Closed Cases table:
  ```markdown
  | case_id | title | opened | closed | domain | priority | outcome |
  |---------|-------|--------|--------|--------|----------|---------|
  | `<slug>` | [title] | YYYY-MM-DD | YYYY-MM-DD | [domain] | [priority] | [outcome ngắn] |
  ```
- **File note:** `> 📂 File: _cases/closed/<slug>.md`
- **Frontmatter:** update `last_updated` và `total_entries`

### Bước 4 — Cập nhật context (nếu case ảnh hưởng state)

- Update `00_CORE_LOGIC/PERSONAL_CONTEXT.md` nếu marital/health/finance thay đổi
- Tạo journal entry tại `_journal/YYYY-MM-DD.md`
- Ghi durable fact vào `_inbox/_personal_memory_raw.md`

## Quy trình MỞ case mới

1. Tạo file tại `_cases/active/<slug>.md` với frontmatter đầy đủ (status=OPEN)
2. Thêm vào `00_CASES_INDEX.md` Active Cases table
3. Update frontmatter của index (last_updated, total_entries)

## Timeline Entry Format

```markdown
### YYYY-MM-DD -- Tiêu đề
**Source:** [nguồn — conversation / file / document]
**Type:** [phân tích | kết quả | cập nhật | ...]

Nội dung chi tiết...
```

Mỗi entry **prepend** lên đầu section (newest on top).

## Pitfalls

| # | Pitfall | Fix |
|---|---------|-----|
| 1 | **Quên update index sau khi move file** | Luôn làm bước 3 NGAY sau bước 2 — không rời tay giữa chừng |
| 2 | **Outcome mơ hồ, thiếu số liệu** | Ghi cụ thể: số tiền, ngày tháng, điều khoản. Không ghi "đã giải quyết" |
| 3 | **Quên scan/lưu văn bản pháp lý** | Trước khi đóng case, copy PDF gốc vào `vault/legal/` và parse bằng liteparse |
| 4 | **Không prepend timeline entry** | Entry mới luôn ở TRÊN CÙNG — không append cuối |
| 5 | **Case active folder rỗng nhưng index vẫn show active** | Kiểm tra: active/ có file ko? Nếu ko, index phải ghi "Không có case active nào" |
| 6 | **Legal citation lỗi thời (stale law ref)** | Case cũ có thể cite sai luật đang hiệu lực (vd: case ly hôn 07/2026 vẫn dẫn LHN&GĐ 2014 dù luật 2024 đã có hiệu lực 01/01/2025). LUÔN verify số điều/luật bằng **bản gốc trong `vault/legal/`** (QĐ tòa, biên bản), không tin tóm tắt của case cũ. Gặp bất thường → FLAG trung thực, không bịa giải thích. |

## Related Skills

- `legal-document-ingest` — xử lý PDF + extract fields + cross-reference + calendar (dùng kèm khi đóng case legal)
- `personal-inbox-routing` — xử lý inbox items
- `personal-process-notes` — xử lý notes vào vault

## MANDATORY VERIFY GATE (rule: never trust LLM, verify everything)

After EVERY parser run that reads Excel/CSV/PDF ([DOMAIN: case files (status, timeline)]), MUST run verify-parser-output gate BEFORE reporting numbers or committing.

1. Independent recompute (fresh script, different method).
2. Cross-assert EVERY number (giá, P&L, room, %Δ, số dư, headcount) vs LLM output.
3. Category-drop scan: count raw rows vs filtered; flag dropped (mã rỗng, dòng tổng, Loc=NaN).
4. Emit VERIFY_RESULT: PASS|FAIL + dropped count. Temp hermes-verify-*.py, clean after.
5. FAIL → LLM wrong until proven. Fix logic, re-run, re-verify.
