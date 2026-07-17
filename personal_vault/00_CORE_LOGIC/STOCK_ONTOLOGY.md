---
name: "Stock Ontology"
type: "ontology"
status: "active"
version: "2026-07-11"
created: "2026-07-11"
last_updated: "2026-07-11"
applies_to: [stock-profile]
tags: [schema, guardrail, vault-structure, stock]
domain: "stock"
---

# STOCK_ONTOLOGY — Schema cho "não" Hermes (stock-profile)

> **Tại sao:** Bài ontology-constrained memory (akshay_pachaar, 2026-05) chốt: *schema phải viết ra mới thành guardrail, không để LLM auto-extract (sẽ ra node generic).* File này chuẩn hóa schema stock-domain của `personal_vault` (shared vault với personal-profile, nhưng stock-profile đọc file này).
>
> **Không auto-LLM extraction.** Memory human-gated qua `/compress-stock-memory` + approve.
>
> **Pair file:** `PERSONAL_ONTOLOGY.md` (personal-profile). Cả 2 cùng vault nhưng Hermes load theo profile context.

---

## 1. Nguyên tắc

- Bắt đầu ít, thêm dần. Thêm node type mới chỉ khi capture >20% domain logic chưa phủ.
- Source/Target constraint = guardrail.
- Folder mới = structure change = zone 🔴 (phải hỏi Warren + thêm vào §2).
- Mọi `type:` mới PHẢI có mặt ở §2B.

---

## 2. Node Types — Canonical `type:` Vocabulary (stock-domain)

> **Scan thực tế 2026-07-11** (personal_vault, stock-types): bảng dưới = vocabulary hợp lệ cho stock-profile. Mọi file `.md` stock-domain mới PHẢI dùng 1 `type:` này.

### §2A. Profile SSOT Node

| Node | `type:` | Vị trí | Định nghĩa | Edges |
|------|---------|--------|------------|-------|
| **Stock Memory** | `memory_reference` | `00_CORE_LOGIC/STOCK_MEMORY.md` | SSOT stock lessons (P&L, valuation, watchlist) | cites Company, cites Decision |

### §2B. Stock File-Class Nodes (vocabulary thực tế)

| `type:` | Count | Vị trí | Mô tả |
|---------|-------|--------|-------|
| `thesis` | 17 | `030-Companies/{ticker}/` | Đầu tư luận (bull case) |
| `anti` | 13 | `030-Companies/{ticker}/` | Anti-thesis (bear case) |
| `catalyst` | 10 | `030-Companies/{ticker}/` | Catalyst watch |
| `bctc` | 10 | `030-Companies/{ticker}/` | Báo cáo tài chính |
| `T` | 9 | `030-Companies/{ticker}/` | Thesis note ngắn |
| `V` | 2 | `030-Companies/{ticker}/` | Valuation note |
| `decision_analysis` | 1 | `040_Deploy_Capital/` | Phân tích quyết định deploy vốn |
| `action_plan` | 1 | `_cases/` hoặc `docs/` | Kế hoạch hành động |
| `index` *(shared)* | 10 | `00_*_INDEX.md` | Registry / hub |
| `reference` *(shared)* | 11 | `30_KNOWLEDGE_BASE/wiki/` | Tài liệu tham chiếu |
| `analysis` *(shared)* | 6 | `30_KNOWLEDGE_BASE/wiki/` | Phân tích sâu |
| `dashboard` *(shared)* | 1 | `30_KNOWLEDGE_BASE/wiki/` | HTML viz |

> **Company folder rule:** `030-Companies/{ticker}/` PHẢI chứa đủ 6 stock-types (`thesis`/`anti`/`catalyst`/`bctc`/`T`/`V`). Thiếu = incomplete analysis.

---

## 3. Edge Types (stock)

| Edge | Cơ chế | Source → Target | Constraint |
|------|--------|-----------------|------------|
| **wikilink** | `[[Ticker]]` / `[[Node]]` | bất kỳ → bất kỳ | Tên khớp exact filename. Sai = deadlink. |
| **SSOT-chain** | raw→script→md→wiki→dashboard | parent → child | Child reference ngược parent. |
| **index→file** | registry | Index → Node | Mọi Node mới PHẢI có row Index. |
| **Company→{6 stock-types}** | analysis tree | `030-Companies/{ticker}/` → thesis/anti/catalyst/bctc/T/V | 1 ticker = 6 types. Thiếu = incomplete. |
| **memory→company** | citation | STOCK_MEMORY → Company | Lesson phải cite ticker. |

**Hard constraint:** KHÔNG tạo edge vô nghĩa (vd `thesis → dashboard`) — trừ Warren duyệt.

---

## 4. Guardrails (zone 🔴)

- Folder mới ở root vault → hỏi trước + thêm node type §2B.
- `type:` mới chưa định nghĩa → hỏi trước.
- Xóa/đổi tên SSOT (`STOCK_MEMORY.md`/`STOCK_CONTEXT`/`STOCK_USER`) → repoint TẤT CẢ refs + update §2/§3.
- Tách case/file mới khi có case gốc → MERGE.

---

## 5. Reconciliation Protocol

| # | Trigger | Hành động |
|---|---------|-----------|
| 1 | Warren tạo/xóa/đổi tên file/folder (zone 🔴) | Tại bước đó update §2B/§3 + ghi §6 log. |
| 2 | **`/compress-stock-memory` chạy** | Bước thêm: scan `type:` + folder tree vs STOCK_ONTOLOGY.md → diff → propose → Warren OK → update + log. |
| 3 | Warren hỏi "ontology check" | Scan, report drift, update nếu OK. |

> Caveat: không có file-watcher. Drift thủ công bị bắt ở trigger 2/3.

---

## 6. 🔄 Reconciliation Log

| Date | Change | By |
|------|--------|-----|
| 2026-07-11 | Tạo STOCK_ONTOLOGY.md — stock-domain vocabulary (6 company-types + decision_analysis/action_plan + shared index/reference/analysis/dashboard). Borrow ý ontology-constrained memory. Pair với PERSONAL_ONTOLOGY.md. | Hermes |
