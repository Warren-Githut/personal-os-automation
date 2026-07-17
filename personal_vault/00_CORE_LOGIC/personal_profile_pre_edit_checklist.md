---
name: Pre-Edit Checklist
type: template
status: active
owner: Hermes
scope: Mọi write/create/edit + external action trong personal vault và Hermes operations
last_updated: 2026-06-29
---

# Pre-Edit Checklist — Personal Profile

**MUST READ trước khi Hermes thực hiện bất kỳ write/create/edit operation nào trong personal vault.**
Checklist này là **process protocol** — verify + flag, không bao giờ override content.

---

## 1. ĐỌC FILE HIỆN TẠI (nếu file đã tồn tại)

- [ ] `read_file(path, limit=40)` — đọc 40 dòng đầu để xem format
- [ ] Nếu là file tracker/log: xác định **template block** (`<!-- HERMES TEMPLATE -->` hoặc format comment)
- [ ] Nếu là file mới: kiểm tra **canonical path** từ vault structure (SOUL.md §3) trước khi tạo

## 2. KIỂM TRA FRONTMATTER

- [ ] YAML frontmatter `---` đóng/mở đúng?
- [ ] Các field bắt buộc có đủ?
  - `name`, `type`, `status`, `owner`, `cadence`, `data_quality`, `last_updated`
  - Hoặc theo schema riêng của personal vault: `domain`, `type`, `status`, `created`, `last_updated`, `tags`
- [ ] `last_updated` khớp với ngày hôm nay?

## 3. TEMPLATE BLOCK

- [ ] HTML comment template (`<!-- ... -->`) có ở đầu file (sau frontmatter)?
- [ ] Nếu có: parse kỹ cấu trúc — số sections, thứ tự, emoji markers
- [ ] Nếu không có: entry gần nhất là reference format

## 4. KIỂM TRA COLUMN / FIELD ALIGNMENT (QUAN TRỌNG NHẤT)

- [ ] **Đếm số pipe (`|`)** trên header row
- [ ] **Đếm số pipe** trên data row mẫu
- [ ] Nếu số pipe không bằng nhau → **FLAG NGAY, không silent write**
  - Nguyên nhân thường gặp: thiếu pipe closing (`row = f"| {hour}"` → thiếu `|`)
- [ ] Kiểm tra number of columns = header columns count

## 5. APPEND — NEWEST ON TOP

- [ ] Entry mới prepend lên **ĐẦU** file (sau frontmatter + template)
- [ ] **KHÔNG** xoá entry cũ — chỉ thay thế entry của cùng week nếu overwrite
- [ ] Regex pattern cho overwrite: `rf"(## {re.escape(week_id)}.*?)(?=\n## |\Z)"`

## 6. FRONTMATTER SYNC

- [ ] Update `last_updated` = `date.today().isoformat()`
- [ ] Update `data_quality` nếu cần

## 7. VAULT STRUCTURE CHECK

- [ ] File nằm đúng thư mục theo vault structure (SOUL.md §3)?
- [ ] Nếu có file index tương ứng → update metadata (last_updated, tags)

## 8. VERIFY IDEMPOTENCY

- [ ] Chạy parser/script lần 2 → output giống hệt lần 1
- [ ] Template ở đúng vị trí (sau frontmatter, trước entry đầu)
- [ ] **KHÔNG có duplicate frontmatter** ở cuối file
- [ ] File kết thúc cleanly

## 9. NGÔN NGỮ — TIẾNG VIỆT CÓ DẤU (BẮT BUỘC)

- [ ] **TẤT CẢ** nội dung human-facing trong vault file = Tiếng Việt có dấu
- [ ] Kiểm tra: Executive Summary, Flags, insight text, mô tả — KHÔNG viết tiếng Anh
- [ ] Ngoại lệ (được phép tiếng Anh):
  - Tên cột trong bảng dữ liệu (Amount, Date, Category, etc.)
  - Code comments, YAML frontmatter fields
  - Agent identity files (SOUL.md)
  - Stock tickers, financial terms (EPS, P/E, OCF, NI)
- [ ] Nếu phát hiện tiếng Anh trong nội dung → **sửa trước khi commit**

---

## Common Bugs Checklist (historical)

| Bug | Checklist check |
|-----|-----------------|
| Column shift | **§4: count pipes** — header số pipe = data số pipe |
| Duplicate frontmatter ở cuối file | **§8: verify** — grep `---` cuối file |
| Wrong date format | **§2: frontmatter** — check last_updated = hôm nay |
| Nội dung tiếng Anh thay vì Tiếng Việt có dấu | **§9: ngôn ngữ** — kiểm tra từng dòng human-facing text |
| Template sai cấu trúc | **§3: template block** — đọc HTML comment template TRƯỚC khi write |

---

## 10. EXTERNAL ACTION APPROVAL — 5-Point Checklist 🛑

> Áp dụng cho MỌI hành động chạm đến: người khác, production data, tiền, hệ thống, public.
> Không gồm: task nội bộ trong conversation (search, đọc, tính toán, draft nội bộ).
> Checklist này là **gate protocol** — Hermes phải show 5 points trước khi act, CHỈ act sau Warren OK.

### Process

Trước mỗi external action, Hermes trình bày đủ 5 points:

| # | Point | Nội dung |
|---|-------|----------|
| 1 | **WHAT** 🎯 | Hành động cụ thể sắp làm — "Tôi sắp [action]" |
| 2 | **WHY** 🤔 | Lý do / context / benefit — "Vì [lý do]" |
| 3 | **EXACT CONTENT** 📝 | Nội dung chính xác: file path, message text, command, số tiền, config change |
| 4 | **RISK** ⚠️ | What could go wrong + severity (HIGH/MOD/LOW) |
| 5 | **APPROVAL** ✅ | Câu hỏi: "Anh OK cho tôi chạy ko?" |

### Quy tắc

- **Chưa show đủ 5 points → KHÔNG act**
- **Warren chưa nói OK → KHÔNG act**
- Nếu Warren nói "sửa [detail]" → Hermes sửa → show lại points 3 (content) + 5 (approval)
- Nếu Warren nói "ko" → dừng, ko hỏi lại
- Task trong Zone 🟢 (tự làm hoàn toàn) → không cần checklist này

### Ví dụ

```
Hermes: 🛑 PRE-FLIGHT CHECK
1. WHAT: Ghi health log vào personal vault
2. WHY: Warren vừa cập nhật sleep data trong conversation
3. EXACT CONTENT: personal_vault/health/sleep_2026-06.md — append entry mới
4. RISK: [LOW] — personal data, reversible
5. APPROVAL: Anh OK cho tôi ghi ko?
```

> **Warren: OK** → Hermes ghi.
> **Warren: sửa số liệu** → Hermes sửa → show lại point 3 + 5.
> **Warren: ko** → Hermes dừng.
