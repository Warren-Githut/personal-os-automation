---
name: "decommission-feature"
category: devops
tags: ['decommission', 'cleanup', 'feature', 'deprecation']
type: "skill"
status: "active"
version: "2026-07-12"
created: "2026-07-12"
domain: "vault+profile"
---

# decommission-feature

Safely remove a feature / system / dependency / naming across ALL layers of Warren's setup — vault docs AND Hermes profile internals. Use when Warren says "remove all X", "xóa hết X", "decommission", "clean X everywhere", or any cross-layer purge for consistency.

> **Why this skill exists:** A literal "remove all X" search-and-delete destroys INFRASTRUCTURE (config provider, live skill, running cron) that merely MENTIONS X. Text mentions ≠ the thing itself. Scope first, stage, verify.

## Layer map (search ALL of these)

| Layer | Path | Edit mechanism | Guard? |
|--------|------|----------------|--------|
| Vault active docs | `Documents/Warren_OS_Local/vault/**` | patch/write_file | no |
| Vault archive/snapshot | `vault/_archives/**`, `state-snapshots/**` | — | KEEP (history) |
| Profile SOUL/USER/MEMORY | `AppData/Local/hermes/profiles/<p>/*.md` | patch/write_file | no |
| Profile config | `.../config.yaml` | **`hermes config set <k> <v>`** | YES — direct edit refused |
| Profile skills | `.../skills/<name>/` | patch/rm | no |
| Profile cron | `cronjob` jobs | **`cronjob remove <id>`** | YES — jobs.json direct edit refused |
| Orphan data | `.../mem0_faiss/`, `*.json`, `*.db` | rm | no |
| Built-in MEMORY.md | `.../MEMORY.md` | patch | no |

## Classification (do NOT delete blindly)

- **ACTIVE ref** (live doc/config/skill mentions X) → groom/remove text.
- **INFRASTRUCTURE** (config `provider: X`, skill THAT IS X, cron THAT RUNS X) → disable via proper mechanism, not text delete.
- **DEAD/orphan** (old data on disk, archive, snapshot) → safe to delete; archive per policy.

## Staged sweep (B1→B5)

1. **B1 Active docs** — grep vault + profile .md; groom mentions; delete draft/obsolete files referencing X.
2. **B2 Config** — `hermes config set <layer>.provider builtin` (or appropriate). NEVER hand-edit config.yaml.
3. **B3 Skills** — delete skill dir via rm; repoint other skills that referenced it.
4. **B4 Cron** — `cronjob list` → `cronjob remove <id>` for X jobs.
5. **B5 Orphan data** — rm config/json/db/faiss dirs on disk.

## Verify (per layer, scoped search_files)

After each stage: `search_files` for the term in THAT layer's path only. Expect 0 active hits. Remaining hits should be archive/history/audit-log (acceptable, keep).

## User-reference (Warren)

- He expects **explicit double-check + risk analysis BEFORE destructive/structural ops** — even after saying "do it."
- "Remove all X" = clean all ACTIVE references, NOT blindly tear down infra. **Surface the infra distinction, propose staged plan** → he approves readily.
- Keep archive/history/lessons (don't scrub provenance).

## Pitfalls

- Editing `config.yaml` or `jobs.json` directly → **refused by guard**. Use `hermes config set` / `cronjob` API.
- Deleting a LIVE skill that other skills reference → patch those references or they dangle.
- 2 SOUL.md (vault copy + profile live) → profile is the agent; vault copy is editable artifact. Consolidate to 1 canonical, don't leave both stale-divergent.
- `git commit` vault repo: stage ONLY the decommission-scope files; pre-existing unrelated modifications (TODAY.md, case files) stay unstaged — don't bundle.

See `references/cross-layer-verify.md` for search patterns + the mem0 decommission case study (2026-07-12, full B1-B5 run, committed+pushed).
