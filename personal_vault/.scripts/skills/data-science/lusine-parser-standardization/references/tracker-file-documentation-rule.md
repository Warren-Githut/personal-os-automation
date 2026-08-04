# Tracker File Documentation Rule (Warren Preference)

> Added 2026-07-03 — from Menu GP% Monthly Tracker creation session.

## Rule

Khi Hermes tạo một tracker file MỚI (file rolling dạng `14_Menu_GP_Monthly_Tracker.md`), phải include đầy đủ documentation trong file để Warren mở ra đọc được mà ko cần Hermes context.

## Checklist — Những gì phải có trong file tracker (sau frontmatter)

1. **Mục đích** — 1-2 dòng: file này dùng để làm gì
2. **Data flow** — step-by-step từ raw data → output
3. **Data Sources table** — từng cột = cần gì | lấy từ đâu | cách lấy
4. **Cách chạy** — trigger command + steps (nếu manual) hoặc cron schedule
5. **Calendar reminder** — event link + schedule (nếu có)
6. **Filter scope** — items nào được track, items nào exclude
7. **Template block** (`<!-- ... -->`) — định nghĩa format từng section

## Example structure

```markdown
---
name: "Menu GP% Monthly Tracker"
...frontmatter...
---

<!-- TEMPLATE BLOCK — 6 sections ... -->

# Menu GP% Monthly Tracker

> Mục đích: ...
> 
> Data flow:
> 1. Star Horse → ...
> 2. Recipe_Index → ...

## Setup & Operations

### Data Sources (table)
### Cách chạy (steps)
### Google Calendar (schedule)
### Filter Scope

---

<!-- NEWEST ON TOP -->
```

## Rationale

- Warren mở file trực tiếp từ vault (ko qua Hermes) — cần tự hiểu file
- Documentation trong file = single source of truth, ko phải nhớ context từ conversation
- Template block + Setup section = self-documenting tracker
