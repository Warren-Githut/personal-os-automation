---
name: "Personal Ontology"
type: "ontology"
status: "active"
version: "2026-07-11"
created: "2026-07-11"
last_updated: "2026-07-11"
applies_to: [personal_profile]
tags: [schema, guardrail, vault-structure, personal]
domain: "personal"
---

# PERSONAL_ONTOLOGY — Schema cho "não" Hermes (personal-profile)

> **Tại sao:** Bài ontology-constrained memory (akshay_pachaar, 2026-05) chốt: *schema phải viết ra mới thành guardrail, không để LLM auto-extract.* File này chuẩn hóa schema personal-domain của `personal_vault` (shared vault với stock-profile, nhưng personal-profile đọc file này).
>
> **Không auto-LLM extraction.** Memory human-gated qua `/compress-personal-memory` + approve.
>
> **Pair file:** `STOCK_ONTOLOGY.md` (stock-profile). Cả 2 cùng vault nhưng Hermes load theo profile context.

---

## 1. Nguyên tắc

- Bắt đầu ít, thêm dần. Thêm node type mới chỉ khi capture >20% domain logic chưa phủ.
- Source/Target constraint = guardrail.
- Folder mới = structure change = zone 🔴 (phải hỏi Warren + thêm vào §2).
- Mọi `type:` mới PHẢI có mặt ở §2B.

---

## 2. Node Types — Canonical `type:` Vocabulary (personal-domain)

> **Scan thực tế 2026-07-11** (personal_vault, personal-types): bảng dưới = vocabulary hợp lệ cho personal-profile. Mọi file `.md` personal-domain mới PHẢI dùng 1 `type:` này.

### §2A. Profile SSOT Node

| Node | `type:` | Vị trí | Định nghĩa | Edges |
|------|---------|--------|------------|-------|
| **Personal Memory** | `memory_reference` | `00_CORE_LOGIC/PERSONAL_MEMORY.md` | SSOT personal health/finance lessons | cites Context, cites Decision |

### §2B. Personal File-Class Nodes (vocabulary thực tế)

| `type:` | Count | Vị trí | Mô tả |
|---------|-------|--------|-------|
| `pulse` | 12 | `10_PULSE/` | Daily/weekly pulse log (health/sleep/market) |
| `tracking` | 9 | `10_PULSE/`, `_cases/` | Bảng theo dõi |
| `log` | 4 | `10_PULSE/`, `_journal/` | Log ghi chép |
| `context` | 2 | `00_CORE_LOGIC/` | Context file (PERSONAL_CONTEXT) |
| `journal` | 2 | `_journal/` | Nhật ký |
| `insurance_summary` | 1 | `legal/` hoặc `docs/` | Tóm tắt bảo hiểm |
| `guide` | 1 | `_inbox/` hoặc `docs/` | Hướng dẫn |
| `template` | 2 | `00_CORE_LOGIC/` | Template |
| `index` *(shared)* | 10 | `00_*_INDEX.md` | Registry / hub |
| `reference` *(shared)* | 11 | `30_KNOWLEDGE_BASE/wiki/` | Tài liệu tham chiếu |
| `analysis` *(shared)* | 6 | `30_KNOWLEDGE_BASE/wiki/` | Phân tích sâu |
| `dashboard` *(shared)* | 1 | `30_KNOWLEDGE_BASE/wiki/` | HTML viz |

> **Pulse rule:** `10_PULSE/` PHẢI dùng `pulse`/`tracking`/`log`. Health metrics map về `PERSONAL_CONTEXT.md`.

---

## 3. Edge Types (personal)

| Edge | Cơ chế | Source → Target | Constraint |
|------|--------|-----------------|------------|
| **wikilink** | `[[Node_Name]]` | bất kỳ → bất kỳ | Tên khớp exact filename. Sai = deadlink. |
| **SSOT-chain** | raw→script→md→wiki→dashboard | parent → child | Child reference ngược parent. |
| **index→file** | registry | Index → Node | Mọi Node mới PHẢI có row Index. |
| **pulse→context** | health tracking | pulse → PERSONAL_CONTEXT | Pulse data map về context metrics. |
| **memory→context** | citation | PERSONAL_MEMORY → Context | Lesson phải cite context nguồn. |

**Hard constraint:** KHÔNG tạo edge vô nghĩa (vd `pulse → dashboard` trừ khi viz thật) — trừ Warren duyệt.

---

## 4. Guardrails (zone 🔴)

- Folder mới ở root vault → hỏi trước + thêm node type §2B.
- `type:` mới chưa định nghĩa → hỏi trước.
- Xóa/đổi tên SSOT (`PERSONAL_MEMORY.md`/`PERSONAL_CONTEXT`/`PERSONAL_USER`) → repoint TẤT CẢ refs + update §2/§3.
- Tách case/file mới khi có case gốc → MERGE.

---

## 5. Reconciliation Protocol

| # | Trigger | Hành động |
|---|---------|-----------|
| 1 | Warren tạo/xóa/đổi tên file/folder (zone 🔴) | Tại bước đó update §2B/§3 + ghi §6 log. |
| 2 | **`/compress-personal-memory` chạy** | Bước thêm: scan `type:` + folder tree vs PERSONAL_ONTOLOGY.md → diff → propose → Warren OK → update + log. |
| 3 | Warren hỏi "ontology check" | Scan, report drift, update nếu OK. |

> Caveat: không có file-watcher. Drift thủ công bị bắt ở trigger 2/3.

---

## 6. 🔄 Reconciliation Log

| Date | Change | By |
|------|--------|-----|
| 2026-07-11 | Tạo PERSONAL_ONTOLOGY.md — personal-domain vocabulary (pulse/tracking/log/context/journal/insurance_summary/guide/template + shared index/reference/analysis/dashboard). Borrow ý ontology-constrained memory. Pair với STOCK_ONTOLOGY.md. | Hermes |
