---
description: "Morning brief for L'Usine ops -- daily or weekly snapshot"
updated: 2026-06-02
---

# /ops-morning-brief — Hermes+Deepseek Adaptation
# v2.0 | 2026-05-25
# PURPOSE: Daily ops brief + weekly snapshot. Ported from Claude Code toolchain to Hermes+Deepseek.
# KEY CHANGES v1→v2:
#   - Claude Code Grep → Hermes search_files()
#   - Claude Code Glob → Hermes list_files()
#   - Claude Code Bash (git) → Hermes execute_command() with [cd vault/] prefix
#   - Claude Code memory paths → vault/projects/ native files
#   - Slack DM step → REMOVED
#   - Scheduled agent (06:00 GMT+7) → ON-DEMAND only

If args contain "7d" or "week" or "tuần":
  Execute WEEKLY MODE below.
Else:
  Execute DAILY MODE below.

---
## DAILY MODE (default — no args)

**Step 0 — Duplicate guard:**
```
search_files(
  regex="^## $CURRENT_DATE",
  file_pattern="morning_briefs_log.md",
  path="10_OPERATION_DATA/morning_briefs"
)
```
If match → output `"⚠️ Today's brief ($CURRENT_DATE) already ran. Re-run? [y/N]"` and wait for confirm.
If not confirmed → STOP. Do not run brief, do not waste tokens.

Execute ALL steps before outputting anything:

**Step 1 — Check recent file changes:**
```
execute_command(
  "cd /d \"C:\\Users\\khoans\\Documents\\Warren_OS_Local\\vault\" && git diff --name-only HEAD~1 HEAD"
)
```
Filter to operational files only (exclude `.claude/`, `30_KNOWLEDGE_BASE/`, `CLAUDE.md`, `*.canvas`). For each remaining file: `read_file(path="...", limit=20)` and write a 1-line summary. If 0 operational files modified → skip section.

**Step 2 — Open decisions — 2 sources only:**
```
(a) read_file(path="00_CORE_LOGIC/CONTEXT.md")
    → extract rows from section "ACTIVE DECISIONS"
    → Status = Unresolved/Pending only
    (table format: | date | decision | status | next step |)

(b) read_file(path="_inbox/tasks.md")
    AND list_files(path="_cases/active", recursive=false)
    → for cases: newest files first, cap 3 items → read first 10 lines (frontmatter only) each.
    → if cases >3 items: "+N more in _cases/active/"

(c) Monitor overdue scan → see Step 6 below (single source for all [monitor] detection).
```
Do NOT grep `[ ]` in pulse logs (covered by Step 5).

**Step 3 — Active project blockers (vault-native, NOT Claude Code memory):**
```
read_file(path="projects/LU5_Reallocation/_INDEX.md")
    → extract lines with "blocker", "blocked", "chờ"
read_file(path="projects/LU5_Reallocation/_DECISION_LOG.md")
    → extract latest 3 unresolved decisions
```
If a file cannot be read → show `⚠️ [file name] not found` in Today's focus, do not skip silently.
(Update this list when active projects change.)

**Step 4 — URGENT scan:**
```
search_files(
  regex="URGENT|urgent|⚠️",
  file_pattern="*.md",
  path="10_OPERATION_DATA"
)
```
Filter to files modified in last 24h (use same filter as Step 1). Do NOT grep `hôm nay` — use ⚠️ as the single urgent convention.

**Step 5 — Smart log scan (skip unchanged logs to save tokens):**
```
execute_command(
  "cd /d \"C:\\Users\\khoans\\Documents\\Warren_OS_Local\\vault\" && git log --since='3 days ago' --name-only --pretty=format:"
)
```
Collect changed file paths matching `10_OPERATION_DATA/0[0-9]_*.md`. Deduplicate.

- **Changed logs**: For each changed log file:
  ```
  search_files(
    regex="^## 202",
    file_pattern="[FILENAME].md",
    path="10_OPERATION_DATA"
  )
  ```
  → parse result for most recent `## 202` line number → `read_file(path="...", offset=LINE_NUMBER, limit=40)`
  Extract: open `[ ]` action items + any 🔴/🟡 flags + underperforming signals (LTO <70% target, rating <4.3, COGS net impact negative, resign/exit spikes).

- **Unchanged logs**: Reuse flags from previous brief entry:
  ```
  search_files(
    regex="^## $PREVIOUS_BRIEF_DATE",
    file_pattern="morning_briefs_log.md",
    path="10_OPERATION_DATA/morning_briefs"
  )
  ```
  → parse line number → `read_file(path="...", offset=LINE_NUMBER, limit=80)`
  → extract only the Weekly Pulse section flags. Prefix with `(unchanged)` in output.

- If git log returns 0 changed logs → reuse ALL flags from previous brief + note `📊 No log updates since last brief — data below is from {previous date}.`

- If search_files returns no match for a log → skip silently.
- If log file cannot be read → show `⚠️ [log name] missing` in Weekly Pulse section.

**Step 6 — MONITOR overdue scan:**
```
search_files(
  regex="\[monitor\]",
  file_pattern="*.md",
  path="_inbox"
)
```
→ For each match, extract created date and determine if overdue per Step 2(c) rules.
Include results in ⚠️ URGENT section as 🟡 flags.

Output ONLY this format — no preamble:

📋 MORNING BRIEF — $CURRENT_DATE

⚠️ URGENT (need handling today)
- [item from Step 4 if any]
- [🟡 monitor overdue items from Step 6 if any]
- 🔴 Pulse flags: [list all 🔴 flags extracted from Step 5 — COL%, GrabFood, Google Reviews, LTO, Revenue. Format: "[metric] [store if applicable]: [value] ([threshold])". If no 🔴 flags → "✅ Pulse normal — no 🔴 flags"]

🔴 Decisions pending
- [open decision + 1-line context, or "None"]

📥 New notes since yesterday
- [filename]: [1-line summary]

📌 Today's focus
- [active project + blocker, or "No blockers"]

---

📊 WEEKLY PULSE (latest week data)

💰 Revenue
- ALL: [Revenue] | W/W: [%] | Y/Y: [%] | Covers: [X] | Avg/Cover: [X]
- LU3: [Revenue] | LU5: [Revenue] | LU7: [Revenue]
- MTD: [MTD ALL] ([Y/Y%]) | Calendar: [X%]
- Flag: [🔴 if any store W/W < -15%, or "OK"]

👥 HR
- Headcount gap: [summary gap vs approved, which store critical]
- Movements: [join/exit/offer this week]
- Actions open: [list of [ ] unchecked]
- Flag: [🔴/🟡 if any, or "OK"]

🧾 COGS
- SKU changes: [X up / X down]
- Net impact: [positive / negative / neutral + estimated %]
- Actions open: [list of [ ] unchecked, or "None"]
- Flag: [🔴 if net impact significantly negative, or "OK"]

🎯 LTO
- Performance: [X% target total / which store performing / which store below 70%]
- Customer feedback: [notable pattern]
- Actions open: [list of [ ] unchecked, or "None"]
- Flag: [🔴 if <60% target, 🟡 if 60–70%, or "OK"]

⭐ Google Reviews
- Rating: LU3 X.X ★ | LU5 X.X ★ | LU7 X.X ★
- Pattern: [positive] / [negative]
- Unreplied: [X reviews or "None"]
- Flag: [🔴 if any store <4.3, or "OK"]

---

## SAVE STEP

After outputting the brief, prepend to `10_OPERATION_DATA/morning_briefs/morning_briefs_log.md`:

**How to prepend (Hermes method):**
```
1. read_file(path="10_OPERATION_DATA/morning_briefs/morning_briefs_log.md")
   → old_content = result
2. Find position after header:
   Find the second `---` line in the file (first after subtitle).
   Or use string operation: header is everything before the first `---\n\n`.
3. Construct:
   new_entry = "## $CURRENT_DATE\n\n[BRIEF OUTPUT ABOVE]\n\n---\n\n"
   # Insert new_entry AFTER header + ---, BEFORE oldest entry
   # Example: header = "# Morning Briefs Log...\n_1 file..._\n\n---\n\n"
   full_content = header + "---\n\n" + new_entry + body
4. write_to_file(path="10_OPERATION_DATA/morning_briefs/morning_briefs_log.md", content=full_content)
```

If file doesn't exist: create new with header:
```
# Morning Briefs Log — L'Usine
_1 file growing. Newest entry on top. On-demand (Hermes+Deepseek)._

---
```

Do not create new file per day. Do not overwrite. Always keep header at top, prepend new entry right after header, before oldest entry → newest on top.

---

## WEEKLY MODE (/ops-morning-brief 7d)

**Step 1 — Get git log for last 7 days:**
```
execute_command(
  "cd /d \"C:\\Users\\khoans\\Documents\\Warren_OS_Local\\vault\" && git log --since='7 days ago' --pretty=format:\"COMMIT|||%h|||%ad|||%s\" --date=short --name-only"
)
```

**Step 2 — Classify commits** into 3 buckets (case-insensitive regex):

- **CONTENT** — `Ingest:|Query →` — new wiki data/analysis. Show full detail.
- **ACTIVITY** — `feat:|fix:|chore:|update:|auto:|case(` — vault/command changes. Show count only. (e.g. `case(lu3):`, `feat(process-notes):`)
- **NOISE** — `vault backup:|auto-git` — automated housekeeping. Skip entirely.

Any commit not matching CONTENT or NOISE → default to ACTIVITY.
If a commit matches both CONTENT and NOISE → CONTENT wins.

**CONTENT commits only:** extract changed file paths, filter to paths starting with `30_KNOWLEDGE_BASE/wiki/` only. Domain = 4th path segment (e.g. `30_KNOWLEDGE_BASE/wiki/labour_costs/file.md` → domain `labour_costs`). Ignore paths under `.claude/`, `_cases/`, `_journal/`, `_inbox/` in all domain counts.

**DOMAIN ACTIVITY:** count unique wiki files touched across CONTENT + ACTIVITY commits (same path filter: `30_KNOWLEDGE_BASE/wiki/` only, exclude `archive/`).

**Total wiki count:**
```
list_files(path="30_KNOWLEDGE_BASE/wiki", recursive=true)
```
→ Filter results: exclude any path containing `/archive/` → count remaining `.md` files = live_total. Do not hardcode.

Output ONLY this format — no preamble:

📅 WEEKLY SNAPSHOT — last 7 days ($CURRENT_DATE)

📥 DATA INGESTED ([N] ingest commits)
- [DATE] [commit subject — truncate at 70 chars]
  → [wiki file 1]
  → [wiki file 2] (list max 3, then "+N more")
- [repeat per ingest commit, newest first]
- (no ingest this week) — if zero

🔧 ACTIVITY ([N] commits — commands, cases, scripts)

📊 DOMAIN ACTIVITY (wiki files only)
- [domain]: [N] files touched  ← sort descending
- [domain]: [N] files touched
- ...
- (no wiki activity this week) — if zero wiki files touched
- Total: [N] unique wiki files / [live_total] total (excl. archive)

⚠️ OPEN ACTIONS (from pulse files)
- Scan all `10_OPERATION_DATA/0[0-9]_*.md`:
  ```
  For each log file in 10_OPERATION_DATA matching 0[0-9]_*.md:
    1. search_files(regex="^## 202", file_pattern="[FILENAME].md", path="10_OPERATION_DATA")
       → parse result for most recent `## 202` line number
    2. read_file(path="10_OPERATION_DATA/[FILENAME].md", offset=LINE_NUMBER, limit=80)
    3. Extract open `[ ]` items
  ```
  If search_files returns no match → skip silently. Show results or "None".

---

### WEEKLY SAVE STEP

**Step 1 — Prepend to weekly_briefs_log.md (rolling):**
Prepend to `10_OPERATION_DATA/morning_briefs/weekly_briefs_log.md`:

**How to prepend (Hermes method):**
```
1. read_file(path="10_OPERATION_DATA/morning_briefs/weekly_briefs_log.md")
   → old_content = result
2. Find position after header (same as daily mode):
   header is everything before the first `---\n\n` (after frontmatter + title).
3. Construct:
   new_entry = "## [YYYY-WXX] | [DATE_START] → [DATE_END]\n_Generated: [CURRENT_DATE]_\n\n[BRIEF OUTPUT ABOVE]\n\n---\n\n"
   # Insert new_entry AFTER header ---, BEFORE oldest entry
   full_content = header + "---\n\n" + new_entry + body
4. write_to_file(path="10_OPERATION_DATA/morning_briefs/weekly_briefs_log.md", content=full_content)
```

Do not overwrite. Always keep header at top, prepend new entry right after header, before oldest entry → newest on top.
If file doesn't exist: create new with header:
```
---
type: weekly_briefs_log
status: active
---

# Weekly Briefs Log — L'Usine
_1 file growing. Newest entry on top. On-demand (Hermes+Deepseek)._

---
```

**Step 2 — Commit (git):**
```
execute_command(
  "cd /d \"C:\\Users\\khoans\\Documents\\Warren_OS_Local\\vault\" && git add 10_OPERATION_DATA/morning_briefs/weekly_briefs_log.md && git commit -m \"feat(weekly-brief): W[XX] 7-day summary [DATE_END]\" && git log --oneline -1"
)
```

> **Slack DM step has been REMOVED** — Hermes+Deepseek does not have Slack MCP integration.
> Weekly brief is on-demand only (no scheduled trigger — Claude Code's `claude.ai/code/routines/` is not available in Hermes).

### Final step — SYSTEM_VIEW Full Refresh

After brief is generated and saved:
1. Read ALL data logs from 10_OPERATION_DATA/ (revenue, COL, reviews, LTO, GrabFood)
2. Read ALL active cases from _cases/active/
3. Write full SYSTEM_VIEW.md - update EVERY section:
   - "## 🎯 TODAY" - refresh from cases
   - "## 💰 REVENUE" - latest week
   - "## 👥 LABOUR" - latest COL/CPH
   - "## ⭐ GOOGLE REVIEWS" - latest week
   - "## 🎯 LTO" - latest performance
   - "## 🛵 GRABFOOD" - if updated
   - "## 📋 P&L BUDGET" - if updated
   - "## 🔴 ACTIVE CASES" - fresh from disk
   - "## 📊 TREND" - add latest week row
4. Update last_updated in frontmatter to today



---

## FEEDBACK MECHANISM (v2.1 | 2026-05-31)

> **Ref:** [[Feedback_Pair_Pattern]]

**Snooze rule for repeated flags:** Flags appearing unchanged in 2+ consecutive briefs are auto-collapsed with `<!-- fb:[WATCH] @YYYY-MM-DD -->` marker. Warren can promote back by removing the marker.

**Permanent skip:** Flags marked `[NOISE]` 2 consecutive times → Hermes auto-skips on all future briefs.

**Weekly checkpoint:** Monday `/ops-context-update` includes batch review of all snoozed/active flags.
