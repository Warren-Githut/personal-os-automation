# Write-Approval Gate — human-in-the-loop for memory & skill writes

Extracted 2026-07-11 from Hermes docs (`memory.md`, `slash-commands`) + source
(`tools/write_approval.py`, `hermes_cli/write_approval_commands.py`). Complements
the vault-SSOT governance in SKILL.md §Memory Write Governance — this is Hermes's
*built-in* gate, independent of WARREN_MEMORY.md.

## What it is

Two independent boolean gates in `config.yaml`:

| Gate | Config key | Stages |
|------|-----------|--------|
| Memory writes | `memory.write_approval` | `memory` tool add/replace/remove |
| Skill writes | `skills.write_approval` | skill create/edit/patch/delete |

`false` (default) = write freely. `true` = stage for approval, never commit until
the user says yes. Covers **both** foreground turns and the background
self-improvement review.

## How staging works

When a write is staged (gate on), Hermes does NOT write immediately. It persists a
pending record and surfaces it for review out-of-band:

- **Pending store:** `<HERMES_HOME>/pending/{memory,skills}/<id>.json`
  (survives process restart; reviewable from CLI, gateway, or dashboard)
- **Foreground CLI memory writes:** prompt inline (entries are small enough to read)
- **Background review / gateway / all skill writes:** always **stage** (no inline
  prompt) → review via `/memory pending` etc.

## Review commands

```
/memory pending              # list staged memory writes (auto ones tagged [auto])
/memory approve <id|all>     # apply
/memory reject <id|all>      # drop
/memory approval on|off      # toggle + persist

/skills pending              # list staged skill writes + one-line gist
/skills diff <id>            # full unified diff (CLI/dashboard/file)
/skills approve <id|all>     # apply
/skills reject <id|all>      # drop
/skills approval on|off      # toggle + persist
```

## Persist via config (NOT via direct file edit — see pitfall)

```bash
hermes config set memory.write_approval true
hermes config set skills.write_approval true
hermes config set display.memory_notifications verbose
```

> **PITFALL — config write guard:** The agent cannot `patch`/`write_file` the
> `config.yaml` directly (guard refuses: "Agent cannot modify security-sensitive
> configuration"). Use `hermes config set <key> <val>` (or the in-chat
> `/memory approval on` / `/skills approval on` slash commands) instead. This applies
> per-profile: pass `--profile <name>` to target a non-active profile.

## Non-IT end-of-session approval pattern (Warren's setup)

For a non-IT user who wants a decision-ready digest instead of raw JSON:

1. **Gate on** for the profile (config above).
2. **Session-start check** (added to SOUL.md §Session Start): read
   `<HERMES_HOME>/pending/{memory,skills}/` — if non-empty, print a short
   Vietnamese digest:
   ```
   📋 Đề xuất nhớ/skill chờ duyệt (N mục):
   1. 🧠 Memory: [1-line summary]
   2. 🛠 Skill: [name + 1-line gist]
   → Duyệt hết: "/memory approve all" + "/skills approve all"
   → Bỏ từng cái: "/memory reject <số>" (hoặc "/skills reject <số>")
   ```
3. **Git commit/push hook** (added to SOUL.md §2.4.1): when Warren runs
   `git commit`, Hermes checks pending again — catches anything left from prior sessions.
4. **Warren approves with 1 line** (`/memory approve all` or
   `/skills approve all`) — or rejects individual items by number.

Key rule: Hermes **cannot self-approve** — only the human can. If Warren doesn't
type the approve command, the write stays staged (never lost). If pending is empty,
Hermes prints nothing (no noise).

## When to turn it on

- User says "turn on memory/skill approval", "don't let Hermes write memory
  without asking", or wants a decision-ready digest to approve writes.
- Multi-profile setups: apply per-profile; each profile's `pending/` is isolated
  under its own `<HERMES_HOME>`.
