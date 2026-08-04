---
name: compress-memory
description: "Memory distillation — archive MEMORY.md, read raw log, consolidate lessons, propose edits, reconcile ontology. Paths from SOUL.md §Quick Reference. Manual trigger by Warren."
version: 2.0.0
author: Hermes
category: core
tags: ['memory', 'distillation', 'compress']
related_skills: ['session-start']
---

# /compress-memory — Memory Distillation Protocol (Profile-Agnostic)

> **Purpose:** Bridge between raw lesson log and the reference MEMORY.md file.
> **Paths:** All file paths are defined in SOUL.md §Quick Reference (`MEMORY_PATH`, `VAULT_ROOT`, etc.).
> Warren runs this manually. Hermes does NOT auto-run it.

---

## Memory file map

Paths from SOUL.md §Quick Reference. Replace placeholders below:

| Key | Path (from §Quick Reference) | Role | Write policy |
|-----|-----|------|--------------|
| `MEMORY_PATH` | See SOUL.md | **Reference** — read each session | ONLY written after `/compress-memory` + approve |
| `RAW_MEMORY_PATH` | `{VAULT_ROOT}/_inbox/{profile}_memory_raw.md` | **Raw log** — append-only entries | Append when approved |
| `USER_PATH` | See SOUL.md `memories/USER.md` | **Profile** | Propose → approve → write |
| `ARCHIVE_DIR` | `{VAULT_ROOT}/_archives/memory/` | **Backup** — old MEMORY before compress | Auto during step 1 |

SSOT: `MEMORY_PATH` is read directly each session — no external sync copy.

---

## Write governance (hard rule)

Hermes does **NOT** auto-write MEMORY.md or USER.md. Every proposed write passes 2 gates:

| # | Gate | If NO → |
|---|------|---------|
| 1 | Will this still be true & useful in 7 days? | SKIP |
| 2 | Durable fact (preference/decision/config/lesson) or task artifact? | If artifact → SKIP |

WRITE only when:
1. **Direct command** — "lưu", "nhớ giùm", "ghi vào memory" → execute immediately.
2. **Proposal on Git Commit** — propose lessons → approve → append to `{VAULT_ROOT}/_inbox/{profile}_memory_raw.md`.
3. **USER.md update** — new preference detected → propose → approve → write.
4. **`/compress-memory`** — distills raw → proposes MEMORY.md edits → approve → WRITE.

### USER.md upkeep (event-triggered, NOT weekly cron)
- **SSOT:** vault USER.md (canonical). Mirror at profile's `memories/USER.md` for built-in layer.
- **Khi update:** chỉ khi có preference/identity MỚI (sự kiện, không lịch).
- **Tại `/compress-memory`:** step 3 PHẢI scan raw/new prefs cho profile-level changes → nếu có, propose USER.md update.
- **Không** đặt cron update — nội dung ít biến động.

### Built-in memory & skill consent gate
- **Built-in `memory` tool = propose-only.** Hermes KHÔNG auto-write. Flow: phát hiện durable fact → ADVISE → Bố duyệt → mới ghi.
- **`/compress-memory` output → vault ONLY.** Chỉ ghi MEMORY.md (SSOT). KHÔNG sync/ghi đè built-in `MEMORY.md`.
- **Skills:** vẫn do Bố duyệt (Skill Archive Gate).
- Hermes never self-approves.

### Vault file style (Warren conventions)
- **Concise + bullets:** max 3–5 bullets per topic, no long prose. Chat style = vault style.
- **Tech-hide 🚨:** Warren is non-IT. JSON / Python / code / config / schema in vault .md MUST be hidden by default (HTML comment `<!-- -->` or non-rendered block).

---

## Raw log format (`{profile}_memory_raw.md`)

Single file, **prepend** newest entry at top:

```
## 2026-06-28
- [Preferences] Warren muốn conclusion-first
- [Corrections] Lần X: suggest sai Y → học được Z

## 2026-06-27
- [Patterns] Warren hay quên check X → Hermes chủ động
- [Lessons Learned] CR >30% khi upsell → cần auto-calc
```

- Section tags: `[Preferences]` / `[Corrections]` / `[Patterns]` / `[Lessons Learned]`
- Each entry 1–2 lines, **Tiếng Việt (có dấu)**
- Prepend newest on top; never overwrite/edit old entries

---

## Proposal on Git Commit

When Warren git commits, Hermes checks for new lessons:
- What worked? → propose **Patterns** or **Lessons Learned**
- What failed? → propose **Corrections** or **Lessons Learned**
- New Warren preference? → propose **Preferences** (to raw) or **USER.md**

---

## Protocol (9 steps)

1. **Archive** → copy MEMORY.md → `{ARCHIVE_DIR}/MEMORY_YYYY-MM-DD.md`
2. **Read** → read raw log + current MEMORY.md
3. **Consolidate** → merge raw lessons into rules, dedup, sharpen. Goal: fewer, better rules.
4. **Stale-Scan** → sau Consolidate, quét MEMORY.md từng entry: entry nào không có reference thực tế (search_files vault) VÀ `last_updated` >30 ngày → đưa vào mục **"🔶 STALE"** trong Propose. Chỉ flag, KHÔNG tự xóa.
5. **Propose** → show Warren the draft (gồm STALE nếu có)
6. **Apply** → Warren OK → overwrite MEMORY.md (path từ §Quick Reference `MEMORY_PATH`)
7. **Clean raw** → clear raw log (or archive to `_archives/memory/raw/`)
8. **Ontology reconcile** → scan vault `type:` frontmatter vs ontology → diff → propose updates
9. **Sync** → MEMORY.md is read directly by Hermes each session. No external sync copy.
10. **Report** — summary of X entries → Y rules, ontology reconciled, MEMORY.md updated.

---

## Boundaries

| Always | Ask First | Never |
|--------|-----------|-------|
| Archive + propose + show diff | Overwrite MEMORY.md | Auto-apply without Warren OK |
| Conclusion-first report | Delete old archive | Modify production data |
| Cite source of each rule | | |
| Flag stale entries (step 4) | | Auto-delete stale WITHOUT Warren OK |
