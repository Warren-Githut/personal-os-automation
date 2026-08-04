---
name: improve-codebase-architecture
description: Lightweight audit cho parser/vault pipeline — tìm deepening opportunities (shallow→deep modules). Scope-before-scan (YAGNI), git-log hotspots, deletion-test. Steal từ mattpocock/skills. User-invoked.
disable-model-invocation: true
version: 1.0.0
trigger: Parser/vault pipeline phình, hoặc Bố bảo "review code", "audit parser", "tại sao skill này dài thế".
---

# Improve Codebase Architecture (Warren-light)

> Steal methodology từ `mattpocock/skills/improve-codebase-architecture` + `diagnosing-bugs`. Runtime-locked → chỉ lấy quy trình, viết lại cho vault parser pipeline. KHÔNG cần plugin/HTML report — output markdown.

## Mục đích
Biến **shallow modules** (interface gần phức tạp bằng implementation) thành **deep modules** (nhiều chức năng qua interface đơn giản). Tăng testability + AI-navigability của parser pipeline (`luso-parsers`, `vault-parser-hygiene`, dashboard scripts).

## Process
### 1. Scope before scan — YAGNI (HARD RULE)
Đừng quét toàn bộ. Quyết định **WHERE** trước:
- Bố chỉ tên module/pain point → lấy nó, skip inference.
- Không → `git log --oneline -30` tìm hotspots (file/area lặp lại) → tập trung đó. Nếu scattered → widen.

### 2. Explore (organic)
Đọc CONTEXT.md glossary + ADR khu vực. Dùng `search_files` walk pipeline. Note friction:
- Hiểu 1 concept phải bounce giữa nhiều module nhỏ?
- Module **shallow** (interface ≈ implementation)?
- Pure functions extracted chỉ để test, nhưng bug nằm ở cách gọi (no locality)?
- Coupled modules leak qua seam?
- Untested / khó test qua interface hiện tại?

### 3. Deletion test (với mọi candidate shallow)
Hỏi: "xóa nó có tập trung complexity hay chỉ dời chỗ?" → "yes, concentrates" = signal muốn.

### 4. Present candidates (markdown, KHÔNG HTML để fit free model)
Mỗi candidate = 1 card:
- **Files** — module liên quan
- **Problem** — tại sao friction
- **Solution** — plain English
- **Benefits** — locality + leverage, test cải thiện thế nào
- **Recommendation** — Strong / Worth exploring / Speculative

### 5. Grilling loop
Bố pick candidate → chạy `interview-me` (grilling) walk decision tree. Side-effects: update CONTEXT.md glossary, viết ADR nếu decision load-bearing.

## Cross-link
- **diagnosing-bugs**: root-cause methodology (reproduce → bisect → hypothesis → fix at seam) — dùng khi parser bể.
- **verify-parser-output**: independent-source anti-tautological check — dùng sau mỗi fix.

## Warren hard rules
- KHÔNG mutate `raw/` (ANCHORS). Audit chỉ read.
- Tiếng Việt có dấu cho human-facing.
- Backup script đổi vào `vault/_archives/skills/`.
