# L'Usine Case Management Workflow — Personal Vault Adaptation

**Version:** 1.0-personal | **Last Updated:** 2026-06-19 | **Owner:** Hermes (Autonomous Operator)

---

## 1. System Overview

### Purpose
End-to-end case management for personal operations. Handles personal initiatives, tasks, and decisions through structured cases with full audit trail.

### Architecture
```
┌─────────────────────────────────────────────────────────────────┐
│                    INPUT CHANNELS                               │
├─────────────────────────────────────────────────────────────────┤
│  Telegram Bot     │  Slack #brain-dump     │  Obsidian Vault   │
│  (Warren direct)  │  (team dump)           │  (structured)     │
└──────────┬────────┴──────────┬──────────────┴────────┬─────────┘
           │                   │                       │
           ▼                   ▼                       ▼
┌─────────────────────────────────────────────────────────────────┐
│              NATURAL LANGUAGE PROCESSOR                         │
│  scripts/case_brain_nl_parser.py  +  case_brain_nl_handler.py  │
│  • Prefix detection: [new/update/edit/close case]              │
│  • Fuzzy matching (token overlap on slug + title)              │
│  • Section classification (Vấn đề/Bối cảnh/Giải pháp/Thành công)│
└─────────────────────────────────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────────────────────────────┐
│                    CASE STORAGE                                 │
├─────────────────────────────────────────────────────────────────┤
│  _cases/active/      │  _cases/closed/      │  00_00_CASES_INDEX.md        │
│  YYYY-MM-DD_slug.md  │  (moved on close)    │  YAML frontmatter      │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. Case File Format

### Frontmatter (YAML, required)
```yaml
---
status: OPEN|CLOSED
domain: family_gg|health|finance|legal|relationship|career
opened: YYYY-MM-DD
updated: YYYY-MM-DD
priority: HIGH|MEDIUM|LOW
follow_up: YYYY-MM-DD
followup_event_id: ""|<google_calendar_event_id>
stakeholders: [Warren, ...]
title: "Human-readable title"
tags: [ops, revenue, ...]
slug: "YYYY-MM-DD_kebab-case-short-title"
---
```

### Body Structure (Markdown, 4 standard sections)
```markdown
# Title (from frontmatter)

## Vấn đề
[Problem description — what issue triggered this case]

## Bối cảnh
[Context — background, constraints, current state, related data]

## Giải pháp đề xuất
[Proposed options with tradeoffs, recommended reply for Warren]

## Thành công
- [Bullet 1: Measurable success criterion]
- [Bullet 2: Measurable success criterion]
- [Bullet 3: Measurable success criterion]

--- (thread entries appended here, newest on top)

### YYYY-MM-DD HH:MM — Warren
[Update content in natural language]

### YYYY-MM-DD HH:MM — Warren
[Previous update...]

## Close Review (added on close)
- Closed: YYYY-MM-DD
- Lesson learned: (auto)
- Insight: (auto)
- Success target: [First bullet from ## Thành công]
```

---

## 3. Natural Language Commands (Telegram/Obsidian)

### Prefix Syntax
| Command | Format | Behavior |
|---------|--------|----------|
| **New** | `[new case] <free text>` | Creates case in `_cases/active/`, auto-generates slug |
| **Update** | `[update case <fuzzy_name>] <payload>` | Appends dated thread entry (newest on top) |
| **Edit** | `[edit case <fuzzy_name>] <instruction>` | In-place frontmatter/body modification |
| **Close** | `[close case <fuzzy_name>]` | Moves to `closed/`, adds Close Review |

### Fuzzy Matching Rules
- Tokenizes query (lowercase, remove diacritics, strip `YYYY-MM-DD_` prefix)
- Scores against slug tokens + title tokens
- Threshold: ≥0.35 overlap score
- Prefix match: `GG access` → `legal_divorce_court_GG_access`

### Examples
```
[new case] Nhà cung cấp cá hồi Norway - chuyển đối tác

[update case GG access] đã liên hệ luật sư, chuẩn bị chứng từ

[edit case legal divorce] priority HIGH

[close case legal divorce]
```

---

## 4. Hermes Operating Protocol (Personal Vault)

### Before Any Case Operation
1. **Read this file** (`_cases/README.md`)
2. **Read `_cases/frontmatter_template.md`** for required YAML fields
3. **Read `_cases/00_00_CASES_INDEX.md`** (unified index — SEARCH THIS FIRST)
4. **Read target case file** for full context

### Search Optimization ⚡
- **Always search `_cases/00_00_CASES_INDEX.md` first** when looking for a case — it lists every active + closed case with slug, status, priority, domain in one file.
- Do NOT `grep -r` the entire `_cases/` directory first. 00_00_CASES_INDEX.md is the index of record.
- Only fall back to direct case file search when the index entry does not contain enough detail (e.g., need body text).

### Creating New Cases
- Always use `YYYY-MM-DD_` prefix for slug
- Default: `domain=legal`, `priority=medium`, `follow_up=tomorrow`
- **REQUIRED:** frontmatter must match schema in `_cases/frontmatter_template.md`
- Run index sync after creation

### Updating Cases
- `update` = append thread (history preserved, newest on top)
- `edit` = in-place modification (no history)
- Both append dated entries

### Closing Cases
- Requires `## Thành công` section with measurable criteria
- Auto-generates Close Review comparing actual vs targets
- Moves file to `_cases/closed/`, clears `followup_event_id`

---

## 5. Directory Structure

```
_cases/
├── README.md                      # ← THIS FILE (Hermes reads first)
├── frontmatter_template.md        # Required YAML fields for new cases
├── 00_00_CASES_INDEX.md                 # Unified index: all cases (active + closed)
├── active/
│   ├── legal_divorce_court_GG_access.md
│   └── ... (more active cases)
└── closed/
    └── 2026-06/
        └── ... (closed case archives)
```

---

## 6. Change Log

| Date | Version | Changes |
|------|---------|---------|
| 2026-06-19 | 1.0-personal | Initial: adopted from work vault, adapted for personal schema |
| 2026-06-19 | 1.1-personal | Unified 00_00_CASES_INDEX.md (replaced ACTIVE + CLOSED separate indexes); added Search Optimization section |

---

**End of Document** — Hermes MUST read this before any personal case operation.
