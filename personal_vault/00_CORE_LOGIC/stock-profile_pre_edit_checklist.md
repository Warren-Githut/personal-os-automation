---
name: Pre-Edit Checklist
type: template
status: active
owner: Hermes
scope: Mọi write/create/edit + external action trong stock analysis và Hermes operations
last_updated: 2026-06-29
---

# Pre-Edit Checklist — Stock Profile

**MUST READ trước khi Hermes thực hiện bất kỳ write/create/edit operation nào liên quan đến stock analysis.**
Checklist này là **process protocol** — verify + flag, không bao giờ override content.

---

## 1. ĐỌC FILE HIỆN TẠI (nếu file đã tồn tại)

- [ ] `read_file(path, limit=40)` — đọc 40 dòng đầu để xem format
- [ ] Nếu là file tracker/log: xác định **template block** (`<!-- HERMES TEMPLATE -->` hoặc format comment)
- [ ] Nếu là file mới: kiểm tra **canonical path** từ vault structure trước khi tạo

## 2. KIỂM TRA FRONTMATTER

- [ ] YAML frontmatter `---` đóng/mở đúng?
- [ ] Các field bắt buộc có đủ?
  - `domain`, `type`, `status`, `created`, `last_updated`, `tags`
  - `tickers`, `brokers`, `report_dates` (nếu là BCTC analysis)
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
- [ ] Update `tags` nếu có ticker/event mới

## 7. VAULT STRUCTURE CHECK

- [ ] File nằm đúng thư mục trong personal vault (investing/, etc.)
- [ ] Nếu có file index tương ứng → update metadata

## 8. VERIFY IDEMPOTENCY

- [ ] Chạy parser/script lần 2 → output giống hệt lần 1
- [ ] Template ở đúng vị trí (sau frontmatter, trước entry đầu)
- [ ] **KHÔNG có duplicate frontmatter** ở cuối file
- [ ] File kết thúc cleanly

## 9. NGÔN NGỮ — TIẾNG VIỆT CÓ DẤU (BẮT BUỘC)

- [ ] **TẤT CẢ** nội dung human-facing trong vault file = Tiếng Việt có dấu
- [ ] Kiểm tra: Executive Summary, Flags, insight text, mô tả — KHÔNG viết tiếng Anh
- [ ] Ngoại lệ (được phép tiếng Anh):
  - Tên cột trong bảng dữ liệu (Ticker, P/E, EPS, OCF, Revenue, etc.)
  - Code comments, YAML frontmatter fields
  - Agent identity files (SOUL.md)
  - Financial terms chuẩn (EBIT, EBITDA, D&A, CAGR, FCF)
  - Broker report quotes gốc
- [ ] Nếu phát hiện tiếng Anh trong nội dung → **sửa trước khi commit**

---

## Common Bugs Checklist (historical)

| Bug | Checklist check |
|-----|-----------------|
| Column shift | **§4: count pipes** — header số pipe = data số pipe |
| Duplicate frontmatter ở cuối file | **§8: verify** — grep `---` cuối file |
| Thiếu ticker tag | **§2: frontmatter** — check tags có ticker symbol ko |
| P/E sai format | **§3: template block** — format từ template hoặc entry gần nhất |
| Nội dung tiếng Anh thay vì Tiếng Việt có dấu | **§9: ngôn ngữ** — kiểm tra từng dòng human-facing text |
| Template sai cấu trúc | **§3: template block** — đọc HTML comment template TRƯỚC khi write |

---

## 10. EXTERNAL ACTION APPROVAL — 5-Point Checklist 🛑

> Áp dụng cho MỌI hành động chạm đến: quyết định đầu tư, giao dịch, publish thesis, ảnh hưởng portfolio.
> Không gồm: task nội bộ trong conversation (tính chỉ số, tra cứu BCTC, research).
> Checklist này là **gate protocol** — Hermes phải show 5 points trước khi act, CHỈ act sau Warren OK.

### Process

Trước mỗi external action, Hermes trình bày đủ 5 points:

| # | Point | Nội dung |
|---|-------|----------|
| 1 | **WHAT** 🎯 | Hành động cụ thể sắp làm — "Tôi sắp [action]" |
| 2 | **WHY** 🤔 | Lý do / data thesis / catalyst — "Vì [lý do]" |
| 3 | **EXACT CONTENT** 📝 | Nội dung chính xác: thesis text, entry/exit price, khối lượng, file path |
| 4 | **RISK** ⚠️ | What could go wrong + severity (HIGH/MOD/LOW) — thị trường, thanh khoản, opportunity cost |
| 5 | **APPROVAL** ✅ | Câu hỏi: "Anh OK cho tôi publish / đề xuất này ko?" |

### Quy tắc

- **Chưa show đủ 5 points → KHÔNG act**
- **Warren chưa nói OK → KHÔNG act**
- Nếu Warren nói "sửa [detail]" → Hermes sửa → show lại points 3 (content) + 5 (approval)
- Nếu Warren nói "ko" → dừng, ko hỏi lại
- Task trong Zone 🟢 (tự làm hoàn toàn) → không cần checklist này
- **🔴 Đặt lệnh LUÔN là zone 4 — Hermes ko bao giờ tự động trade, kể cả có 5-point checklist**

### Ví dụ

```
Hermes: 🛑 PRE-FLIGHT CHECK
1. WHAT: Publish thesis cho GAS — đề xuất entry
2. WHY: BCTC Q2/2026 vừa ra — OCF/NI divergence chỉ 8%, receivables ổn, P/E = 12.5 vs 5Y avg 14.2
3. EXACT CONTENT: personal_vault/investing/GAS_thesis.md — draft thesis + entry price 85k-90k
4. RISK: [MOD] — gas price phụ thuộc oil, thanh khoản thin ở vùng giá này
5. APPROVAL: Anh OK cho tôi publish thesis này ko?
```

> **Warren: OK** → Hermes publish.
> **Warren: sửa entry price** → Hermes sửa → show lại point 3 + 5.
> **Warren: ko** → Hermes dừng.
