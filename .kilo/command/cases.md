---
model: deepseek-obsidian/deepseek-v4-pro
description: "Case management (list/detail/close/new) adapted for ORION+Deepseek toolchain. Personal_OS: MCP replaced with Python scripts."
updated: 2026-06-02
---

# /cases
# v3.1 | 2026-05-31
# PURPOSE: List and manage active case threads. **Files = source of truth. ACTIVE_CASES_INDEX.md = derived view (auto-validated).**
# KEY CHANGES v2.0->v3.0:
#   - FIRST PRINCIPLE FIX: ACTIVE_CASES_INDEX.md is now a DERIVED view from files on disk, not an independent record.
#   - Added Pre-Flight Validation Gate (Section 0) — runs before EVERY operation, cross-refs index vs actual files, auto-repairs orphans.
#   - Added /cases validate subcommand — manual validation + repair.
#   - Step 1 now derives case list from files on disk, not from the index.
#   - Step 6A + Step 8A both auto-validate after mutate.
# KEY CHANGES v1.8->v2.0 (retained):
#   - Added frontmatter with model: deepseek-obsidian/deepseek-v4-pro
#   - Explicit tool call references: list_files(), read_file(), write_to_file(), execute_command()
#   - Calendar: uses push_gcal.py (Google Service Account)
#   - Slack: uses notify_slack.py (webhook)

## Config

`
BRAIN_DUMP_CHANNEL: C0B3VU8L0G5  (Warren_Life Slack #brain-dump)
CALENDAR_SCRIPT: python personal_vault/scripts/push_gcal.py
SLACK_NOTIFY_SCRIPT: python personal_vault/scripts/notify_slack.py
`

## Usage

`
/cases                  # list all OPEN cases — derived from files, validated against index
/cases {keyword}        # view full timeline — fuzzy match keyword vs case names
/cases close {keyword}  # close case — fuzzy match, confirm before execute
/cases new {keyword(s)} # create new case — generate slug from keywords
/cases validate         # cross-ref index vs actual files, report + auto-repair inconsistencies
`

**From Slack brain dump (no need to open vault):**
`
[new case: dispute Lys]       -> create new case about dispute/Lys
[close: dispute]              -> find case related to "dispute", confirm then close
`

---

## Section 0 — PRE-FLIGHT VALIDATION GATE (mandatory — runs at start of every operation)

> **First-principle rule:** Files in _cases/{active,closed}/ = source of truth. {ACTIVE,CLOSED}_CASES_INDEX.md = derived caches.
> If index vs files mismatch -> auto-repair before proceeding. Do not ask Warren — fix silent.
>
> **Encoding rule:** All .md file write/edit operations MUST use Kilo edit/write tool. Do not use execute_command + PowerShell
> (Set-Content/Out-File) because PowerShell corrupts UTF-8 Vietnamese characters. Exception: mkdir + move file (must use PS).

**ORION tool:**
`
list_files(path="_cases/active/")
list_files(path="_cases/closed/")         # validate closed index too
read_file(path="_cases/ACTIVE_CASES_INDEX.md")
read_file(path="_cases/closed/CLOSED_CASES_INDEX.md")
`

### Step 0.1 — Cross-reference (BOTH indexes)

1. list_files("_cases/active/") -> get all .md filenames -> active slugs
2. list_files recursive "_cases/closed/" -> get all .md filenames under closed subdirs -> closed slugs
3. Parse ACTIVE_CASES_INDEX.md table rows:
   - Extract slug from File column (wikilink format [[_cases/active/{slug}]])
   - Separator row (exact match): `| ---------- | -------- | ---------------------------- | ------------- | -------------------------------------------------------------------------- | ---------- | ------------------------------------------------------ |`
4. Parse CLOSED_CASES_INDEX.md table rows:
   - Extract slug from File column (wikilink format [[_cases/closed/{YYYY-MM}/{slug}]])
   - Separator row (exact match): `|---|---|---|---|---|---|`
5. Compare for EACH index:
   - **Orphans (index row — no file):** slug in index table but NOT in files list
   - **Untracked (file — no index row):** slug in files list but NOT in index table

### Step 0.2 — Auto-repair (silent, do not ask Warren)

#### Active index
| Issue detected | Auto-fix |
|---|---|
| **Orphan row(s) found** | Delete orphan row from table. Tool: `edit(filePath=ACTIVE_CASES_INDEX.md, oldString=..., newString=...)`. Report: 🗑️ Removed N orphan active entries (no file found): [list slugs] |
| **Untracked file(s) found** | Read file -> extract frontmatter (opened, priority, domain, summary, follow_up) -> append row at top of table (after separator row). Tool: `edit(filePath=..., append pattern)`. Report: 📝 Added N untracked files to active index: [list slugs] |
| **Both** | Do both above, report once |
| **No issues** | Silent — skip. |

#### Closed index
| Issue detected | Auto-fix |
|---|---|
| **Orphan row(s) found** | Delete orphan row from table. Report: 🗑️ Removed N orphan closed index entries (no file found): [list slugs] |
| **Untracked file(s) found** | Read file -> extract frontmatter (closed, type, slug, domain, decision) -> append row. Report: 📝 Added N untracked files to closed index: [list slugs] |
| **Both** | Do both, 1 message |

### Step 0.3 — Sort index tables

After fixing, re-sort table rows: newest Opened/Closed date on top. If same date -> higher Priority first (HIGH > MEDIUM > LOW).

### Step 0.4 — Update last_updated

Find last_updated line in frontmatter of both index files -> update to today.

> **Reasoning:** Without a validation gate, both indexes will drift apart — this was the root cause of the 2026-05-29 bug (lys-dispute-pickup + 3 other orphan entries). This gate runs at the start of EVERY operation so inconsistency has no chance to persist.

---

## Step 1 — List OPEN cases

**ORION tool:**
`
list_files(path="_cases/active/")
`

Read all files in _cases/active/. For each file — use read_file():
1. list_files(path="_cases/active/") -> get all .md files
2. For each file: read_file(path="_cases/active/{filename}") -> extract frontmatter
3. Extract: Status, Opened date, Stakeholders, Domain, last timeline entry date
4. Calculate days open = today - Opened date

> **Note:** Use files as source of truth. Do not use index to list. Index is only cache for /query.

Output format:

`
━━━━━━━━━━━━━━━━━━━━━━━
🗂️ ACTIVE CASES ({n} open)
━━━━━━━━━━━━━━━━━━━━━━━

[{slug}] {summary 1 sentence}
  📅 Opened: {date} ({n} days ago)
  👤 Stakeholders: {names}
  🔄 Last update: {date of last timeline entry}
  📌 Open items: {n} unchecked

⚠️ STALE (>30 days no update): [{slug}] — last touched {date}
━━━━━━━━━━━━━━━━━━━━━━━
`

If no cases -> "No open cases."

---

## Step 2 — /cases {keyword}: view full case

**ORION tool:**
`
read_file(path="_cases/active/{matched-filename}")
`

Fuzzy match keyword vs filename slug + Keywords field (from Step 1 list results).
If match 1 case -> read_file(path="_cases/active/{filename}") and print full content.
If match multiple cases -> list them, Warren picks number -> read selected file.

---

## Step 3 — /cases close {keyword}

1. **Run Section 0 (Pre-Flight Validation Gate)** — ensure index is clean before close.
2. Fuzzy match keyword vs _cases/active/ filenames + Keywords fields.
3. Confirm with Warren: "Close case **{matched-slug}**? [y/n]" — wait for confirm.
4. (Personal_OS: no project auto-detection — all cases close the same way)
5. If y -> ask Closing Record (1 time, all at once):
   `
   Fill in closing record to save to second brain:
   (a) Type: family / health / trading / finance / relationship / legal / growth
   (b) Outcome: resolved / unresolved / escalated
   (c) Decision Made: [final decision — 1-2 sentences, MANDATORY]
   (d) Lessons Learned: [optional — type "skip" if none]
   `
   - ORION drafts (c) from case timeline content — Warren only approves/edits.
   - (a) and (b): if Warren types ordinal numbers instead of text -> auto-convert:
     Type: family=1, health=2, trading=3, finance=4, relationship=5, legal=6, growth=7
     Outcome: resolved=1, unresolved=2, escalated=3
   - (c) mandatory — ORION drafts from timeline then asks: "Decision Made — my draft: '[draft]'. OK? [y/edit]"
     If Warren types "skip" 1st time -> remind: "Decision Made is the most important field for second brain. Even 1 short sentence works."
     If Warren types "skip" 2nd time -> ORION uses draft automatically, append with tag [auto-drafted]. Do not block close, do not leave blank.
6. Append Closing Record at end of file before move:
   `markdown
   ---
   ## Closing Record
   - **Closed:** {YYYY-MM-DD}
   - **Type:** {type}
   - **Outcome:** {outcome}
   - **Decision Made:** {decision}
   - **Lessons Learned:** {lessons | "—"}
   `
6B. **Ingest gate** — auto after Closing Record is written:
   - Fire conditions: Lessons Learned ≠ "—" AND Decision Made ≠ [auto-drafted]
   - If conditions met -> prompt Warren:
     "⚠️ Case [{slug}] has digest-worthy insight: [{Decision Made first 60 chars}]. Want to /ingest? (y/skip)"
   - Warren "y" -> ORION suggests: /ingest {slug}.md {inferred_domain} and runs immediately
   - Warren "skip" or no reply -> continue Step 6 normally. Silent.
   - Do not fire if: Lessons Learned = "—" OR Decision Made = [auto-drafted]

7. Update frontmatter:
   - Find status: OPEN -> replace with status: CLOSED
   - Append 2 new fields to end of frontmatter block (before closing ---):
     closed: {YYYY-MM-DD}
     type: {type}
   - If file is legacy (no type: field present) -> append normally, no separate migration needed.
8. **Knowledge routing (auto after writing Closing Record):**

   | Type | Action after close |
   |---|---|
   | family / health / relationship | Closing Record is sufficient. Archive case. Do not append to any log. |
   | trading / finance / legal | Append to 30_KNOWLEDGE_BASE/wiki/DECISION_LOG.md (newest on top): ## {YYYY-MM-DD} — {Decision Made}\n- Type: {type} \| Outcome: {outcome}\n- Lessons: {lessons}\n- Source: case _cases/closed/{YYYY-MM}/{filename} |
   | growth | Closing Record is sufficient. Optionally append to _growth/_INDEX.md if insight worth capturing. |

9. **Append into _cases/closed/CLOSED_CASES_INDEX.md** (newest on top -- insert row after separator row):
   **ORION tool:** edit(filePath, oldString=separatorRow, newString=separatorRow + newline + newRow)
   **Separator row (exact match):** `|---|---|---|---|---|---|`
   ```
   New row: | {YYYY-MM-DD} | {type} | {slug} | {domain} | {Decision Made first 100 chars} | [[_cases/closed/{YYYY-MM}/{slug}]] |
   ```
   Domain = value from frontmatter domain field.
   If CLOSED_CASES_INDEX.md does not exist, create with header before append:
   ```
   | Closed | Type | Slug | Domain | Summary | File |
   |---|---|---|---|---|---|---|
   ```
   **Encoding safety:** Use Kilo edit tool (NOT Set-Content).
10. **Remove from _cases/ACTIVE_CASES_INDEX.md** -- find table row with slug = {matched-slug} and delete.
    **ORION tool:** edit(filePath, oldString=fullRowText, newString="") -- use exact row string including leading/trailing |
    **Separator row (exact match):** `| ---------- | -------- | ---------------------------- | ------------- | -------------------------------------------------------------------------- | ---------- | ------------------------------------------------------ |`
    After removal, **run Section 0** to validate index is clean after close.
    Format: | {YYYY-MM-DD} | {priority} | {slug} | {domain} | {summary} | {follow_up} | [[_cases/active/{filename}]] |
    If ACTIVE_CASES_INDEX.md does not exist, silent (fallback, created if needed).
11. Create folder _cases/closed/{YYYY-MM}/ if not yet exists — do not ask Warren.
    **ORION tool:**
    `
    execute_command(command="mkdir \"_cases\\closed\\{YYYY-MM}\"")
    `
    **Fallback if mkdir fail:** use full path:
    `
    execute_command(command="New-Item -ItemType Directory -Path \"_cases\\closed\\{YYYY-MM}\" -Force | Out-Null")
    `
12. Move file to _cases/closed/{YYYY-MM}/.
    **Critical order:** Step 12 is the LAST STEP of the close flow — all writes (Closing Record, frontmatter, indexes) must complete BEFORE the move. If move fails, file stays in _cases/active/, Section 0 will re-add to index -> recoverable.
    **ORION tool:**
    `
    execute_command(command="Move-Item -LiteralPath \"_cases\\active\\{old_filename}\" -Destination \"_cases\\closed\\{YYYY-MM}\\{old_filename}\" -Force")
    `
    **Fallback if Move-Item fails (file lock):** retry 1 time after 500ms. If still fails -> tell Warren: "⚠️ File move failed: [error]. File remains in _cases/active/. Run /cases close {slug} again to retry."
13. Confirm with Closing Record summary:
    "✅ Case [{slug}] closed.
     Type={type} | Outcome={outcome} | Decision Made=✓
     -> _cases/closed/{YYYY-MM}/{filename}
     -> CLOSED_CASES_INDEX.md updated
     -> ACTIVE_CASES_INDEX.md cleaned + validated
     [if trading/finance/legal] -> DECISION_LOG.md updated"

---

## Step 4 — /cases new {keyword(s)}

1. **Run Section 0 (Pre-Flight Validation Gate)** — ensure index is clean before creating.
2. **Slug rule:** Remove Vietnamese diacritics, lowercase, hyphens, max 4 words, do NOT add custom suffixes.
   E.g.: "Hân nghỉ việc" -> han-nghi-viec | "dispute Lys" -> tranh-lys
3. Ask Warren 3 questions (all at once, not one by one):
   - (a) Summary 1 sentence?
   - (b) Stakeholders?
   - (c) Any deadline / follow-up date? (type date or "no")
4. If Warren enters natural date ("next Monday"), convert to ISO and confirm: "I understand this as {YYYY-MM-DD}. Correct?" -- wait for Warren confirmation. Prefer ISO date input for reliability.
5. Keywords = what Warren types after new — auto-filled into **Keywords** field.
6. Create file _cases/active/{YYYY-MM}_{slug}.md with standard template (includes **Follow-up:** field).
   **ORION tool:**
   `
   write_to_file(path="_cases/active/{YYYY-MM}_{slug}.md", content="...")
   `
7. **Calendar push** (based on answer (c)):
   - If date given -> create Google Calendar all-day event:
     - summary: "🗂️ Follow-up: {slug}"
     - date: date confirmed in step 4
     - description: Summary from (a) + file path
   - **Calendar script:**
     `
     execute_command(command="python personal_vault/scripts/push_gcal.py --summary \"🗂️ Follow-up: {slug}\" --date YYYY-MM-DD --tags \"#case\" --priority high")
     `
   - **If Calendar script fails:**
     - Write ⚠️ Calendar push failed to case file header (use apply_diff)
     - Send Slack DM: use notify_slack.py:
       `execute_command(command="python personal_vault/scripts/notify_slack.py \"⚠️ Case [{slug}] created OK but Calendar push failed. Set manually for {date}.\"")`
     - Do NOT block case file creation — proceed despite Calendar fail.
   - If Warren typed "no" -> skip Calendar.

8. **Append into _cases/ACTIVE_CASES_INDEX.md:**
   **ORION tool:** edit(filePath, oldString=separatorRow, newString=separatorRow + newline + newRow)
   **Separator row (exact match):** `| ---------- | -------- | ---------------------------- | ------------- | -------------------------------------------------------------------------- | ---------- | ------------------------------------------------------ |`
   ```
   New row (newest on top -- insert after separator): | {YYYY-MM-DD} | {priority} | {slug} | {domain} | {summary} | {follow_up} | [[_cases/active/{filename}]] |
   ```
   Domain = inferred from keywords.
   If ACTIVE_CASES_INDEX.md does not exist, create:
   ```
   | Opened | Priority | Slug | Domain | Summary | Follow-up | File |
   |---|---|---|---|---|---|---|
   ```
   **After append -> run Section 0 (validate + sort)** to ensure index consistent.
9. Confirm: "Case [{slug}] created -> _cases/active/{filename}" + (if Calendar) "📅 Reminder set: {date}"

---

## Step 5 — /cases validate (manual validation)

**Use when:** Warren suspects index drift, or after batch operations.

1. Run Section 0 (Pre-Flight Validation Gate) — full orphan detection + untracked detection + auto-repair
2. Output summary:
   `
   ━━━━━━━━━━━━━━━━━━━━━━━
   ✅ CASES VALIDATION
   ━━━━━━━━━━━━━━━━━━━━━━━
   Files on disk: {n}
   Index entries: {n}
   Orphans removed: {n}
   Untracked added: {n}
   ━━━━━━━━━━━━━━━━━━━━━━━
   Index is now consistent with actual files ✅
   `

---

## Rules

- **Source of truth:** Files in _cases/active/. The index is a DERIVED cache for query speed.
- **Validation runs first:** Every /cases operation starts with Section 0 (Pre-Flight Validation Gate).
- Auto-repair is silent — do not ask Warren unless there's a conflict that cannot be auto-resolved.
- Only read _cases/active/ when listing. Do not read _cases/closed/ unless Warren explicitly asks.
- Fuzzy match: keyword compared against filename slug + **Keywords** field. "tranh" matches "Lys-tranh-return". Ambiguous -> list + ask Warren to pick number.
- Stale = OPEN > 30 days without new timeline entry -> flag but do not auto-close.
- Case file = 1 source of truth for that thread. Do not duplicate into journal.

---

**v3.1 | 2026-05-31 | Personal_OS adaptation: MCP replaced with push_gcal.py + notify_slack.py. Domain-based case types. No project auto-detection.**
