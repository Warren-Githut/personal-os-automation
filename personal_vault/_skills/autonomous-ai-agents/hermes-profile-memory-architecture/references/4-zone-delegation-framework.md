# 4-Zone Delegation Framework 🟢🟡🟠🔴

> **Purpose:** Define explicit boundaries for agent autonomy in SOUL.md §Core Rules.
> Instead of vague "be autonomous but be careful", assign every task class to one of 4 zones.
>
> **Created:** 2026-06-29, from Hermes Agent Daily Assistant Prompt Pack analysis.
> **Applied to:** warren-profile (L'Usine Ops), stock-profile (equities analyst), personal_profile (personal AI).

## When to Use

- Architecting a new profile's SOUL.md — build zones in from the start
- Profile scope creep — agent acting on tasks it shouldn't → tighten zones
- User says "sao tự ý làm cái này?" / "sao không làm cái kia?" → task fell in wrong zone
- Adding high-risk workflows (money, external messages, production writes)

## The Four Zones

| Zone | Name | Agent action | User touch |
|------|------|-------------|------------|
| 🟢 | **TỰ LÀM HOÀN TOÀN** | Executes without asking | None (0-touch) |
| 🟡 | **DRAFT → WARREN APPROVE** | Research, prepare, draft; waits for OK | Approve / edit / reject |
| 🟠 | **NHẮC / CHUẨN BỊ CONTEXT** | Only gather info + remind | Agent does NOT act |
| 🔴 | **TỰ LÀM TAY** | Touches nothing — even draft | Manual only |

### 🟢 ZONE 1: No approval needed

**Conditions (ALL must be true):**
- Risk = 0 (no money, no people impact, no public exposure)
- Result is reversible (can undo or redo)
- Agent has explicit SOP from prior sessions or SOUL.md
- Task is internal (conversation / local files / read-only)

**Examples per profile:**

| Profile | 🟢 tasks |
|---------|----------|
| **warren (ops)** | Parse files, calculate KPI, draft analysis, check queues, search web |
| **stock** | Compute OCF/NI, calculate P/E vs 5Y avg, fetch news, run integrity gate scan |
| **personal** | Log health data, capture web content, compute personal finance totals |

### 🟡 ZONE 2: Draft → approval-only

**Triggers (ANY true → zone 🟡):**
- Action touches production data (write vault, edit config, run parser)
- Action affects other people (send message, create event, email)
- Action costs money (order, payment, subscription change)
- Workflow is new — never been tested before

**Process (hard requirement in SOUL.md):**
```
1. Agent presents: [action] + [reason] + [exact content] + [risk] + [cost]
2. User: OK / "Sửa [detail]" / "Ko"
3. Agent: act ONLY after user says OK
```

**🛑 Companion gate — 5-Point Pre-Action Protocol:**
Every 🟡 action also requires the full 5-Point Pre-Action Protocol (see `references/pre-action-protocol-5-point.md`). The 3-step process above is the summary; the 5-point protocol adds structured fields (WHAT/WHY/EXACT CONTENT/RISK/APPROVAL) and explicit rules for edit/reject flows.

**Placement in SOUL.md and pre_edit_checklist.md:**
- SOUL.md: The delegation zones section defines WHICH zone a task falls in
- SOUL.md §[N+1]: The Pre-Action Protocol section defines HOW 🟡 actions are executed
- pre_edit_checklist.md §10: The companion checklist for vault write operations + external actions

**Examples per profile:**

| Profile | 🟡 tasks |
|---------|---------|
| **warren (ops)** | Write to vault, edit config, send Telegram, create calendar events, run parser first time |
| **stock** | Write thesis/anti-thesis, propose entry/exit price, recommend portfolio rebalance |
| **personal** | Write to personal vault, create investment note, send email, schedule appointments |

### 🟠 ZONE 3: Reminder / context-prep only

**Triggers:**
- Decision requires user's strategic judgment
- Task only user can do (negotiation, relationship, signing)
- Not enough context for agent to recommend

**Output format:**
```
Context (data, summary, options)
→ Question for user to decide
→ Agent does NOT act
```

**Examples per profile:**

| Profile | 🟠 tasks |
|---------|----------|
| **warren (ops)** | "Focus margin or covers this week?", prepare data for supplier meeting |
| **stock** | "BCTC Q3 due — check date", "PVD dropped 20% — review?", compile weekly news |
| **personal** | "3 months since portfolio review", "Tonight is kid's class", compile options before user decides |

### 🔴 ZONE 4: Manual only — agent NEVER touches

**Triggers:**
- Legal / compliance impact (contracts, pricing, termination)
- Irreversible impact (delete data, close store, transfer assets)
- Personal / emotional (staff evaluation, family decisions, negotiation)
- Task user has never delegated → default zone 🔴

**Examples per profile:**

| Profile | 🔴 tasks |
|---------|----------|
| **warren (ops)** | Sign contracts, change pricing, fire staff, delete data, close store |
| **stock** | **Place buy/sell orders**, take profit / cut loss, transfer between accounts |
| **personal** | Investment decisions, parenting decisions, negotiation with anyone |

## Zone Priority Rules

1. **Default zone for every new task = 🟡** — agent self-demotes to 🟢 after proving safety across multiple runs
2. **When in doubt → move DOWN one zone** (🟢→🟡→🟠→🔴)
3. **User can promote** by saying "lần sau tự làm luôn" / "khỏi hỏi mấy cái này" → agent moves task to 🟢
4. **Each skill / cron job must have an assigned zone** — verify zone before executing
5. **Regular zone review** — if a task keeps landing in wrong zone → update SOUL.md

## Placement in SOUL.md

Insert as a new sub-section after Core Rules table. Recommended heading for cross-profile consistency:

```
## [§N.] DELEGATION ZONES — 4 mức tự động 🟢🟡🟠🔴

> Default = 🟡. Nghi ngờ → xuống zone thấp hơn.
```

## Verification After Changes

When modifying SOUL.md delegation zones across multiple profiles:

1. **Per-profile checklist:**
   - All 4 zones present with profile-specific examples
   - Zone Priority Rules present
   - Original SOUL.md content preserved (no accidental overwrite)
   - Table pipe counts match (no broken tables)
   - Section numbering consistent (if renumbering was needed)

2. **Cross-profile consistency:**
   - Same zone semantics (🟢 = no approval, 🟡 = approve, 🟠 = remind, 🔴 = never)
   - Profile-specific examples match domain
   - Zone Rules common across all profiles

3. **Ad-hoc verification script pattern** (for temp use):
   ```python
   # For each SOUL.md, regex-check: zone headers exist, priority rules exist,
   # original sections preserved, table structure intact
   ```

## Anti-Patterns

- 🚫 **Setting everything to 🟢** — agent will overstep and erode user trust
- 🚫 **Setting everything to 🟡** — agent becomes useless, user approves every trivial thing
- 🚫 **No default zone** — agent has no fallback when unsure; will guess wrong
- 🚫 **Assigning 🔴 to reversible tasks** — excessive friction. Let the user promote tasks they're comfortable with
- 🚫 **Forgetting zone during skill/cron creation** — a cron job without zone can execute 🟡/🔴 work autonomously
