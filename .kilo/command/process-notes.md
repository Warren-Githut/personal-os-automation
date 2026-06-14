---
updated: 2026-06-02
---

# /process-notes
# v3.2 | 2026-05-31
# PURPOSE: Fetch messages from Slack #brain-dump, classify, route to correct destination, save as Markdown notes.
# KEY CHANGES v3.1->v3.2:
#   - Removed ALL Slack MCP references (fetch, send, read-file) - replaced with Python scripts
#   - Slack fetch: invoke_mcp(SLACK_READ_CHANNEL_MCP_TOOL) -> fetch_slack_notes.py (Python SDK)
#   - Slack DM: invoke_mcp(SLACK_SEND_MESSAGE_MCP_TOOL) -> notify_slack.py (webhook/bot)
#   - Step 0/1/2/6b/7: all Slack MCP tool calls replaced with Python scripts
# KEY CHANGES v3.0->v3.1:
#   - Replaced Calendar MCP with push_gcal.py (Service Account)
# KEY CHANGES v2.7.1->v3.0:
#   - Added frontmatter with model: hermes-deepseek-reasoner

## Config
```
BRAIN_DUMP_CHANNEL: C0B3VU8L0G5  (LU_workspace #brain-dump)
SLACK_FETCH_SCRIPT: python vault/scripts/fetch_slack_notes.py
SLACK_NOTIFY_SCRIPT: python vault/scripts/notify_slack.py
CALENDAR_METHOD: python vault/scripts/push_gcal.py
  # Env vars needed:
  #   SLACK_BOT_TOKEN_LIFE - Warren_Life workspace bot token (fetch)
  #   SLACK_BOT_TOKEN_LU   - LU_workspace bot token (fetch)
  #   SLACK_WEBHOOK_URL    - Incoming Webhook (notify/fallback)
  #   GOOGLE_SA_CREDENTIALS - Google Service Account JSON (push_gcal)
```

Fetch messages from Slack #brain-dump, classify, route to correct destination, and save as Markdown notes.
Display the entire batch plan once — Warren confirms one time only.

## Usage
```
/process-notes           # fetch from .last_confirmed (or 24h UTC if none exists)
/process-notes --hours 48
```

## Steps

$ARGUMENTS

---

### Step 0 — Map Config UUIDs (0 calls — local lookup)

No need for ToolSearch anymore. UUIDs are pre-defined in the Config block as separate variables:
- `SLACK_READ_CHANNEL_MCP_TOOL`
- `SLACK_SEND_MESSAGE_MCP_TOOL`
- `SLACK_READ_FILE_MCP_TOOL`

Calendar does NOT use MCP — uses script `push_gcal.py` (Google Service Account, see Step 6b).
Use Slack variables directly in `invoke_mcp(tool=..., params=...)` in subsequent steps.
If MCP tool call fails → fallback: notify Warren + continue skipping that tool. Do not stop the run.

---

### Step 1 — Fetch messages

**Determine `oldest` timestamp:**

**Parse timestamp from file:** When reading line 1 of `.last_fetch` or `.last_confirmed`, parse using `int(float(value.strip()))` (use `read_file` → line 1 → parse value → `int(Number(value))` in JS or `int(float(value.strip()))` in Python). Handle both int strings and legacy float strings (backward compatible).

1. Read `_inbox/.last_fetch` and `_inbox/.last_confirmed` (if they exist).
   - Both exist AND `.last_fetch > .last_confirmed` → interrupted run → ask Warren:
     `⚠️ Previous run was interrupted at [ISO from .last_fetch]. Re-process from there? (fetch: T1, confirmed: T2) [y/n]`
     - `[y]` → use `.last_fetch` | `[n]` → use `.last_confirmed`
   - Both exist AND `.last_confirmed >= .last_fetch` → normal completion → use `.last_confirmed`.
      ⚠️ If .last_confirmed is > 24h ago -> note the delta for display in Step 5 (non-blocking). Continue fetch.
   - Only `.last_confirmed` → use as `oldest`
   - Only `.last_fetch` (no `.last_confirmed`) → ask Warren:
     `⚠️ .last_fetch exists at [ISO] but no .last_confirmed — previous run crashed before confirm. Fetch from there? [y/n]`
     - `[y]` → use `.last_fetch` | `[n]` → `oldest = now - 24h`
   - No files exist → `oldest = now - 24h` (UTC Unix timestamp)
2. `--hours N` → `oldest = now - N hours` (UTC). Skip interrupt check. Still write `.last_fetch`.
3. Write `.last_fetch` right before calling Slack using `write_to_file(path="_inbox/.last_fetch", content="{int(now)}\n# {ISO_8601_Vietnam} — fetch start")`
4. Call `invoke_mcp(tool=SLACK_READ_CHANNEL_MCP_TOOL, params={channel: BRAIN_DUMP_CHANNEL, oldest: oldest, ...})`. **If returns 0 messages** → do not write `.last_fetch` (call `write_to_file(path="_inbox/.last_fetch", content="")` to clear content or restore old value), notify "0 messages from [ISO] to now. If just posted — re-run with --hours 1 to verify.", stop.

**Call Slack MCP (with pagination loop):**
- Use `invoke_mcp(tool=SLACK_READ_CHANNEL_MCP_TOOL, params={channel: BRAIN_DUMP_CHANNEL, oldest: int(unix_timestamp_UTC), ...})`. If fail → fallback: notify Warren + use `read_file(path="_inbox/tasks.md")` to check recent tasks.
- Param `oldest = {int(unix_timestamp_UTC)}`. `--workspace W` → only fetch that one. Default: both.
- **Pagination:** If response has `cursor` → continue fetching with cursor until all pages exhausted. Combine all messages before processing.

---

### Step 2 — Process by message_type

**audio:** Script downloaded to `_inbox/voice/`. Run using `execute_command(command="python vault/scripts/process_voice.py \"{audio_path}\" --model small --delete-source", cwd="vault")`.
Read output from command result → use transcript as `text`. Delete `__tmp_*.md` after reading.

**text:** Use field `text` directly.

**attachment:** Use fields `filename`, `permalink`, `text` (caption, may be empty).

**If image** (extension: jpg, jpeg, png, heic, gif, webp, bmp):
1. Call `invoke_mcp(tool=SLACK_READ_FILE_MCP_TOOL, params={file_id: ..., url_private: ...})` with `url_private` (or `url_private_download`) from file object — do not use `permalink` (permalink is a web URL requiring browser auth, cannot be downloaded). If MCP fail → fallback: manual description from caption + filename.
2. Pass image to Claude vision — request brief description: what is the main content, any notable text/data points.
3. Create `text` for classify:
   ```
   [IMAGE: {filename}]({permalink})
   Vision: {description from Claude}
   Caption: {text if any}
   ```
4. **Continue normal classification** (Step 3 case detection + Step 4 classify) — do not route directly to Journal.
5. If `invoke_mcp(tool=SLACK_READ_FILE_MCP_TOOL, ...)` fails or vision fails → fallback: `[IMAGE: {filename} — vision unavailable]({permalink})`, route to Journal as before, add ⚠️ in summary.

**If other file** (pdf, doc, xlsx, etc.): Use fields `filename`, `permalink`, `text` (caption, may be empty).
Create `text` for classification step:
```
[ATTACHMENT: {filename} — {text}]({permalink})
```
If `text` empty: `[ATTACHMENT: {filename}]({permalink})`
Route directly → Journal (`_journal/YYYY-MM.md`), skip Step 3 case detection.

---

### Step 3 — Case detection (priority before classification)

#### Flow A — Warren explicit (prefix)

**Create new case** `[new case: {keyword(s)}]` or `[new case - {keyword(s)}]` (colon or dash, optional leading space, case-insensitive):
- Slug: remove diacritics, lowercase, hyphens, max 4 words, no auto-suffix.
- Ask 3 questions: (a) Summary 1 sentence? (b) Stakeholders? (c) Deadline/follow-up date?
- Create `_cases/active/YYYY-MM_{slug}.md`. Keywords = text after `[new case:`.
- Has date → push Calendar all-day event via `push_gcal.py`:
  ```bash
  python vault/scripts/push_gcal.py --summary "🗂️ Follow-up: {slug}" --date YYYY-MM-DD --tags "#case" --priority high
  ```
  Calendar fail → ⚠️ in case header + Slack DM.
- Natural language date ("next Monday") → convert to ISO + confirm before pushing.

**Close case** `[close: {keyword}]`:
- Fuzzy match keyword vs `_cases/active/`. Confirm: "Close case {slug}? [y/n]"
- Confirm → move to `_cases/closed/YYYY-MM/`, ask "Resolution 1 sentence?"
- Multiple matches → list them, Warren picks number.

No prefix → Flow B.

#### Flow B — Claude detect

Use `search_files(path="_cases/active/", regex="^\\*\\*Keywords:\\*\\*.*")` to get Keywords of each case (no full file read). Extract entities from message. Match:
- **HIGH** (2+ entities match) → flag in batch plan: `🗂️ Seems to belong to case [{slug}] — append? [Nc] or skip`
- **MOD** (1 entity) → route to journal normally, no suggestion
- **NONE** or folder empty or search_files returns 0 → route normally, no flag, no halt

Default if Warren doesn't reply `[Nc]` = journal. No silent merge.

---

### Step 3B — Classify + Detect domain (1 read pass)

#### Type:

| Type | Signs |
|------|----------|
| `decision` | specific numeric target, "decide", "from now on", "will do", conflict between 2 sides |
| `idea` | "I think", "how about", "let's try", "idea", "what if" |
| `meeting-summary` | "today meeting", "you guys", "team agreed", multiple people |
| `task` | action items, things to do, deadline |
| `observation` | "I noticed", "customer", real observation with no action |
| `lesson-learned` | "next time", "lesson learned", "shouldn't", "need to remember", "takeaway", past incident |
| `incident` | accident, incident, serious customer complaint, equipment failure mid-shift, food safety |
| `supplier-note` | supplier, ingredient price change, delivery quality, new/discontinued SKU |
| `sop-update` | "process is wrong", "SOP needs fix", "need to add step", operational gap discovered |
| `competitor-intel` | visited competitor, saw new concept/menu/price, market observation |
| `staff-note` | individual staff feedback, coaching, praise/criticism, HR observation (sensitive) |

**Priority:** "urgent", "gấp", "deadline today/tomorrow" → `urgent`. Otherwise: `normal`.

#### Domain(s):

| Keyword | Domain | Tag |
|---------|--------|-----|
| LU5, site, floor 5, F5, Nicholas, reallocation, allocation, ventilation, kitchen LU5 | `LU5` | `#lu5` |
| marketing, GrabFood, campaign, MKT, social, loyalty, promotion | `marketing` | `#marketing` |
| COL, labour, payroll, staffing, headcount, OIL, labour hours, CPH, roster | `labour` | `#labour` |
| COGS, food cost, menu, ingredients, beverage, supplier, recipe | `menu-cogs` | `#menu-cogs` |
| P&L, revenue, profit, breakeven, EBITDA, rent | `operations` | `#operations` |
| review, customer, service, complaint, CX, discount, FOC | `customer-experience` | `#cx` |
| LTO, summer bev, toast, limited time, seasonal | `lto` | `#lto` |
| SOP, process, protocol, standard | `sop` | `#sop` |
| LU3 | — | `#lu3` |
| LU7 | — | `#lu7` |

**Multi-domain:** Do NOT split. Use multiple tags. E.g.: `#labour #lu5`.

---

### Step 4 — 4-Tier Routing

| Type | Destination |
|------|-------------|
| `task` | `LUSINE_TODO_Kanban.md` (lane by priority) |
| `idea`, `competitor-intel` | `_ideas/YYYY-MM.md` |
| `[case:]` prefix | `_cases/active/` or `_cases/closed/` |
| all others | `_journal/YYYY-MM.md` |

> Wiki is only updated via `/ops-ingest`. Brain dump NEVER writes directly to wiki.

**Task lane routing (task → LUSINE_TODO_Kanban.md):**
- "urgent" / deadline hôm nay → 🔴 Today
- Deadline trong tuần / normal priority → 🟡 This Week
- Monitor / vague / future / no deadline → 📋 Backlog
- Thuộc case đang active → thêm link `[[_cases/active/{slug}]]` vào card
> Journal types: decision, meeting-summary, observation, staff-note, lesson-learned, incident, supplier-note, sop-update.

**LU5 Project exception** — when entry routes to case `lu5-relocation-crescent-mall` (Step 3 case detection matches this slug):

1. **decision** → also append to `projects/LU5_Reallocation/_DECISION_LOG.md` (in parallel with case). Then update `_INDEX.md` 🔴 Pending table: add new row to "Warren needs to decide".

2. **meeting-summary / supplier-note** → do NOT write to _DECISION_LOG. Only update `_INDEX.md` by keyword:
   - done_kw = [done, confirmed, approved, signed, received, completed] → append row to 🟢 Recently Done table
   - wait_kw = [waiting, pending, not yet, none yet, awaiting] → append row to 🟡 Waiting table
   - If both match or neither match → default 🟡 Waiting (safer — avoid false-positive into Pending)

3. **Others** (observation, staff-note, incident, lesson-learned, sop-update) → do NOT update `_INDEX.md`. Only append case timeline as normal.

4. **_INDEX.md append format** (each table type uses 1 new table row, newest on top within section):
   - 🔴 Pending: `| {n+1} | {Decision summary 1 sentence} | {date} | {source link if any} |`
   - 🟡 Waiting: `| {summary 1 sentence} | {who — person/org name} | {brief note} |`
   - 🟢 Done: `| {date} | {summary 1 sentence} |`

5. **Do not remove** old entry from 🟡 Waiting when appending to 🟢 Done — Warren reviews and removes manually.

> **Note (future projects):** When there is a new capital project (e.g.: LU3 renovation) — copy this block, change case slug + project path. Block auto-disables when case closes (no longer in _cases/active/).

**File rules:**
- Journal + Ideas: monthly rolling (`YYYY-MM.md`), newest entry on top, create if missing.
- Cases: create `YYYY-MM_{slug}.md`, append to `## Timeline`, close → move to `_cases/closed/YYYY-MM/`.
- Re-occurring case (same slug, different year): `{slug}_YYYY-MM.md`.

---

### Step 5 — Batch Plan

After processing **all** messages, display **one single batch plan**:

```
📥 X message(s) to process:
⚠️ **24h info:** Last fetch was [N hours] ago — [M] messages in range. Use `--hours N` for a narrower window.

━━━━━━━━━━━━━━━━━━━━━━━
[1] {type} | {workspace} {time} | {priority}
    "{text max 80 chars...}"
    🗂️ Tier: Journal / Ideas / Tasks
    💡 {1-sentence reason}
    📝 → {destination file}

[2] ...
    🗂️ Seems to belong to case [{slug}] — append? [2c] or skip
━━━━━━━━━━━━━━━━━━━━━━━

Confirm?
  [y]     Save all (case suggests ignored if no [Nc] reply)
  [Nc]    Append message N to case [{slug}]
  [Ns]    Skip message N
  [Ne]    Change routing for message N
  [all-s] Skip all
```

Wait for Warren to reply **once**. Do not save anything before confirm.

---

### Step 6 — Save notes (use write_to_file / apply_diff)

All file writes execute **sequentially one file at a time** (Hermes does not support parallel writes).
- **Create new / overwrite:** `write_to_file(path="...", content="...")`
- **Append / insert within file:** `apply_diff(path="...", diff="...")` — use SEARCH block to locate insertion point.
- **Journal / Ideas (newest on top):** `apply_diff()` insert after `---` header (SEARCH block = `---\n\n`, REPLACE = `---\n{new entry}\n\n`).
- **Tasks append (LUSINE_TODO_Kanban.md):** `apply_diff()` hoặc `edit()` prepend vào đúng column theo lane routing.

After all writes complete, collect results: if any write fails → hard error, tell Warren which file failed, do not write `.last_confirmed`.

**Journal entry (newest on top — insert after `---` header):**
```markdown
---
### [{date} {time}] {title}
**Source:** Slack #{channel} ({workspace})
**Type:** {type} | **Priority:** {priority}
#{tag1} #{tag2}

⚡ **Flags / Insights:** {if any — place BEFORE bullets}

{3-5 bullets content}

**Action Items:**
- [ ] {if any}
---
```

**Ideas entry:** Same as Journal, replace content with:
`**What:** / **Why interesting:** / **Next step:** (or "Review end of month")`

---

### Step 6b — Google Calendar (push_gcal.py) + Slack (tasks only)

**Calendar format:** Always use `TASK:` prefix — do not create regular events.
- Summary: `TASK: {task name} — {YYYY-MM-DD}`
- Description: "📋 [[LUSINE_TODO_Kanban.md]] | {context} | {deadline} | {stakeholders}" (use `--description`)
- Tags: `#task`, `#{store}` if applicable

**Kanban card format** (write via `edit()` / `apply_diff`):
```
- [ ] YYYY-MM-DD — {task} #tag1 #tag2 #{priority}
  deadline:: YYYY-MM-DD
  stakeholders:: [name1, name2]
```

Before adding task: use `search_files(path=".", regex="{YYYY-MM-DD}.*{first 3 words of title}", file_pattern="LUSINE_TODO_Kanban.md")` to check duplicate. Task CASE C (no deadline): search first 5 words of title. If `calendar::` already present → skip.

**CASE A — has specific date AND time:**
Timed event via `push_gcal.py`:
```bash
python vault/scripts/push_gcal.py --summary "TASK: {name} — {date}" --date YYYY-MM-DD --time HH:MM --tags "#task" --priority high --description "📋 Kanban: [[LUSINE_TODO_Kanban.md]] | {deadline} | {stakeholders}"
```
Then Slack DM: `execute_command(command="python vault/scripts/notify_slack.py \"📅 TASK: {name} — {date}\"")`.

**CASE B — has deadline date, no time:**
All-day event via `push_gcal.py`:
```bash
python vault/scripts/push_gcal.py --summary "TASK: {name} — {date}" --date YYYY-MM-DD --tags "#task" --priority medium --description "📋 Kanban: [[LUSINE_TODO_Kanban.md]] | {deadline} | {stakeholders}"
```
Slack DM: `execute_command(command="python vault/scripts/notify_slack.py \"📅 TASK: {name} — {date} — deadline today\"")`.

**CASE C — no date/deadline:**
No Calendar. Tag `📋 no-deadline`. Slack DM: `execute_command(command="python vault/scripts/notify_slack.py \"📋 {name} (no deadline)\"")`.

**Calendar fail → ⚠️ soft error** (write `.last_confirmed` with ⚠️), continue anyway.

---

### Step 6c — Case file template

**Create new case:**
```markdown
# Case: {slug}
**Opened:** {YYYY-MM-DD}
**Status:** OPEN
**Stakeholders:** {person / vendor / team names}
**Store:** {LU3 / LU5 / LU7 / all / personal}
**Keywords:** {2-3 words for entity matching}
**Follow-up:** {YYYY-MM-DD or "none"}

## Summary
{1-2 sentences}

## Open Items
- [ ] {action item}

## Timeline
*(newest on top)*

### [{date} {time}] {title}
**Source:** Slack #{channel} ({workspace})
{content}

---
```

**Append:** insert `### [{date} {time}] {title}\n**Source:** ...\n{content}\n\n---` at the top of `## Timeline` (below `*(newest on top)*` line).

**Close:** set `**Status:** CLOSED | {YYYY-MM-DD}`, add `**Resolution:** {1 sentence}`, move file to `_cases/closed/YYYY-MM/`.

---

### Step 6d — Write .last_confirmed (write_to_file)

After saving ALL, write `_inbox/.last_confirmed` using `write_to_file(path="_inbox/.last_confirmed", content="{int(fetch_start_timestamp)}\n# {ISO_8601_Vietnam} — confirmed")` with **same timestamp value as `.last_fetch`** (fetch-start time, not current time — preserves messages posted during processing window).

- **Soft error** (Calendar/Slack fail) → note ⚠️, continue, **still write** `.last_confirmed`.
- **Hard error** (file write fail) → stop, **do not write** `.last_confirmed`.

---

### Step 7 — Final summary + Slack DM (invoke_mcp)

0 messages → no DM.

≥1 message → Slack DM Warren via `invoke_mcp(tool=SLACK_SEND_MESSAGE_MCP_TOOL, params={channel: "Warren DM", text: "..."})`:
```
📥 Brain dump routed — {HH:MM}

📋 Tasks ({n}): TASK: {title} — {date} | Calendar ✓
📋 No-deadline ({n}): {title} 📋
📓 Journal ({n}): {title}
💡 Ideas ({n}): {title}
🗂️ Cases ({n}): [{slug}] {update title}
🗂️ Watching: {slug1}, {slug2}
⚠️ URGENT: {title}
```
Only show sections with ≥1 note. URGENT only when urgent. Watching only when `_cases/active/` has files. Send DM to Warren (do not post to channel).

---

**v3.2 | 2026-05-31 | Full Slack MCP removal: fetch_slack_notes.py + notify_slack.py replace all 3 MCP tools. Config, Step 0, 1, 2, 6b, 7 updated.**


### Step 8 — SYSTEM_VIEW Post-Op

After all writes confirmed and .last_confirmed updated:
1. Read 00_CORE_LOGIC/SYSTEM_VIEW.md
2. Update ## 🔴 ACTIVE CASES: refresh case list from files on disk
3. Update ## 🟡 Decisions Pending: remove resolved items (closed cases), add new ones
4. Update last_updated in frontmatter to today

---

## FIX: Dual-timestamp desync (2026-05-30)

**Root cause:** fetch_slack_notes.py uses its own .last_processed_ts.json, desyncs from .last_confirmed.

**Fix flow:** Always use --reset-ts, delete .last_processed_ts.json before fetch.

---

## POST-OP: SYSTEM_VIEW Update

After all messages are routed and .last_confirmed updated:
1. Read 00_CORE_LOGIC/SYSTEM_VIEW.md
2. Update section "## ACTIVE CASES": refresh case list from files on disk (check OPEN/CLOSED status)
3. Update section "## Decisions Pending": sync with active cases + resolved items
4. Update last_updated in frontmatter to today
