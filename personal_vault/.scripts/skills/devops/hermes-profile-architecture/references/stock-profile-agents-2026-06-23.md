# stock-profile AGENTS.md — 2026-06-23

Designed via `interview-me` methodology (see SKILL.md → Profile-Level AGENTS.md Pattern).

## Process

| Phase | Decision |
|-------|----------|
| Vault paths | Plain path list, not ASCII tree. Root + allowed subfolders only |
| Runtime notes | OS (Windows git-bash), working dir (stock_vault/), default BCTC source (TCBS, cross-check) |
| OCR priority | liteparse first for ALL PDFs, fallback to other tools |
| Boundaries | Explicit list of DO NOT write folders (ideas/, cases/, tasks/, Daily_Pulse.md) — prevents personal-vault pollution |
| Frontmatter | YAML frontmatter for consistency with HORION: name/description/role/language/end_warren_questions_with/source_of_truth/cite_numbers/changes_effective/profile_type |
| Profile files index | Quick reference for agent: what each layer (SOUL/MEMORY/USER) contains |
| Language | English (consistent with all other layers) |

## Key Design Decisions

- **Profile-level AGENTS.md coexists with vault AGENTS.md** — they are independent. Profile AGENTS.md (`~/.hermes/profiles/stock-profile/AGENTS.md`) is loaded by the profile; vault AGENTS.md (`stock_vault/AGENTS.md`) is loaded from working directory. Both appear in context. No override.
- **YAML frontmatter is useful** even though SOUL.md already covers identity — it gives tools and search engines a structured handle on the file.
- **Boundaries section** is critical — without it, the agent may write to personal folders (health, family, tasks) thinking they're in scope.
- **Profile files index** saves the agent from having to open all 3 other files to understand the layer separation.
- **OCR priority belongs in AGENTS.md, not MEMORY.md** — it's a project-wide technical convention (how to process PDFs), not an environment fact.

## Pitfalls

- **Do NOT repeat SOUL.md rules in AGENTS.md** — causes drift when SOUL is updated but AGENTS is not. If you need a pointer, use a simple cross-reference: "Stock criteria in SOUL.md; pulse format rules in MEMORY.md."
- **Do NOT list individual file paths** — folder-level is sufficient. Agent self-discovers files via search.
- **Do NOT put tool commands here** — they belong in MEMORY.md (always in context). AGENTS.md is for project architecture, not workflow reference.

## Final AGENTS.md

Written to `~/.hermes/profiles/stock-profile/AGENTS.md`. Full content:

```yaml
---
name: stock-profile
description: "stock-profile — Long-term VN equities analyst (Buffett-Munger style)."
role: stock-analyst
language: en
end_warren_questions_with: recommended_answer
source_of_truth: vault
cite_numbers: true
changes_effective: new-session-or-reset
profile_type: per-project
---
```

```markdown
# stock-profile — VN Equities Context

## Vault access
personal_vault root: `C:/Users/khoans/Documents/Stock_OS/stock_vault`

Read/write allowed:
- `10_PULSE/020_VNStock_Weekly_Outlook`
- `10_PULSE/021_VNStock_Macro`
- `10_PULSE/022_VNStock_Daily_Outlook`
- `10_PULSE/023_VNStock_Sector`
- `10_PULSE/024` through `029` (future files)
- `30_KNOWLEDGE_BASE/wiki/investing`
- `00_CORE_LOGIC`

All other vault folders are read-only unless explicitly asked.

## Boundaries (DO NOT)
- Do not write to: _ideas/, _cases/, _tasks/, TODO_Kanban.md, 10_PULSE/Daily_Pulse.md
- Do not create new files outside the listed pulse folders
- Do not modify CONTEXT.md (00_CORE_LOGIC/) without asking

## Runtime notes
- OS: Windows (git-bash terminal, POSIX shell syntax)
- Working directory: `stock_vault/`
- Default BCTC source: TCBS. Cross-check with VPS, HSC, Vietcap, SSI.

## PDF / OCR priority
For all PDFs and scans:
1. **liteparse** (preferred — use `pdf-parse` skill)
2. Fallback to other tools if liteparse fails or returns unusable output

## Profile files
- SOUL.md = identity, personality, integrity gate, portfolio dashboard
- MEMORY.md = vault paths, pulse conventions, tool commands, YAML schema
- USER.md = Warren profile (name, philosophy, broker, preferences)
```

## Source citation format
See SOUL.md → Data quality tags section. Summary:
- [HIGH] = audited BCTC / user-provided doc
- [MOD] = unverified report / web search
- [LOW] = training knowledge / estimate