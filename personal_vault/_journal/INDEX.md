---
name: JOURNAL_INDEX
type: index
status: active
domain: meta
last_updated: 2026-07-01
scope: personal_vault/_journal/
index_first_rule: Read this file before writing journal entries — naming convention + template
auto_update: Hermes must update this table whenever journal files are added/removed
---

# _journal — Index & Entry Conventions

> **Purpose:** Raw personal journal — Warren's unfiltered thoughts, reflection, daily notes.
> Không tự động route vào wiki hay pulse. Journal = private, wiki = curated.

---

## 🧭 How to Use

| Nếu muốn… | Thì viết vào… |
|-----------|---------------|
| Ghi nhanh suy nghĩ trong ngày | `YYYY-MM-DD.md` (1 file/ngày) |
| Note về 1 chủ đề cụ thể | `YYYY-MM-DD_slug.md` |
| Brain dump dài | append vào `YYYY-MM-DD.md` — newest on top |

## File Naming

```
YYYY-MM-DD.md              — daily journal entry
YYYY-MM-DD_slug.md         — topic-specific entry (e.g. 2026-07-01_reorg-thoughts.md)
```

## Entry Format (trong file)

```markdown
---
created: 2026-07-01
domain: meta
type: journal
---

# 2026-07-01

## Thoughts

...

## Decisions

...

## Random
...
```

## Rules

- **Append newest on top** trong mỗi file
- **Không rewrite/edit** entry cũ — chỉ append
- **Journal ≠ wiki** — content in journal is raw, unprocessed
- Khi 1 entry cần chuyển thành knowledge → Hermes propose `/ops-ingest` vào wiki

---

*Created: 2026-07-01 (vault reorg)*
