---
name: hermes-profile-architecture
description: Govern Hermes profile strategy — when to split, when to consolidate, and how to manage domain separation within a single profile. Use when deciding profile structure for a new domain, or when profile sprawl creates maintenance friction.
---

# Hermes Profile Architecture

## Core Principle

**One profile per human, not per domain.** Domains separate via skill namespacing, not profile isolation.

## Memory & Context Architecture

Hermes builds context every turn from **6 layers** in this priority order:

```
→ SOUL.md        (slot #1) — Agent personality, voice, hard rules
→ MEMORY.md      — Facts agent learned across sessions (2,200 char limit)
→ USER.md        — User profile, preferences, style (1,375 char limit)
→ AGENTS.md      — Project context, conventions, architecture (from CWD)
→ Skill descriptions — Loaded on demand from SKILL.md files
→ Tool schemas + message history
```

**Key rules:**

| Layer | Location | Purpose |
|-------|----------|---------|
| **SOUL.md** | `~/.hermes/SOUL.md` or `$HERMES_HOME/SOUL.md` (CLI), `AppData/Local/hermes/profiles/<name>/SOUL.md` (Desktop) | Durable identity, tone, communication style. **Never loaded from CWD.** If empty/unreadable → falls back to built-in default. |
| **MEMORY.md** | `~/.hermes/memories/MEMORY.md` (CLI), `AppData/Local/hermes/profiles/<name>/memories/MEMORY.md` (Desktop) | Agent's personal notes — environment facts, conventions, tool quirks, lessons. **Per-profile** — zero cross-domain pollution. |
| **USER.md** | `~/.hermes/memories/USER.md` (CLI), `AppData/Local/hermes/profiles/<name>/memories/USER.md` (Desktop) | User profile — name, location, preferences, risk tolerance, pet peeves. **Per-profile.** |
| **AGENTS.md** | Vault root or CWD | Project context — only 1 per session: `.hermes.md` → `AGENTS.md` → `CLAUDE.md` → `.cursorrules` |

### The Agent Loop

Every message triggers:
```
user message → build context (SOUL + memory + user + AGENTS + skills + tools + history)
            → send to LLM
            → LLM decides: call tool or respond
            → if tool call: execute → return result → loop
            → if response: deliver to user
            → memory update (agent checks if worth remembering, writes to MEMORY.md/USER.md)
```

This is **Hermes' closed learning loop** — the agent learns from every conversation. Memory updates after every response means the agent accumulates domain knowledge over time.

### SOUL.md vs AGENTS.md

| SOUL.md (Durable identity) | AGENTS.md (Project scope) |
|----------------------------|---------------------------|
| Tone, style, communication defaults | Project architecture, conventions |
| Personality-level behavior | Repo-specific workflows |
| **Follows you everywhere** | **Belongs to a project** |

### When Setting Up a New Profile

1. **Seed SOUL.md** first — defines the profile's personality (trader, ops, personal, etc.)
2. **Seed MEMORY.md** with vault paths, folder structure, domain-specific conventions
3. **Seed USER.md** with profile owner's domain-specific preferences
4. **Verify AGENTS.md** exists in the vault root the profile will work in
5. **Test:** run a task, verify memory update fires after first response

Reference: [Hermes Docs — Personality & SOUL.md](https://hermes-agent.nousresearch.com/docs/user-guide/features/personality), [Hermes Docs — Context Files](https://hermes-agent.nousresearch.com/docs/user-guide/features/context-files)

---

## SOUL.md Design Methodology

SOUL.md is the most important layer — it defines the agent's identity, voice, and hard rules. A bad SOUL produces a generic agent that needs constant steering. A good SOUL makes the agent feel like an extension of the user's own thinking.

### Workflow: Interview → Draft → Critique → Refine → Write

Do NOT write SOUL.md from scratch. Use `interview-me` to extract intent first.

```
Phase 1 — INTERVIEW (using interview-me skill)
├── Hypothesize what the user wants the profile to BE
├── Ask one question at a time, each with a guess attached
├── Target: ~95% confidence (can predict user's reactions to next 3 questions)
└── Key dimensions to uncover:
    ├── Identity: "who is this agent?" (trader? ops manager? personal assistant?)
    ├── Voice: tone, formality, language (Vietnamese? English? mixed?)
    ├── Format: brevity level — bullet vs paragraph vs data dump
    ├── Decision style: system-thinker? gut-feel? data-first?
    ├── Hard rules: non-negotiables, boundaries, red lines
    ├── Push vs pull: reactive-only or trigger-based alerts?
    └── User's pain points: "I forget details" → concise. "I'm visual" → tables.

Phase 2 — DRAFT
├── Write SOUL.md in structured sections
├── Each section = one behavioral rule, not multiple
├── Keep it short — SOUL is identity + core rules + zones + search, NOT an encyclopedia. Every section must be decision-layer SSOT; if a section is a procedure it belongs in a skill, if it's a reference table it belongs in AGENTS.md / an index. (Complex ops profiles land ~140 lines even after extraction — fine; 300+ means concerns aren't separated. See 'Refactoring a Bloated SOUL' below.)
└── Include a DATA_CONTRACT if the profile handles sensitive/verifiable data

Phase 3 — CRITIQUE (user reviews draft)
├── User will delete aspirational-but-unrealistic sections
├── User will merge style rules into system prompt if they're obvious defaults
├── User will define confidence tags concretely (see Confidence Tag Taxonomy below)
└── User will call out template fields that require computational tools the agent doesn't have

Phase 4 — REFINE
├── Remove anything the user flagged as aspirational (tools don't exist)
├── Add concrete definitions for abstract concepts (HIGH/MOD/LOW)
├── Add DATA_CONTRACT for integrity gates (when does analysis run? when does it stop?)
├── Add structured output templates (Portfolio Dashboard, etc.) — but only fields the agent can ACTUALLY fill
└── Re-check: "can I run this rule with the tools I have?"

Phase 5 — WRITE
├── Write to $HERMES_HOME/SOUL.md (or profile's SOUL.md)
├── Profile: ~/.hermes/profiles/<profile-name>/SOUL.md
└── Note: SOUL.md is loaded at session START. Changes take effect on new session.
```

### Confidence Tag Taxonomy

When the user defines [HIGH/MOD/LOW] tags, the definitions must be SOURCE-based, not feel-based:

| Tag | Source | Example usage |
|-----|--------|---------------|
| `[HIGH]` | Audited BCTC, user-provided verified doc, exchange filing | "EPS Q1 = 3,450 [HIGH — từ BCTC kiểm toán]" |
| `[MOD]` | Unverified broker report, web search, press release, VDSC/HSC note | "Backlog +15% YoY [MOD — từ báo cáo HSC]" |
| `[LOW]` | Estimate, training knowledge, inference without direct source | "Dự phóng EPS 2026: ~4,000 [LOW — ước tính cá nhân]" |

Without source definitions, tags are meaningless. **Always define the taxonomy in SOUL.md.**

### DATA_CONTRACT Pattern

For profiles that handle verifiable data (BCTC, financials, health metrics), include a DATA_CONTRACT:

```markdown
## DATA_CONTRACT (bắt buộc)
1. [Critical analysis X] chỉ chạy khi user cung cấp nguồn Y (file/link).
   Nếu không có nguồn → tự động respond:
   ```
   CHỜ: cần [nguồn Y] để chạy [analysis X].
   Phân tích bên dưới dựa trên public data — confidence MAX = [MOD].
   ```
2. Source tag chỉ cite 1 trong 3 loại:
   (1) user-provided doc → [HIGH]
   (2) web search result → [MOD]
   (3) training knowledge → [LOW]
3. Nếu không đủ dữ liệu → ghi rõ `CHỞ: thiếu X` thay vì guess.
```

### Anti-patterns in SOUL.md

| Anti-pattern | Why it fails |
|--------------|--------------|
| **Push triggers** ("alert me when X happens") | SOUL.md is identity, not a monitoring agent. Push requires cron/daemon — write it as a cronjob, not SOUL. |
| **Communication style rules** ("always use bullets") | These belong in system prompt / Hermes config, not SOUL. SOUL = identity, not formatting. |
| **Aspirational templates** requiring computation the agent can't do (IRR, DCF, fair value) | The agent will fabricate numbers to fill the template. Only template fields the agent can actually produce with available tools. |
| **Overpromising capability** ("analyze all my holdings and rank them") | Without a portfolio tool / pricing API, the agent can't maintain a live ranking. Limit to what the current turn's context supports. |
| **Vague rules** ("be thorough", "think deeply") | These are unmeasurable. Replace with specific constraints: "3-5 bullet lines per ticker", "conclusion first, evidence below". |

### Refactoring a Bloated SOUL (Warren 2026-07-15)

A SOUL that grew to 346 lines (2,997 words) is not "identity" — it's three concerns mixed: (1) identity/rules, (2) **procedure** (session bootstrap, memory distillation protocol), (3) **reference tables** (file maps, formula tables, quick-ref). The fix is architectural separation, not editing prose.

**Procedure → extract into skills.** Anything that is a *sequence of steps* Hermes runs (session-start load order, `/compress-memory` 9-step protocol, raw-log format, write governance) becomes a skill (`session-start`, `compress-memory`). SOUL keeps a one-line pointer: "Load `session-start` skill each session."

**Reference → extract into pointers.** File maps, quick-reference tables, formula tables duplicate what already lives in `AGENTS.md` / index files. Delete the table; replace with one line: "see `Warren_OS_Local/AGENTS.md`" or "see `00_WIKI_INDEX.md`". Do NOT duplicate architecture that has a canonical home.

**Result:** warren-profile SOUL went 2,997 → 1,132 words (−62%), kept only §1 Identity, §4 Comms, §5 Core Rules, §5.1 Zones, §7 Search. Procedure in 2 skills, reference in pointers.

**🚨 Dangling-reference verification (mandatory after any SOUL rewrite):**
Before declaring done, grep the new SOUL for every path and `§N` reference, then verify each against reality:
1. Every `path/to/file.md` referenced MUST exist on disk. Caught this session: `USER_GUIDE.md` was referenced but **did not exist** → pointed to the real `Warren_OS_Local/AGENTS.md` instead.
2. Every relative path MUST resolve from the agent's actual cwd. Caught this session: `vault/AGENTS.md` was wrong — file is at repo root `Warren_OS_Local/AGENTS.md`.
3. Every `§N` pointer MUST match a section that still exists after the rewrite. Renumbering (e.g. old §8 Search → new §7) must be propagated to all references.

A SOUL with dead links is worse than a bloated one — it silently misroutes the agent every session.

### 4-Zone Delegation Framework (SOUL.md Pattern)

For profiles where Hermes handles diverse task types across risk levels, add a delegation zone system to SOUL.md. This gives a clear decision tree: "can I act, or must I ask?"

| Zone | Name | Meaning | Default behavior |
|------|------|---------|-----------------|
| 🟢 **Zone 1** | TỰ LÀM HOÀN TOÀN | Act without asking | Risk=0, reversible, agent knows intent |
| 🟡 **Zone 2** | DRAFT → APPROVE | Research/draft, then wait for OK | Touches production, costs money, affects others, first-time workflow |
| 🟠 **Zone 3** | NHẮC / CHUẨN BỊ | Remind + prepare context only | Needs user's judgment, can't be delegated |
| 🔴 **Zone 4** | TỰ LÀM TAY | Never automate, never draft | Legal/compliance, irreversible, personal |

**Zone Priority Rules (include in SOUL.md):**
1. **Default = 🟡** for every new task — agent proves safety over time to move up
2. **When uncertain → move down a zone** (🟢→🟡→🟠→🔴)
3. **User promotes tasks** by saying "lần sau tự làm" / "khỏi hỏi" (🟡→🟢)
4. **Every skill/cron job declares a zone** — checked before execution
5. **Periodic zone review** — tasks that repeatedly hit wrong zone → update SOUL.md

**🟡 Zone process — mandatory before any external action:**
1. Agent presents: [action] + [reason] + [exact content/change] + [risk] + [cost]
2. User responds: OK / "Sửa [detail]" / "Ko"
3. Agent acts ONLY after user says OK

**Adapting per domain:** Zone examples in SOUL.md must match the domain's risk profile:
- **Ops profile:** 🟢 = parse KPI, review queue. 🔴 = sign contracts, delete data.
- **Stock profile:** 🟢 = analyze BCTC, calculate ratios. 🔴 = place orders.
- **Personal profile:** 🟢 = log health, capture content. 🔴 = investment decisions.

**Anti-pattern:** Assigning everything to 🟢 or everything to 🔴. The value is in the gradient.

**🛑 Companion — 5-Point Pre-Action Protocol:**
Every 🟡 Zone 2 action requires a structured 5-point gate (WHAT/WHY/EXACT CONTENT/RISK/APPROVAL) before execution. See `references/pre-action-protocol-5-point.md` in this skill for the full protocol. Applied in SOUL.md as §Pre-Action Protocol and in pre_edit_checklist.md as §10.

**📋 Pre-Edit Checklist Pattern:**
For every profile connected to a vault, maintain a `pre_edit_checklist.md` companion file in the vault's `00_CORE_LOGIC/`:
- **Naming convention:** Profile-prefixed — `personal_profile_pre_edit_checklist.md`, `stock-profile_pre_edit_checklist.md` (not bare `pre_edit_checklist.md` for non-default profiles)
- **Sections:** 1-9 cover vault write integrity (frontmatter, template, columns, append, index sync, language). §10 adds the 5-Point Pre-Action Protocol for external actions.
- **Mandated read:** SOUL.md §Session Start Protocol must include "đọc pre_edit_checklist.md trước mỗi lần ghi" as hard requirement.
**Post-creation sync:** After creating/updating a pre_edit_checklist.md for a profile, patch that profile's SOUL.md in two places: (1) §Quick Reference — add a line pointing to the file, (2) §Session Start Protocol — verify the vault-write requirement mentions it. Without this sync, the agent won't know the file exists.

### Concrete Example: stock-profile SOUL.md

See `references/stock-profile-soul-2026-06-23.md` for the final SOUL.md produced by this methodology, including:
- DATA_CONTRACT for BCTC integrity gate
- Confidence tag definitions [HIGH/MOD/LOW]
- Portfolio Dashboard template (qualitative, no fabricated numbers)
- Hard rules from a long-term investor (no short, no margin, no day-trade)

---

## MEMORY.md Design Methodology

MEMORY.md = agent's personal notes: environment facts, conventions, workflows. Always in context (injected every turn), so it must be **compact and high-signal**. 2,200 char limit.

### What Belongs in MEMORY.md

| Category | Example | Priority |
|----------|---------|----------|
| **Vault root + allowed folders** | `VAULT_ROOT = C:/Users/Warren/personal_vault` | HIGH (without this, agent can't navigate) |
| **Pulse / data file conventions** | Format rules, append rules, frontmatter requirements | HIGH (without this, agent corrupts data files) |
| **Tool commands** | Short reference: `stock-deep-research = deep research 1 ticker` | MOD (skill descriptions loaded on demand) |
| **YAML schemas** | Shared frontmatter fields across all pulse files | MOD (prevents schema drift) |
| **OS / environment facts** | Windows, git-bash, forward-slash paths | LOW (agent discovers these over time) |

Do NOT put in MEMORY.md:
- **User identity** (belongs in USER.md)
- **Voice/style rules** (belongs in SOUL.md or system prompt)
- **One-off task data** (put in vault files)
- **Procedural steps** that are long (put in a skill)

### Interview Workflow: MEMORY.md

Use `interview-me` to extract what facts the profile needs:

```
Phase 1 — VAULT PATH
├── Root directory OR explicit allowed subfolders?
├── GUESS: Root + allowed subfolders. Hardcoding specific file paths will go stale.
└── Decision: root + allowed folders. Agent self-discovers files via search.

Phase 2 — TOOL COMMANDS
├── Which tool references should be embedded (short alias + function)?
├── GUESS: 3-4 main tools, 1 line each. Skills descriptions are loaded on demand.
└── Decision: Keep tool references to 1-2 lines each, enough for agent to know which to invoke.

Phase 3 — FILE/DATA CONVENTIONS
├── What rules must be followed when writing/modifying profile data files?
├── Common rules: language (vi/en), entry order (newest on top), template safety (append after ```), frontmatter update policy
└── Decision: 4-6 bullet rules, no prose. Agent reads latest entry before writing for structural consistency.

Phase 4 — YAML SCHEMA
├── Common frontmatter schema across profile's data files?
├── GUESS: Shared schema = domain, type, status, created, last_updated, tags, [domain-specific fields]
└── Decision: 1 line listing fields. Detailed schemas belong in AGENTS.md or a skill.

Phase 5 — WRITE
├── Language: English (facts stay stable, VN in output only)
├── Format: bullet sections, no prose
├── Write to profile/memories/MEMORY.md
└── Verify char count ≤ 2,200
```

### MEMORY.md Content Guidelines

- **English** — facts are stable across sessions. Vietnamese only in agent output.
- **Bullet sections** — never prose. Each line = one retrievable fact.
- **Header-comment style** — key: value pairs for paths and schema, imperative bullets for rules.
- **Read-first discipline** — always tell agent to read latest entry's structure before writing a new one. Prevents format drift. Template hardcoding is an anti-pattern (templates change; facts should not).

### Dual SSOT Pattern: Vault-Level vs Profile-Level Memory

Hermes memory has two tiers serving different purposes:

| Tier | Location | Purpose | Format |
|------|----------|---------|--------|
| **Vault SSOT** | `<vault>/00_CORE_LOGIC/MEMORY.md` | Authoritative, version-controlled | Sections (Preferences/Corrections/Patterns/Lessons) |
| **Profile sync** | `profiles/<name>/memories/MEMORY.md` | What Hermes loads every session. 2,200 char limit. | Flat §-delimited durable facts |

**Dual-SSOT flow:** Vault SSOT is canonical. Profile-level MEMORY.md is the compact sync copy. `/compress-memory` distills raw lessons → writes structured SSOT → syncs to profile. Recommended for profiles WITH a dedicated vault (vault has git history, profile has the char-efficient fact list Hermes reads).

**Shared-vault variants:** When a profile shares a vault with another domain (e.g., stock-profile + personal-profile both use `personal_vault`), choose between two approaches:

- **Profile-only SSOT** — MEMORY.md stays in `profiles/<name>/memories/`; raw log `warren_memory_raw.md` and `archives/memory/` at profile root. No vault file scatter, no Obsidian visibility. Good for lightweight profiles where the user doesn't need to see memory in the vault.
- **Vault-SSOT with distinct naming** — Files live in vault with profile-prefixed names (`STOCK_MEMORY.md`, `_stock_profile_memory_raw.md`). Obsidian-visible, git-tracked. User accepts vault file scatter for visibility. Profile cache syncs from vault (1-direction).

**Naming convention for vault-SSOT shared files (Warren-approved 2026-07-01):** `{PROFILE}_{TYPE}.md`
- `STOCK_USER.md` (not USER_STOCK.md), `PERSONAL_USER.md`
- `STOCK_CONTEXT.md`, `PERSONAL_CONTEXT.md`
- `STOCK_MEMORY.md` (kept as-is), `PERSONAL_MEMORY.md`
- Same pattern for raw logs: `_inbox/_stock_profile_memory_raw.md`, `_inbox/_personal_memory_raw.md`
- Profile-prefixed pre_edit_checklist files: `stock-profile_pre_edit_checklist.md`, `personal_profile_pre_edit_checklist.md`

**Prefix over subfolder** — files sit flat in `00_CORE_LOGIC/` with prefix, not in subfolders (`stock/USER.md`). Keeps paths shorter, search faster, avoids nesting complexity when only 2-4 files per profile.

**Full paths required** — when referencing these files in SOUL.md, AGENTS.md, or plans, always use full path from vault root: `stock_vault/00_CORE_LOGIC/STOCK_USER.md` not `00_CORE_LOGIC/STOCK_USER.md`. Abbreviated paths cause confusion across profiles when both profiles reference the same folder.

**⚠️ Enforcement pitfall:** Every SOUL.md, AGENTS.md, and MEMORY.md must use `stock_vault/00_CORE_LOGIC/...` consistently. A single abbreviated path (`00_CORE_LOGIC/` or `_inbox/` without `stock_vault/`) is enough to cause confusion. After any profile file restructure, grep for bare `00_CORE_LOGIC/` and `_inbox/` in all profile files to catch stragglers. In the 2026-07-01 restructure, 12+ abbreviated paths had to be fixed across 6 files.

Interview to decide: does user need to see raw memory in Obsidian? If yes → vault-SSOT with distinct naming. If no → profile-only SSOT.

**Decision framework:**

| Scenario | Pattern | Rationale |
|----------|---------|-----------|
| Profile has dedicated vault | Vault SSOT + profile sync | Git versioning, clear SSOT, consistent with warren-profile |
| Profile shares vault with another domain | **Two sub-options:** (interview to decide) | |
| ¦-- Light: Profile-only SSOT | MEMORY.md stays in `profiles/<name>/memories/`; raw log + archives also profile-local | Avoid vault file scatter. No Obsidian visibility. |
| ¦-- Heavy: Vault-SSOT w/ distinct naming | `vault/00_CORE_LOGIC/<PROFILE>_MEMORY.md` + `vault/_inbox/_<profile>_memory_raw.md` | Obsidian-visible, git-tracked. Requires distinct filenames (`STOCK_MEMORY.md`, `_stock_profile_memory_raw.md`). User must accept vault file scatter. |
| Profile has no vault access at all | Profile-only SSOT | No vault to write to; keep everything in profile |
| Single profile, single vault | Vault SSOT + profile sync | All-in-one, cleanest |

**Profile-only implementation:**
- MEMORY.md stays in `memories/MEMORY.md` (what Hermes reads)
- Raw lessons: `warren_memory_raw.md` at profile root (prepend, section-tagged)
- Archives: `archives/memory/` at profile root (pre-compress backups)
- SOUL.md gets Self-Evolving Memory Loop section + Write Governance
- `warren_memory_raw.md` format matches SOUL.md §2.3: `[Preferences]`/`[Corrections]`/`[Patterns]`/`[Lessons Learned]` section tags

### SSOT Hard Rule (Warren Pattern)

When Warren says "SSOT" he means it literally:

> **🚫 HARD RULE — SSOT:** `vault/00_CORE_LOGIC/<FILE>_MEMORY.md` is the **Single Source of Truth**. Hermes **NEVER** auto-writes/logs/updates into built-in memory (the `memory` tool / profile cache `memories/MEMORY.md`) without explicit Warren command. Every memory write MUST go through: raw log → `/compress` → Warren approve → update vault SSOT → sync to profile cache. No exceptions. No auto-save. No "tự ghi nhớ".

**Distinction:** The vault SSOT (structured markdown) and the profile cache (§-delimited compact) are **two different formats** serving different layers:
- Vault SSOT = structured sections (Preferences/Corrections/Patterns/Lessons Learned) — for Obsidian, git, readability
- Profile cache = §-delimited flat entries — for Hermes built-in memory injection (2,200 char limit)

**Do NOT copy vault markdown directly into profile cache.** The formats are incompatible. The sync step in `/compress-memory` protocol writes the distilled content, not a raw copy.

### Path Pitfall: CLI vs Desktop

| Install mode | Profile path |
|--------------|-------------|
| **Hermes Desktop** (GUI app) | `%LOCALAPPDATA%/hermes/profiles/<name>/` i.e. `C:/Users/<user>/AppData/Local/hermes/profiles/<name>/` |
| **Hermes CLI** (terminal) | `~/.hermes/profiles/<name>/` |

**Common error:** Sync commands copy vault SSOT to `~/.hermes/profiles/<name>/...` but Hermes Desktop reads from `AppData/Local/hermes/profiles/<name>/...`. When using Hermes Desktop, ALWAYS use `AppData/Local/hermes/` paths for profile-level files. Verify by checking which profile directory has `state.db`, `config.yaml`, and `memories/`.

### Git Commit Trigger (vs End-of-Session)

Warren's preference (2026-06-28): Memory proposals trigger ONLY on `git commit`, not at end-of-session.

| Trigger | What happens |
|---------|-------------|
| **git commit** (preferred) | Hermes checks: what worked? what failed? any new rule? → propose → Warren says "ghi" → append to raw log |
| End-of-session | ❌ NOT used — Warren found it too noisy |
| Mid-task | ❌ NOT used — interrupts flow |

### Concrete Example: stock-profile MEMORY.md

See `references/stock-profile-memory-2026-06-23.md`.

---

## USER.md Design Methodology

USER.md = user profile: identity, philosophy, preferences, pet peeves. Always in context. 1,375 char limit.

### Separation Principle

| Layer | Role | Content |
|-------|------|---------|
| **SOUL.md** | Cách nói | Voice, tone, formatting rules, integrity gates |
| **USER.md** | Ai đang nói chuyện | Identity facts, philosophy, broker, pet peeves, data preferences |
| **MEMORY.md** | Môi trường làm việc | Vault paths, tool commands, conventions |

**Do NOT duplicate:** Stock criteria in both SOUL + USER → inconsistency risk. Pick one home.

**Do NOT include:** Holdings/positions (go in vault files, change too often). Communication style (goes in SOUL).

### Interview Workflow: USER.md

Use `interview-me` to extract user identity:

```
Phase 1 — IDENTITY CORE
├── Name, location, thinking style
├── Knowledge level (system-thinker? forgets details? expert in domain X?)
└── Decision: concise, 2-3 lines. Never PII unless explicitly requested.

Phase 2 — PHILOSOPHY
├── Investment/influence philosophy (Buffett, Munger, Lynch...)
├── Approach (all-in + DCA, concentrated, diversified...)
├── Broker preference
└── Decision: 1-2 lines. Philosophy shapes agent's recommendations.

Phase 3 — PET PEEVES
├── What does the user HATE in analysis?
├── Common: analysis without source, recommendations without risk assessment, long-winded theory, unsolicited non-domain advice
└── Decision: 3-5 bullet items. These are the user's red-line preferences.

Phase 4 — DATA PREFERENCE
├── How should data be presented?
├── Common: comparisons > absolutes, ratios > raw numbers, % change > single snapshot
└── Decision: 1-2 lines. This is formatting preference, not voice.

Phase 5 — USAGE PATTERN
├── When does the user engage? (ad-hoc? weekly? monthly?)
└── Decision: 1 line. Helps agent prioritize.

Phase 6 — WRITE
├── Language: English (profile identity is stable, VN only in output)
├── Write to profile/memories/USER.md
└── Verify char count ≤ 1,375
```

### What NOT to Put in USER.md

| Item | Where it belongs | Why |
|------|-----------------|-----|
| Communication style | SOUL.md or system prompt | Voice/form is how agent acts, not who user is |
| Stock/domain criteria | SOUL.md (if rule) or skill | Criteria is instruction to agent, not identity fact |
| Holdings / positions | Vault pulse files | Changes too often, char-inefficient |
| PII (phone, email, age) | Nowhere | Unnecessary, security risk, wastes chars |
| Tool commands | MEMORY.md | Workflow fact, not user identity |

### Concrete Example: stock-profile USER.md

See `references/stock-profile-user-2026-06-23.md`.

---

## AGENTS.md Design Methodology (Profile-Level)

AGENTS.md at profile level (`~/.hermes/profiles/<name>/AGENTS.md`) is **independent** from vault-level AGENTS.md. Both load — they coexist. Profile AGENTS = scope + conventions; vault AGENTS = project-wide rules.

### When to Create Profile-Level AGENTS.md

| Signal | Action |
|--------|--------|
| Profile has a different vault root than default | Create — agent needs to know where to read/write |
| Profile has domain-specific file conventions (OCR priority, BCTC source order) | Create — conventions are per-domain |
| Profile has READ/WRITE boundaries to prevent cross-domain pollution | Create — prevents agent writing to health/family folders |
| Profile shares the same vault as personal profile | Create — define boundaries explicitly to avoid conflicts |

### Interview Workflow: AGENTS.md

Use `interview-me` to extract project context:

```yaml
# Phase 1 — FRONTMATTER
├── YAML frontmatter for consistency with other profiles
├── Fields: name, description, role, language, source_of_truth, cite_numbers, changes_effective, profile_type
├── GUESS: Always include frontmatter. Tools and search engines need structured handles.
└── Decision: Yes — consistent YAML across all profiles.

# Phase 2 — VAULT ACCESS
├── Root directory path
├── Read/write allowed subfolders (list, not tree — saves chars)
├── GUESS: Root + subfolder list. Per-file paths go stale. Agent self-discovers via search.
└── Decision: Root + allowed subfolder list. Include future-proof wildcard (024-029).

# Phase 3 — BOUNDARIES (CRITICAL)
├── Which folders/files is this profile explicitly NOT allowed to write to?
├── Common: _ideas/, _cases/, _tasks/, Daily_Pulse.md (personal journal), CONTEXT.md
├── GUESS: Preventing cross-domain write pollution is the #1 reason for profile isolation.
└── Decision: Explicit DO NOT list. Include a catch-all: "All unlisted folders are read-only unless explicitly asked."

# Phase 4 — RUNTIME NOTES
├── OS, shell, working directory, default data sources, preferred tool order
├── GUESS: 3-5 lines max. OS + working dir are essential; data source preference is useful.
└── Decision: Include OS (Windows git-bash), working dir, default BCTC source + cross-check sources.

# Phase 5 — TECHNICAL CONVENTIONS
├── Any domain-specific technical priority (OCR tool order, PDF parser preference)
├── GUESS: Put technical conventions here, NOT in MEMORY.md. MEMORY = env facts; AGENTS = conventions.
└── Decision: Yes — OCR priority (liteparse first, fallback), source citation format.

# Phase 6 — PROFILE FILES INDEX
├── Quick reference for agent: what each layer (SOUL/MEMORY/USER) contains
├── GUESS: 3-4 lines, pointers only. Saves agent from opening all files just to find what's where.
└── Decision: Add one-line-per-layer summary at bottom of AGENTS.md.

# Phase 7 — WRITE
├── Language: English (consistent with all other layers)
├── File: ~/.hermes/profiles/<name>/AGENTS.md
└── Verify: Agent can read this + vault AGENTS.md without confusion (they coexist).
```

### What NOT to Put in Profile AGENTS.md

| Item | Where it belongs | Why |
|------|-----------------|-----|
| SOUL.md rules (voice, integrity gate, stock criteria) | SOUL.md | Repeat causes drift when SOUL updates |
| Tool commands | MEMORY.md | MEMORY is always in context; AGENTS is project architecture |
| Individual file paths | Nowhere | Folder-level is sufficient; agent self-discovers |
| User identity | USER.md | AGENTS is about the project, not the user |
| Pulse format rules | MEMORY.md | Property of environment/workflow, not project scope |

### Standardized SOUL.md Section Template (Warren-approved 2026-07-01)

When building a new profile SOUL.md, use this 10-section numbered format. Each section covers one behavioral dimension:

```markdown
---
name: "<profile-name>"
type: "agent_identity"
domain: "<domain>"
---

# SOUL — <profile-name>

One-liner identity.

## 1. IDENTITY            — Role, mission, what agent is NOT, style, language.
## 2. COMMUNICATION       — Tone, format, pet peeves, favorite templates.
## 3. DATA QUALITY TAGS   — [HIGH]/[MOD]/[LOW]/[UNKNOWN] definitions.
## 4. DATA_CONTRACT       — When analysis runs vs when it waits for source.
## 5. INTEGRITY GATE      — Domain-specific check criteria (stock: OCF vs NI, etc.).
## 6. OUTPUT TEMPLATE     — Structured output format for primary deliverable.
## 7. MEMORY LOOP         — SSOT/Raw log/Built-in cache + cycle + governance.
## 8. HARD RULES          — Numbered non-negotiables (see checklist below).
## 9. PROFILE MAP         — Table of SOUL/USER/MEMORY/AGENT with vault paths.
## 10. SESSION PROTOCOL   — Ordered file read at session start.
```

**Hard Rules checklist (add as needed):**
1. Domain confinement (what profile does/doesn't cover)
2. Pushback rule (when to challenge user)
3. Silent unless triggered (no spam)
4. Citation (every data point needs source)
5. Domain priority (GG first for personal, thesis discipline for stock)
6. Financial/capital priority (EF flag, allocation rules)
7. **Memory write protection** — never auto-write built-in memory without "ghi"
8. **Cross-domain forbidden zone** — explicitly forbid the other profile's folders

**AGENT.md naming:** Profile-level AGENT files follow the `{PROFILE}_AGENT.md` convention: `STOCK_AGENT.md`, `PERSONAL_AGENT.md`. New profiles MUST use prefix naming. Existing profiles using bare `AGENTS.md` can migrate at rename opportunity.

### Cross-Profile Forbidden Zones (Bidirectional Pattern)

When a second profile is created in a shared vault, BOTH profiles need `🚫 TUYỆT ĐỐI CẤM` sections. This is **bidirectional** — personal→stock AND stock→personal:

| Profile | Forbids | In SOUL.md | In AGENT.md |
|---------|---------|------------|-------------|
| personal_profile | `03_Investing/`, `020_VNStock_*`, `STOCK_*` | HARD RULE #8 | Access: 🚫 TUYỆT ĐỐI CẤM |
| stock-profile | `02_Health/`, `Daily_Pulse.md`, `050/051_Health_Log.md`, `PERSONAL_*`, `_cases/` | HARD RULE #8 | Access: 🚫 TUYỆT ĐỐI CẤM |

One-direction is not enough. Without bidirectional protection, switching to profile A and discussing domain B causes memory pollution. Both profiles must explicitly forbid each other's folders from read/grep/search.

**Implementation in AGENT.md (both profiles):**
```
## Access: what I touch

🚫 TUYỆT ĐỐI CẤM:
├── 30_KNOWLEDGE_BASE/wiki/03_Investing/     (stock domain — forbidden to read/grep/search)
├── 10_PULSE/020_VNStock_*                   (stock pulse — forbidden to read/grep/search)
├── 00_CORE_LOGIC/STOCK_*                    (stock context — forbidden to read/grep/search)
└── 30_KNOWLEDGE_BASE/raw/                   (NEVER write)
```

**When to use:** Profile has zero business in the other domain — personal_profile should never interact with stock analysis, stock-profile should never touch health/family files.

**Signal to add:** User explicitly says "ko được read/grep/search" about a folder. This overrides the weaker "read-only" boundary.

### Concrete Example: stock-profile AGENTS.md

See `references/stock-profile-agents-2026-06-23.md`.

---

## Profile-Level AGENTS.md Pattern

AGENTS.md is not just for vault roots. Each profile can have its own AGENTS.md at:

```
~/.hermes/profiles/<profile-name>/AGENTS.md
```

This is **independent** from the vault's AGENTS.md. Both are loaded:
- **Profile AGENTS.md** (`~/.hermes/profiles/<name>/AGENTS.md`) — profile-specific conventions, vault paths, domain scope
- **Vault AGENTS.md** (`<vault_root>/AGENTS.md`) — project-wide rules, architecture

### When to Use Profile-Level AGENTS.md

- When the profile needs its own working directory / vault reference (e.g., stock-profile → personal_vault, HORION → Warren_OS_Local)
- When the profile has domain-specific conventions that don't belong in shared vault AGENTS.md
- When you want to avoid polluting the shared vault AGENTS.md with profile-specific rules

### Example: HORION Profile AGENTS.md

HORION's `~/.hermes/profiles/HORION/AGENTS.md` contains:
- Phạm vi (3 L'Usine restaurants)
- Vault reference (`Warren_OS_Local`, not `personal_vault`)
- Profile-specific rules (language, conclusion-by-recommendation, no-double-SOUL rule)
- Working directory conventions

### Example Use Case: stock-profile

stock-profile's `~/.hermes/profiles/stock-profile/AGENTS.md` could contain:
- Read/write access to specific pulse folders (020-029, wiki/investing, 00_CORE_LOGIC)
- Profile-specific runtime notes
- Cross-reference to SOUL.md + MEMORY.md for the agent (e.g., "Stock criteria in SOUL.md; pulse format rules in MEMORY.md")

---

---

## When to Split Profiles

| Signal | Action |
|--------|--------|
| Different humans using Hermes | Separate profiles (mandatory) |
| Radically different toolchains (e.g., one needs browser, one air-gapped) | Separate profiles |
| Conflicting model/provider requirements that can't be solved per-task | Separate profiles |
| Security isolation requirement (work vs. personal on shared machine) | Separate profiles |
| **Memory separation requirement** — user wants Hermes to have zero cross-domain memory pollution (e.g., stock research memories should never load when discussing health/family, and vice versa) | **Separate profiles.** Memory is per-profile, so domain-specific profiles give clean context isolation. Junction technique bridges skills. |

## When to Consolidate — Merge Strategy

**Scenario:** Same human, ~95% skill overlap, different vaults/domains.

**Symptoms:**
- Duplicate skill installs/maintenance across profiles
- "Forgot to switch profile" errors
- Cognitive load: "which profile has `ops-query`?"
- Cronjob/model/config drift between profiles

**Solution:** Single profile with **domain-namespaced skills**:
- `ops-morning-brief` (reads `VAULT_ROOT=lusine`)
- `personal-morning-brief` (reads `VAULT_ROOT=personal`)
- Both loaded simultaneously, no switching needed
- Model override per-task via `/model` or cronjob `model` field

## When to Consolidate — Single Canonical Source Strategy (Warren's Choice)

**Scenario:** Same human, different vaults on purpose, but ALL skills must live in ONE master profile.
Other profiles are "thin shells" — they exist only to reference their vault / AGENTS.md with ZERO skills.

**Symptoms:**
- Warren explicitly: "tôi ko muốn những profile còn lại có bất kỳ command/script/parser/skill nào"
- User wants one canonical place to maintain — no drift risk
- Profile switching is acceptable for vault access; skill use requires master profile

**Solution:** Strip skills from all profiles EXCEPT the canonical master.
```
warren-profile  (75 skills)  ← ALL skills live here
lusine-profile  (0 skills)   ← thin shell, vault access only
personal_profile (0 skills)  ← thin shell, vault access only
```

## Consolidation Playbook (Merge)

1. **Audit skill overlap** → `hermes skills list -p profileA` + `profileB`
2. **Identify domain-unique skills** (e.g., `lusine-ops` vs `personal-commands`)
3. **Pick a base profile** (usually the more mature one)
4. **Install domain-unique skills into base** — they coexist via namespacing
5. **Migrate cronjobs** → single profile, each job declares its `VAULT_ROOT` via env or skill config
6. **Migrate model config** → default model for primary domain, per-job/task override for secondary
7. **Delete old profile** → `hermes profile delete old-profile`
8. **Update aliases/scripts** → point to single profile

## Consolidation Playbook (Single Canonical Source)

1. **Audit uniqueness** — verify master profile has ALL skills from other profiles. Any unique skill in non-master profile? → copy to master first.
2. **Cron job audit** — check all cron jobs: do they reference non-master profile names, paths, or skill paths? If yes, migrate to master.
3. **Strip non-master profiles** → `rm -rf ~/AppData/Local/hermes/profiles/<non-master>/skills/`
4. **Verify**:
   - `ls ~/AppData/Local/hermes/profiles/<non-master>/skills/` → not found or empty
   - `ls ~/AppData/Local/hermes/profiles/master/skills/` → count unchanged
   - Critical skills (`ops-cases`, `vault-structure-audit`, etc.) still present in master
5. **Document** — update vault README.md stating which profile is canonical and that other profiles are zero-skill shells.

## Vault Access Pattern

### For Merge Strategy (single profile, multiple vaults):
Skills read `VAULT_ROOT` from:
- Cronjob `env` field (preferred for scheduled work)
- Skill config YAML (for interactive use)
- `/model` + `VAULT_ROOT` combo for ad-hoc tasks

### For Single Canonical Strategy (multiple thin-shell profiles):
- Skills live only in master profile
- Vault files accessible from any profile (they're on filesystem)
- To run commands → switch to master profile via `hermes profile set master-profile`
- Thin-shell profiles have AGENTS.md for Hermes session context but zero executable skills

## Cross-Profile Skill Access (Critical Architecture Note)

**Skills ARE per-profile.** Hermes Desktop loads skills from the active profile's `skills/` directory. If you strip all skills from a profile, that profile CANNOT load any skill — including skills living in another profile's `skills/` directory.

### The Windows Junction Technique

On Windows, `ln -s` (git-bash) creates FAKE symlinks — Python `os.path.islink()` returns False and contents don't update dynamically. Instead:

```python
import subprocess, os, shutil

junc_path = r'C:\...\personal_profile\skills\personal-commands'
target = r'C:\...\warren-profile\skills\personal-commands'

if os.path.exists(junc_path):
    shutil.rmtree(junc_path)

result = subprocess.run(
    ['cmd.exe', '/c', 'mklink', '/D', junc_path, target],
    capture_output=True, text=True, shell=True
)
# Verify:
print('Is link:', os.path.islink(junc_path))  # Must be True
print('Contents:', os.listdir(junc_path))     # Must match target
```

**Requirements:**
- Python subprocess with absolute paths (not `ln -s` in git-bash/MSYS)
- `mklink /D` = directory junction, NOT `ln -s` — real junction, dynamically reflects target
- No admin required if Developer Mode is enabled on Windows 10/11
- Contents update dynamically when new files are added to target

### The Linux / macOS Approach

On Linux/macOS, real symlinks work natively:
```bash
ln -s /path/to/master-profile/skills/shared-category /path/to/thin-profile/skills/shared-category
```

### Git Cleanup Pattern: Always Use `git rm` for Tracked Files

When deleting files from a git-tracked vault, plain `rm -rf` removes the file from the filesystem but git still tracks it. On the next `git add -A && git commit`, git restores the deleted file from its index. This causes phantom re-appearances — deletions that silently undo themselves.

**Rule:** For any file tracked by git, always use `git rm <path>` (for files) or `git rm -rf <path>` (for directories). This stages the deletion in git's index AND removes the file from disk in one step.

**Recovery if files keep reappearing after `rm`:** Check `git status` — if the file shows as "modified" (deleted) but keeps coming back, switch to `git rm` and commit immediately.

**Exception:** Empty directories (git doesn't track them — they stay as filesystem shells after `git rm`). Use `rmdir` or `rm -rf` separately to clean up empty directory shells after git rm commits. Verify with `git status --porcelain` that no untracked remnants remain.

**Must include junction step after stripping skills:**

1. **Audit uniqueness** — verify master profile has ALL skills from other profiles
2. **Cron job audit** — migrate cron jobs to master profile
3. **Strip non-master profiles** — remove skill categories from thin profiles EXCEPT categories you'll junction
4. **Set up junction** for shared skill categories → Python subprocess + `mklink /D` (Windows) or `ln -s` (Linux/macOS)
5. **Verify cross-profile access** → switch to thin profile, try loading a skill:
   ```
   hermes profile set thin-profile
   # Then invoke: "run <skill-name>" — must work
   ```
6. **Document** — update vault README.md stating which profile is canonical, junctioned categories, and the recovery command

## Execution: Vault Split (One Domain → Separate Vault)

When splitting ONE profile's vault into two separate vault repos (e.g. stock-profile's `personal_vault` → new `Stock_OS/stock_vault`, personal_profile keeps `Personal_OS/personal_vault`):

### Step 0: Decide Path Convention (user NON-IT → agent decides)
- User said "tôi non dân it, có biết gì đâu" → **agent picks the path, states it, does NOT ask.** Mirror the existing pattern: `Stock_OS/stock_vault/` matches `Personal_OS/personal_vault/`.
- Do NOT surface path micro-decisions to a non-IT user. State the decision, proceed to approval gate.

### Step 1: Backup BEFORE any move (always)
```bash
cp -r Personal_OS/personal_vault Personal_OS_BACKUP_2026-07-18
# verify: ls Personal_OS_BACKUP_2026-07-18/00_CORE_LOGIC/STOCK_MEMORY.md
```
Keep the backup until the split is verified + committed. Delete only after user confirms.

### Step 2: Inventory — `cp -r` the whole domain tree
- Identify ALL artifacts: wiki (48 files), `STOCK_*` core logic, pulse files, `_inbox` raw, `_archives/memory`, vault `scripts/`.
- Also catch the NON-OBVIOUS: `.smart-env/multi/*.ajson` (auto-generated mirrors — DELETE from source, they regenerate), `RETRIEVAL_MAP.md` / `00_WIKI_INDEX.md` stock rows, cross-refs in `PERSONAL_CONTEXT.md` / `README.md` / `PERSONAL_USER.md`.
- **Cache trap:** `search_files` returns STALE results after `rm` (it caches the index). During a migration, the SOURCE OF TRUTH is terminal `ls` / `find` / `grep -rln`, NEVER `search_files`. A deleted file can still show in `search_files` for minutes.

### Step 3: Move (all `cp -r`, reversible) then Purge source
- `cp -r` stock tree → Stock_OS. Verify counts (find ... | wc -l).
- Purge source: `rm -rf 03_Investing/`, `STOCK_*`, stock pulse, `_inbox` raw, `_archives/memory/STOCK_*`, stock `scripts/`, `.smart-env/multi/*stock*`, `_tmp_broker/`, `weekly_connections_log.md`.
- **Leave alone (historical, not live):** `.archive/index_backup_*/WIKI_INDEX.md` (old snapshot), `log.md` (change-log with past stock entries), `.obsidian/themes/*.css` (false-positive var names). Only LIVE wikilinks/index entries matter.

### Step 4: Rewrite indices + docs in BOTH vaults
- Stock_OS gets fresh `RETRIEVAL_MAP.md` + `00_WIKI_INDEX.md` + `00_PULSE_INDEX.md`.
- Personal_OS: remove stock rows from indices, keep a one-line "MOVED → Stock_OS/..." pointer (intentional, NOT a leak). Update `PERSONAL_USER.md` cross-profile pointer path.
- Scripts (vault `scripts/` + profile `scripts/` + `skills/**`): replace `Personal_OS/personal_vault` → `Stock_OS/stock_vault`. Batch with `python3` + `pathlib.write_text` (see runbook).

### Step 5: Repoint cron jobs
- `cronjob action=update` with `workdir=C:/.../Stock_OS/stock_vault` for stock scripts (stock-price-daily, frameworks-weekly, mem0-cleanup).
- Verify with `cronjob list`.

### Step 6: Git commit BOTH vaults (separate repos)
- Stock_OS: `git init` NEW repo (do NOT carry Personal_OS history). Commit.
- Personal_OS: `git add -A && git commit` (purge). LF/CRLF warnings are harmless on Windows.
- **Cross-profile `patch` guard:** the `patch` tool BLOCKS writes to another profile's `skills/` (soft guard — "belongs to profile warren-profile but agent runs under stock-profile"). BYPASS with terminal `python3` + `pathlib` (the guard is defense-in-depth, not a hard boundary). Only do this for stock scripts that live under another profile's tree.

### Step 7: Obsidian vault
- Copy `.obsidian/` (config is relative-path, 0 hardcoded vault root) → new vault. Obsidian → Open folder as vault → `Stock_OS/stock_vault`.
- Plugins (Dataview, Smart-Connections, Homepage) inherit. Smart-Connections re-indexes on first open.

### Step 8: Verify (acceptance)
```bash
# Personal_OS: 0 live stock hits (excluding .archive + log.md + intentional MOVED pointer)
cd Personal_OS/personal_vault && grep -rln "VN_Equities\|STOCK_MEMORY\|03_Investing\|Holdings.md" . --exclude-dir=.git | grep -v "_archive" | grep -v "MOVED"
# stock-profile: 0 Personal_OS refs in code
grep -rln "Personal_OS/personal_vault" profiles/stock-profile/skills profiles/stock-profile/scripts
# both committed
git -C Stock_OS/stock_vault rev-parse --short HEAD
git -C Personal_OS/personal_vault rev-parse --short HEAD
```

### Anti-patterns (this session)
| Mistake | Fix |
|---------|-----|
| Trusting `search_files` after `rm` | Use terminal `ls`/`find`/`grep -rln` as source of truth during migration |
| Forgetting `.smart-env/*.ajson` mirrors | They are auto-generated — delete from source, regenerate on vault open |
| Deleting `.archive/` + `log.md` historical stock refs | Leave them — historical, not live links |
| Hardcoding `Personal_OS/personal_vault` in moved scripts | Batch `pathlib.replace` → `Stock_OS/stock_vault` |
| Using `patch` on another profile's skills | Cross-profile guard blocks it — use terminal `python3` |
| Asking non-IT user "which path?" | Agent decides, states, proceeds to approval gate |

See `references/vault-split-runbook-2026-07-18.md` for the full executed session (commands + verification output).

## Execution: Profile Split (Domain Separation)

When splitting an existing profile into a new domain-specific profile (e.g., personal → stock):

### Step 1: Clone + Junction

```bash
# 1. Create profile from existing
hermes profile create new-profile --clone-from existing-profile

# 2. Junction skills → canonical profile (Windows)
python3 -c "
import subprocess, os, shutil

junc_path = r'C:\...\new-profile\skills'
target = r'C:\...\canonical-profile\skills'

shutil.rmtree(junc_path)
result = subprocess.run(
    ['cmd.exe', '/c', 'mklink', '/D', junc_path, target],
    capture_output=True, text=True, shell=True
)
# Verify
assert os.path.islink(junc_path), 'Junction failed'
print('Junction OK:', os.listdir(junc_path)[:5])
"
```

### Step 2: Memory Migration — Move, Do NOT Copy

Hermes memory is per-profile. When splitting:

```
existing-profile/        new-profile/
  memories/                memories/
    MEMORY.md  ←──move──→   MEMORY.md  (only domain-A entries)
    USER.md    ←──move──→   USER.md    (only domain-A entries)
```

**Rules:**
- **Move** each entry, never copy. Zero overlap is the goal.
- **Grey zones** (e.g., finance = personal or investing?): classify once, document the decision. If uncertain, keep in base profile and adjust later.
- **Shared entries** (e.g., workflow preferences, tool quirks): keep in base profile. New profile inherits them only from junction/context, not from memory.
- **USER.md split:** Personal identity (name, location, family) stays in base. Domain-specific identity (investor, trader) + domain rules go to new profile.

**Memory classification:**
| Signal | Classification |
|--------|---------------|
| Mentions tickers, BCTC, EPS, broker, trading | → STOCK / INVESTING |
| Mentions sleep, health, family, court, GG | → PERSONAL / HEALTH |
| Mentions COL, CPH, revenue, LTO, F&B | → OPS |
| Mentions tool quirks, path conventions, workflow preferences | → SHARED (keep in base) |

After splitting, verify:
```bash
grep -c "BCTC\|ticker\|broker" existing-profile/memories/MEMORY.md
# Should be 0 if all stock entries moved
```

### Step 3: Cron Audit

Not all cron jobs need migration:
- **Domain-specific cron** (e.g., broker pipeline, stock fetcher) → belongs in new profile
- **Infra cron** (vault lint, backup, index sync) → stays in base/default profile
- Check: `hermes cron list` under each profile

If no domain-specific cron exists yet, skip — create when needed.

### Step 4: Verify

```bash
# List profiles
hermes profile list

# Switch and test
hermes profile use new-profile
# Invoke a skill: "capture-stock" or "deep research <ticker>"
# Check memory: Hermes should NOT mention old domain's topics

hermes profile use existing-profile
# Hermes should NOT mention new domain's topics
```

### Step 5: Gradual Rename (Optional)

If skill names carry the old domain prefix (e.g., `personal-stock-ingest`), rename slowly — when the skill is next touched, not all at once:

| Old name | New name | When |
|----------|----------|------|
| `deep-research-stock` | `stock-deep-research` | Next use |
| `personal-stock-ingest` | `stock-ingest` | Next use |

**Safer rename via curator archive:**
1. Create new skill with `skill_manage(action='create', name='new-name', content=updated_SKILL.md)`
2. Copy supporting files (`scripts/*`, `templates/*`) from old skill to new
3. Archive old skill: `hermes curator archive old-name`
   - Old skill moves to `.archive/` — recoverable via `hermes curator restore old-name`
   - Git detects the rename (preserves history)
   - Junction still works throughout transition

This is safer than raw directory rename — curator handles cleanup and archive is recoverable. Also avoids junction breakage during the split-second window when the directory doesn't exist.

**Path-hardcoding trap in multi-profile setups:**
Scripts and cron jobs often hardcode profile paths (e.g., `personal_profile`). When creating cross-profile tools:
- Always reference the **canonical profile** (warren-profile), not the originating profile
- Check for hardcoded paths after any profile split: `grep -n "personal_profile\|lusine-profile" scripts/`
- Common culprits: google-workspace script imports, config.yaml references, cron script paths

## Three-Profile Architecture (Warren's Pattern)

For users who need **ops + investing + personal** with memory-zero-overlap:

```
warren-profile    → Ops (L'Usine). Default profile. Skills: canonical.
                    Memory: COL, CASES, weekly reports, revenue.
                   
stock-profile     → Investing (VN equities, BTC, Poly).
                    Memory: BCTC patterns, EPS, broker pipelines, watchlists.
                    Junction: skills/ → warren-profile/skills/
                   
personal_profile  → Health, sleep, family, court, GG.
                    Memory: sleep quality, GG access, court dates.
                    Junction: skills/ → warren-profile/skills/
```

**Rules:**
- Skills always canonical at warren-profile. Other profiles use junction.
- Memory: zero overlap. Move (never copy) when splitting domains.
- User switches manually (`hermes profile set <name>`). No auto-detect.
- Junction = `mklink /D` via Python subprocess (Windows) or `ln -s` (Linux/macOS).

**When this pattern fits:**
- User accepts manual profile switching
- Memory pollution is an active pain point
- Domains are genuinely disjoint (ops ≠ investing ≠ health)
- Skills are >=95% shared (can be junctioned from one canonical source)

| Anti-pattern | Why It Fails |
|--------------|--------------|
| "Orchestrator profile" that delegates to domain profiles | Adds layer, doesn't solve duplicate maintenance; profiles stay isolated |
| Symlinking vaults into profile | Couples vault lifecycle to profile; breaks multi-tool access (Obsidian, VS Code) |
| Keeping profiles "just in case" (with skills) | Drift accumulates; cognitive tax compounds |
| Keeping thin-shell profiles with stale skills | Zero-value; skills are never called but can still drift from canonical. Strip completely, or junction to canonical. |
| **Claiming "100% skill consolidation" without verifying cross-profile loading** | Skills are per-profile. Stripping from thin profiles breaks cross-profile access. Always verify: switch to thin profile and load a skill before declaring consolidation complete. |
| **Using `ln -s` on Windows for cross-profile skill access** | Git-bash `ln -s` creates a fake directory copy, not a real symlink. Contents don't update dynamically. Python `os.path.islink()` returns False. Use `mklink /D` via Python subprocess instead. |

## MSYS Path Prefix Quirk (Windows)

When using `write_file` or `patch` with MSYS-style paths (`/c/Users/...`), the tool can produce a double-prefix path like `C:\c\Users\khoans\...`. This is because MSYS converts `/c/` to `C:\` internally, and the tool appends another `C:\` prefix.

**Prevention:** Always use absolute Windows paths:
```python
# ✅ Correct
path = r'C:\Users\khoans\AppData\Local\hermes\...'

# ❌ Risky  
path = '/c/Users/khoans/AppData/Local/hermes/...'
```

**Recovery if file lands at wrong path:**
```bash
mv "C:/c/Users/khoans/Actual/Path/file.md" \
   "/c/Users/khoans/Actual/Path/file.md"
```

### Patch Tool Multiline Trap

The `patch` tool can silently fail when `new_string` contains multi-line content with special characters (emojis, Unicode, markdown formatting). It returns `"success": true` but the file is **not modified**.

**Symptoms:** Verification script catches content missing; file unchanged after successful patch report.

**Prevention:**
- For small files (≤100 lines), prefer `write_file` with the complete new content
- For large files, use `patch` only with SHORT single-line replacements
- Always verify after `patch` on multiline content: `grep` for the added section or run a diff check

**Recovery:** Read the file, construct the full desired content, and write with `write_file`.

## References

- `references/00-core-logic-restructure-2026-07-01.md` — 00_CORE_LOGIC split into profile-specific files: naming convention, path enforcement, git rm pitfall, bidirectional forbidden zones, wikilink fragility.
- `references/cross-profile-cron-management.md` — Direct edit technique for cron jobs in non-active profiles (bypasses cronjob tool scope limitation)
- `references/profile-consolidation-case-study.md` — This session's L'Usine + Personal OS analysis
- `references/cross-profile-junction-technique.md` — Windows junction setup + verification
- `references/stock-profile-creation-2026-06-23.md` — Stock profile split: full execution log
- `references/stock-profile-creation-session-2026-06-23.md` — Session record: commands, decisions, memory map
- `references/mem0-troubleshooting.md` — 4-layer diagnostic pattern when mem0 fails to init (config → package → Docker → Qdrant)
- `references/personal-profile-creation-2026-07-01.md` — Personal profile bootstrap from scratch: SOUL.md → PERSONAL_AGENT.md → memories/MEMORY.md, with shared-vault naming and cross-profile forbidden zones
- `references/personal-profile-creation-session-2026-07-01.md` — Session record: commands, decisions, file list, bidirectional forbidden zones
- `references/soul-slim-refactor-2026-07-15.md` — Warren SOUL 2,997→1,132 words: what moved to skills/pointers + mandatory dangling-reference verification bash.