---
model: deepseek-obsidian/deepseek-v4-pro
description: "Voice note processing protocol (transcribe -> classify -> enrich -> archive) adapted for ORION+Deepseek toolchain."
updated: 2026-06-02
---

# /process-voice
# v1.0 | 2026-05-25

Transcribe, classify, and enrich voice notes into Markdown notes with clear names, correctly typed tags, and linked wiki.

## Usage

```
/process-voice              # process all unprocessed files in _inbox/voice/
/process-voice <filename>   # process 1 specific file
```

## Steps

$ARGUMENTS

---

### Step 1 — Find files

- No arguments: `list_files(path="_inbox/voice/", file_pattern="*.m4a")` find all `.m4a .mp3 .wav .ogg` without processed notes
- Has filename: process that file (fuzzy match name, no full path needed)

---

### Step 2 — Transcribe

```
execute_command(command="python scripts/process_voice.py \"_inbox/voice/<filename>\" --model small")
```

`read_file()` output path from stdout (format `__tmp_*.md`). `read_file()` content to get transcript with personal terms fixed.

---

### Step 3 — Classify type

`read_file()` transcript, choose 1 of the following types:

| Type | Signs |
|------|----------|
| `decision` | has specific numeric target, "decide", "from now on", "will do" |
| `idea` | "I think", "how about", "let's try", "idea", "what if" |
| `meeting-summary` | "today meeting", "you guys", "team agreed", multiple people |
| `task` | only action items, things to do, deadline |
| `observation` | "I noticed", "customer", real observation with no action |

**Priority:** If transcript has "urgent", "boss asked", "deadline today/tomorrow" -> `urgent`. Otherwise: `normal`.

---

### Step 4 — Fill content and name file

**Create concise title** (5-8 words) summarizing main content. Example: `GG access strategy review`.

**New filename:** `[{type}] {title} - {date}.md`
Example: `[decision] GG access strategy review - 2026-05-14.md`

**Fill into file:**

```yaml
tags: [inbox, voice, {type}]   # replace unprocessed with type
type: {type}
priority: {normal|urgent}
```

```markdown
# {Title}   <- replace "Voice Note — filename" with meaningful title

## Key Points
- {3-5 bullets summarizing main content, in Warren's language}

## Action Items
- [ ] {specific tasks if any, leave empty if none}

## Context / Follow-up
**Related Wiki:**
{link appropriate wikis based on keywords}
```

**Wiki link mapping:**

| Keyword heard | Link |
|---|---|
| trading, stock, equity, portfolio | `[[30_KNOWLEDGE_BASE/wiki/trading/Trading_Strategy]]` |
| health, weight, exercise, sleep, blood | `list_files(path="30_KNOWLEDGE_BASE/wiki/health/", file_pattern="*.md")` -> pick best match |
| GG, Gia Gia, family, son, parent | `list_files(path="30_KNOWLEDGE_BASE/wiki/family_gg/", file_pattern="*.md")` -> pick best match |
| finance, budget, net worth, debt, saving | `list_files(path="30_KNOWLEDGE_BASE/wiki/finance/", file_pattern="*.md")` -> pick newest file |
| growth, learning, book, insight, course | `list_files(path="30_KNOWLEDGE_BASE/wiki/growth/", file_pattern="*.md")` -> pick best match |
| relationship, friend, connection | `list_files(path="30_KNOWLEDGE_BASE/wiki/relationship/", file_pattern="*.md")` -> pick best match |
| decision | `[[30_KNOWLEDGE_BASE/wiki/DECISION_LOG]]` |

Use `apply_diff()` to update file `__tmp_*.md` with all enriched content.

Then **rename file** from `__tmp_*.md` -> `[{type}] {title} - {date}.md` using `execute_command(command="mv ...")`.

---

### Step 5 — Display and confirm

Show completed note. If `priority: urgent` -> add **⚠️ URGENT** line before displaying.

Ask: "Note ok? Any changes needed?"

---

### Step 6 — Archive audio

If Warren confirms ok -> `execute_command(command="mv ...")` move audio to `_inbox/voice/done/`.
