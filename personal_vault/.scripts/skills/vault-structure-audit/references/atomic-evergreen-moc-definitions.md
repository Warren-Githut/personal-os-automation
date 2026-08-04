---
type: reference
topic: atomic-evergreen-moc-definitions
version: 3.0.0
---

# Strict Definitions: Atomic / Evergreen / MOC

Đọc file này **trước khi audit** để calibration. Mọi check trong Phase 1B/1C/1D phải dùng definitions ở đây — không tự chế.

---

## 1. Atomic Note

**Định nghĩa:** Body < 1KB **HOẶC** chứa đúng 1 core idea (không pha trộn nhiều concept).

### Check criteria (OR logic — vi phạm 1 cái = vi phạm atomic)

1. **Size**: body content (không tính frontmatter) > 1KB → 🟡 borderline, > 5KB → 🔴 vi phạm
2. **Idea count**: note chứa > 1 concept độc lập (vd: vừa ghi meeting notes, vừa ghi task list, vừa ghi decision) → 🔴
3. **Refactor smell**: nếu cắt note làm 2-3 file mà mỗi file vẫn standalone → note vi phạm atomic

### ✅ Sample Atomic Note

```markdown
---
type: insight
created: 2026-06-15
updated: 2026-06-20
domain: trading
tags: [vietnam-market, valuation]
---

# P/E của VN-Index thấp hơn historial mean

VN-Index hiện P/E ~12, thấp hơn 5-year mean ~15. Lý do chính:
- Bank earnings inflated (P/E denominator high)
- Foreign net sell 2024-2025

→ Value trap risk cao. Đợi earnings confirmation.

## Links
- [[2026-06-10 VN-Index macro review]]
- [[Valuation methodology Vietnam stocks]]
```

**Tại sao atomic:** 1 idea duy nhất (P/E observation), < 1KB, standalone, có links ra context.

### ❌ Sample Non-Atomic Note

```markdown
---
type: mixed
---

# Daily dump 2026-06-20

## Meeting với sếp
... 500 từ ...

## Task list
- [ ] A
- [ ] B
... 20 tasks ...

## Random idea về trading
... 300 từ ...

## Health check
... 200 từ ...
```

**Vi phạm:** multi-concept, > 5KB, không standalone. → Split thành 4 notes.

---

## 2. Evergreen Note

**Định nghĩa:** Note đã refine ≥ 1 lần + được kết nối. Cụ thể, phải thỏa **TẤT CẢ** 4 điều kiện (AND logic):

1. **Frontmatter**: có `status` + `updated` (minimum)
2. **Inbound link**: ≥ 1 note khác link tới note này (có người "tham chiếu")
3. **Outbound link**: ≥ 1 link ra note khác (note này "tham chiếu" tới ai)
4. **Refined**: `last_updated - created > 30 ngày` (đã qua ít nhất 1 chu kỳ revise)

### Check severity

| Condition vi phạm | Severity | Lý do |
|-------------------|----------|-------|
| Thiếu frontmatter (status/updated) | 🟡 | AI không query được |
| 0 inbound link (orphan) | 🟡 | Entropy cao, retrieval cost tăng |
| 0 outbound link (dead-end) | 🟡 | Connection loss, insight generation cản |
| Chưa refined (created == updated) | 🟢 | Non-evergreen nhưng có thể promote |

### Lifecycle

```
Seed note (created, no links)
   ↓ +frontmatter +links +refine (30d+)
Evergreen note
   ↓ entropy / no maintenance
Stale note (last_updated > 180d, no recent inbound)
   ↓ archive
Archived
```

### ✅ Sample Evergreen Note

(same as Atomic sample above — thỏa cả 4 conditions)

### ❌ Sample Non-Evergreen Note

```markdown
# Quick note about something

Just thought about this. Will expand later.
```

**Vi phạm:** thiếu frontmatter, 0 links, chưa refined. → Seed note, chưa evergreen.

---

## 3. MOC (Map of Content)

**Định nghĩa:** Note có chức năng **chính là điều hướng**. Phải thỏa **TẤT CẢ**:

1. **Tên match**: `*MOC*` / `*Map*` / `*Index*` (case-insensitive) trong filename hoặc H1
2. **Content chính là links**: ≥ 50% body (sau frontmatter, tính bằng characters hoặc lines) là `[[wikilinks]]` hoặc links tới notes khác
3. **Không phải content note**: MOC không chứa argument/analysis chính — chỉ structure + brief annotation per link

### Check criteria

| Check | Severity | Fix |
|-------|----------|-----|
| Tên không match `*MOC*/*Map*/*Index*` | 🟡 | Rename hoặc reclassify |
| < 50% body là links (MOC but content-heavy) | 🟡 | Split: 1 MOC + 1 content note |
| MOC stale: > 20% links chết (target không tồn tại) | 🔴 | Refresh từ ground truth |
| MOC orphan: 0 inbound | 🟡 | Link MOC từ README/area root |
| MOC over-hub: > 50 outbound links | 🟡 | Split thành sub-MOCs |

### ✅ Sample MOC

```markdown
---
type: moc
created: 2026-06-01
updated: 2026-06-20
domain: trading
---

# Trading MOC

Central navigation for trading knowledge.

## Core concepts
- [[P/E observation VN-Index 2026-06]]
- [[Valuation methodology Vietnam stocks]]
- [[Foreign net sell impact 2024-2025]]

## Active positions
- [[TCB position thesis]]
- [[FPT position thesis]]

## Watchlist
- [[MWG analysis]]
- [[VHM analysis]]

## Reviews
- [[2026-06-10 VN-Index macro review]]
- [[2026-05 monthly trading review]]
```

**Tại sao là MOC:** tên match, > 80% body là links, không có argument chính, chỉ điều hướng + brief group headers.

### ❌ Sample Fake MOC

```markdown
# Trading MOC

Trong 2026, thị trường Việt Nam đối mặt nhiều thách thức. P/E thấp
nhưng value trap risk cao. Bank earnings inflated, foreign net sell
tiếp tục. Mình nghĩ nên giữ cash-heavy portfolio cho đến Q3... [1000 từ analysis]

## Some links
- [[TCB]]
- [[FPT]]
```

**Vi phạm:** < 50% body là links. → Đây là content note, không phải MOC. → Split: rename thành analysis note + tạo MOC thật.

---

## Audit checklist (dùng trong Phase 1D)

```
For each note in vault:
  □ Atomic check: body < 1KB OR 1 idea?
    - Nếu vi phạm → flag 🟡/🔴, recommend split
  □ Evergreen check: 4 conditions all true?
    - Nếu thiếu condition → flag + recommend promote
  □ If matches *MOC*/*Map*/*Index* → MOC check:
    - ≥ 50% body links? stale links? orphan? over-hub?
    - Nếu vi phạm → flag + recommend reshape

For each top-level area:
  □ Có ≥ 1 MOC?
    - Nếu thiếu → recommend create MOC (3H)
```

---

## Why strict definitions matter

Loose definitions → audit subjective → advice useless → entropy tăng.

Strict definitions → check mechanical → advice concrete → entropy giảm.

**Vault Architect principle #3 (Signal-to-Noise):** definition chính nó phải SNR cao. File này ~3KB, 3 definitions, 6 samples, 1 checklist. Không filler.
