---
name: "_personal_memory_raw"
type: "memory_raw"
status: "active"
domain: "personal"
created: "2026-07-01"
last_updated: "2026-07-09"
description: "Append-only raw lessons log cho personal_profile. Distill qua /compress-personal-memory → PERSONAL_MEMORY.md"
---

# Raw Memory Log — Personal Profile

> **Append-only.** Entry mới nhất ở trên.
> Chỉ ghi khi Warren nói "ghi".
> `/compress-personal-memory` sẽ distill file này → `00_CORE_LOGIC/PERSONAL_MEMORY.md`.

## 2026
- [Decisions] [2026-07-18] Bỏ mem0 FAISS hoàn toàn ở mọi profile (simplify stack) — "không dùng mem0 FAISS ở đâu cả". personal_profile Bố tự xóa (zone 🔴 — con KHÔNG đụng filesystem cross-profile). Từ nay vault (PERSONAL_MEMORY.md) là SSOT duy nhất → con KHÔNG ghi mem0 nữa, chỉ ghi _personal_memory_raw.md khi có lệnh "ghi/nhớ". Cần update SOUL.md §2.1 (xóa dòng mem0 FAISS) + §10 (Mem0 Gate) sau khi xóa xong.
- [Corrections] [2026-07-09] Anti-loop rule clarified: (a) built-in đầy → Hermes tự do prune stale + add mới (Warren KO ý kiến, native). ANTI-LOOP CHỈ khi nhầm store: KHÔNG loop xóa (a) để nhét (b) — (b) push qua Python script, không qua memory tool. (Em over-corrected rule cũ thành "dừng hẳn" → sai, sửa.)
