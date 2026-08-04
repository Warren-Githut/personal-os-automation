---
name: hermes-skill-runtime
description: "Hermes skill runtime behavior: slash command registration, trigger resolution, skill loading mechanics, and common pitfalls."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [hermes, skills, runtime, slash-commands, registration, debugging]
    related_skills: [hermes-agent, hermes-agent-skill-authoring]
---

# Hermes Skill Runtime Behavior

> **Scope:** How Hermes loads, registers, and executes skills at runtime. Complements `hermes-agent` (setup/config) and `hermes-agent-skill-authoring` (SKILL.md structure). This skill covers the *runtime mechanics* that caused real production issues.

---

## Overview

Hermes skills have two distinct phases:
1. **Authoring-time** — SKILL.md frontmatter + body (covered by `hermes-agent-skill-authoring`)
2. **Runtime** — How the agent discovers, loads, and exposes skills as slash commands (this skill)

The critical mismatch: **`trigger` field in frontmatter is documentation only**. Actual slash command registration derives from the **skill name** (folder name / `name` field).

---

## Slash Command Registration Mechanics

### The Rule

| Source | Determines |
|--------|------------|
| Skill folder name / `name` field | **Actual slash command** (e.g., folder `ops-process-notes` + `name: ops-process-notes` → `/ops-process-notes`) |
| `trigger` field | Documentation only — shown in `/help`, not used for registration |
| `quick_commands` config | Aliases (e.g., `process-notes: ops-process-notes` makes `/process-notes` work) |

### Registration Flow

```
~/.hermes/skills/<category>/<skill-name>/SKILL.md
         │
         ▼
Skill loader scans directory at session start
         │
         ▼
Extracts `name` field (falls back to folder name)
         │
         ▼
Registers `/${name}` in COMMAND_REGISTRY
         │
         ▼
Available in CLI autocomplete, Telegram menu, Slack mapping, /help
```

### Why This Matters

**Real production issue (this session):**
- Skill folder: `process-notes/`
- `name: process-notes`
- `trigger: "/ops-process-notes [--hours N] /process-notes [--hours N]"`
- **Result:** Only `/process-notes` worked. `/ops-process-notes` showed "No matches" in command palette.
- **Fix:** Rename folder to `ops-process-notes/`, set `name: ops-process-notes`, add `quick_commands` alias.

---

## Skill Loading & Discovery

### Load Order
1. **Session start** — Full scan of `~/.hermes/skills/` (all profiles) + in-repo `skills/`
2. **Level 0** — `skills_list()` returns `[{name, description, category}, ...]` (~3k tokens)
3. **Level 1** — `skill_view(name)` loads full SKILL.md content on demand
4. **Level 2** — `skill_view(name, "references/...")` loads supporting files

### Lazy Loading
- Skills are **not** pre-loaded into context
- Agent calls `skill_view(name)` when user invokes `/skill-name` or asks about it
- This is why `/help` shows all skills but context stays small

### Profile Isolation
- Each profile has its own `~/.hermes/profiles/<name>/skills/`
- Skills in profile A don't appear in profile B
- `hermes skills list --profile NAME` shows profile-specific install state

---

## Skill Bundles — Load Multiple Skills at Once

Hermes supports **skill bundles**: named groups of skills loaded via a single slash command. Useful for grouping related skills always used together (e.g., research + ingest + deploy before a stock purchase).

### Bundle Mechanics

```bash
# Create a bundle
hermes bundles create stock-deploy \
  --skill stock-deep-research \
  --skill stock-ingest \
  --skill stock-deploy-capital

# List all bundles
hermes bundles list

# Show a bundle's contents
hermes bundles show stock-deploy

# Delete a bundle
hermes bundles delete stock-deploy
```

**Result:** `/stock-deploy` loads all 3 skills at once.

### How Bundles Differ from Skills

| Aspect | Skill | Bundle |
|--------|-------|--------|
| Storage | `skills/<category>/<name>/SKILL.md` | `skill-bundles/<name>.yaml` |
| Has instructions? | Yes — full SKILL.md body | No — just a YAML skill list |
| Slash command | `/skill-name` | `/bundle-name` |
| What loads | 1 SKILL.md into context | All N constituent SKILL.md files |

### When to Bundle vs. Load Individually

- **Bundle** when you always use the same set together (e.g., `stock-deploy` before buying a stock)
- **Load individually** when skills have independent triggers and are rarely combined
- **Warning:** bundling 10+ skills loads all their SKILL.md → high token overhead. Keep bundles ≤5 skills.

### Storage & Profile Isolation

Bundles are YAML files in the active profile's `skill-bundles/` directory:

```yaml
# ~/AppData/Local/hermes/profiles/<profile>/skill-bundles/<name>.yaml
name: stock-deploy
skills:
- stock-deep-research
- stock-ingest
- stock-deploy-capital
```

Like skills, bundles are profile-scoped. A bundle created in `stock-profile` is not available in `warren-profile`.

### Reload

After manually editing a bundle YAML file:
```bash
hermes bundles reload
```

### Pitfalls

- **One-skill bundles:** Valid but unnecessary — `/skill-name` is shorter than `/bundle-name` with 1 skill.
- **Name collision:** If a bundle name matches an existing skill name, the bundle takes priority in the slash command registry. Don't reuse skill names for bundles.
- **Delete ≠ skill uninstall:** Deleting a bundle does NOT delete the constituent skills. They remain available via `/skill-name`.
- **Cross-profile:** Create bundles per-profile; they don't sync.

---

## Backward Compatibility: `quick_commands`

When renaming a skill (changing its slash command), preserve old invocations:

```yaml
# ~/.hermes/profiles/<name>/config.yaml
quick_commands:
  old-command-name: new-skill-name
```

**Example from this session:**
```yaml
quick_commands:
  process-notes: ops-process-notes
```

Now both `/process-notes` and `/ops-process-notes` work.

---

## Common Pitfalls

### 1. Trigger Field ≠ Registration
**Symptom:** Docs say `/ops-xyz`, command palette shows "No matches"
**Cause:** Skill named `xyz`, `trigger: "/ops-xyz"`
**Fix:** Rename folder + `name` field to `ops-xyz`, add `quick_commands` alias

### 2. Trigger Field Lists Multiple Commands
**Symptom:** `trigger: "/ops-foo /foo /bar"` — only `/foo` works
**Cause:** Only first token (skill name) registers; rest are docs
**Fix:** Pick ONE canonical name, use `quick_commands` for aliases

### 3. Category Folder vs Skill Folder
**Symptom:** Skill not found, `skills_list` doesn't show it
**Cause:** Placed SKILL.md in `skills/category/SKILL.md` instead of `skills/category/skill-name/SKILL.md`
**Fix:** Skills MUST be in their own subfolder under category

### 4. Session Cache
**Symptom:** Created new skill, `/skill-name` says "not found"
**Cause:** Skill loader initialized at session start
**Fix:** `/reset` (new session) or restart Hermes

### 5. Profile Mismatch
**Symptom:** Skill installed but not showing
**Cause:** Installed in default profile, running `lusine-profile`
**Fix:** `hermes skills install --profile lusine-profile ...` or copy to profile's skills dir

### 6. Windows Path Mangling in Skill Scripts
**Symptom:** `patch`/`write_file` with `/c/Users/...` → `C:\\c\\Users\\...`
**Cause:** MSYS path translation
**Fix:** Use Windows paths `C:\\\\Users\\\\khoans\\\\...` or `terminal(python)` for writes

### 7. Deleting a Skill That Exists in Multiple Profiles
**Symptom:** Skill still appears in another profile after `skill_manage(action='delete')`
**Cause:** `skill_manage` only deletes from the current profile's skills directory. If the skill was installed or copied to other profiles (common with shared skills like `macro-frameworks`), it persists there.
**Fix:** After `skill_manage(action='delete')`, manually check and delete from other profiles:
```bash
rm -rf /c/Users/khoans/AppData/Local/hermes/profiles/<other-profile>/skills/<category>/<skill-name>/
```
**Verify:** `ls <other-profile>/skills/<category>/<skill-name>/` should show "No such file or directory".

---

## Verification Checklist

After creating/modifying a skill:

- [ ] `hermes skills list --profile <active>` shows skill as `enabled`
- [ ] `/help` in new session lists the skill with correct name
- [ ] Command palette autocomplete shows `/skill-name`
- [ ] If renamed: `quick_commands` alias works for old name
- [ ] `skill_view(name="skill-name")` loads full content (no truncation)
- [ ] References/templates/scripts load via `skill_view(name, "references/...")`

---

## One-Shot Recipes

### Rename a Skill (Canonical → Fix Mismatch)
```bash
# 1. Move folder
mv ~/.hermes/profiles/<name>/skills/old-name ~/.hermes/profiles/<name>/skills/new-name

# 2. Update SKILL.md frontmatter
# name: new-name
# trigger: "/new-name [args]"

# 3. Add backward compat
hermes config set quick_commands.old-name new-name --profile <name>

# 4. Verify
hermes skills list --profile <name> | grep new-name
# → restart Hermes desktop / /reset
```

### Debug Why Slash Command Not Working
```bash
# Check skill name registration
hermes skills list --profile <name> | grep -i <partial-name>

# Check config aliases
grep -A10 "quick_commands" ~/.hermes/profiles/<name>/config.yaml

# Check SKILL.md name field
cat ~/.hermes/profiles/<name>/skills/<skill-name>/SKILL.md | head -20
```

---

## References

- `hermes-agent` — Setup, config, CLI, gateway, profiles
- `hermes-agent-skill-authoring` — SKILL.md structure, validator, in-repo vs user-local
- Official docs: https://hermes-agent.nousresearch.com/docs/user-guide/features/skills
- Slash command registry source: `hermes_cli/commands.py` (COMMAND_REGISTRY)