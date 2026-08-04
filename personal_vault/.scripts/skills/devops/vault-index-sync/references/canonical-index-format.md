# Canonical Vault Index Format

Use this template when creating or rewriting any index file across profiles (warren or personal).

## 1. YAML Frontmatter

```yaml
---
name: <INDEX_NAME>
type: index
status: active
domain: work | personal | meta
owner: Hermes (Head of Ops: Warren) | Hermes / Warren | ORION
scope: <path or subsystem this index covers>
last_updated: YYYY-MM-DD
total_files: <N>
index_first_rule: Always read this file before <action>; do not <anti-pattern>
auto_update: <who> must update this index when <trigger>
stale_check: <condition that means stale>
refresh_cadence: session_start | event-driven | <cron>
maintained_by: Hermes (auto-sync) + Warren (approval for <X>)
related_paths:
  - <related path 1>
  - <related path 2>
---
```

## 2. Inventory Table Rules

- Use these normalized columns when possible: `file`, `period`, `type`, `key_insights`, `last_updated`
- For case indexes: `case_id`, `status`, `domain`, `opened`, `follow_up`, `priority`, `owner`
- For SOP indexes: `name`, `status`, `last_verified`
- Custom columns are allowed only if `related_paths` or notes explain why the custom schema is needed

## 3. Update Protocol Section

Always include at the bottom:
- How entries are added/removed/updated
- Whether the index is **derived** (read from source files) or **canonical** (source of truth)
- What triggers a refresh
- What to do when a referenced file is missing (mark stale here, do not silently skip)

## 4. Workspace Authority

- `99_HERMES_AGENT_WORKSPACE/` = agent-internal SOPs, rules, indexes, scratch
- `30_KNOWLEDGE_BASE/wiki/` = human-facing knowledge base (Warren/docs)
- Files with `hermes_` prefix inside agent workspace are canonical for that workspace; same-named files elsewhere are secondary
