---
name: hermes-curator-hygiene
description: Protect important agent-created skills on a Hermes profile from the Curator background pass (7d run / 30d stale / 90d archive). Verify curator scope, decide which skills to pin, check/restore the archive, and enable LLM consolidation. Use when the user mentions "curator", "skill got archived", "pin skills", or asks to protect skills from auto-archive.
type: skill
category: devops
status: active
created: 2026-07-15
trigger: "user mentions curator / skill archived / pin or protect skills / enable consolidation"
---

# Hermes Curator Hygiene

The Curator is an auxiliary background task that periodically reviews agent-created skills, marks them stale (30d unused) and archives them (90d unused). Archives are recoverable (`.archive/`); it never deletes. Pinned skills bypass every auto-transition and LLM review pass.

## When to use this skill
- User says a skill "got archived" or is missing from the prompt.
- User asks to "pin" or "protect" skills.
- Periodic profile maintenance.
- Before/after enabling LLM consolidation.

## 1. Verify scope FIRST — do NOT trust the doc
The bundled `hermes-agent` skill claims Curator "only touches skills with `created_by: "agent"` provenance." **This is NOT reliably true per profile.** On warren-profile (verified 2026-07-15): `hermes curator status` reports `agent-created skills: 113 total` even though a grep across every `SKILL.md` found ZERO `created_by:` frontmatter fields. → Every skill in the profile is in-scope for auto-archive, including hand-built ones.

ALWAYS verify with:
- `hermes curator status` → counts, interval, `consolidate` flag, least/most-active top-5.
- `hermes curator usage` → provenance column (`agent`/`hub`/`builtin`) per skill + activity/use/view/patch counts + `last_activity`.

## 2. Pin SOP (the only real protection)
Pinning bypasses ALL auto-transitions and LLM consolidation. Reversible via `unpin`. Zero risk.
```
hermes curator pin <skill-name>
# → "curator: pinned '<skill>' (will bypass auto-transitions)"
hermes curator unpin <skill-name>
```
Pin everything important, ESPECIALLY rare/low-frequency skills (highest 90-day trap):
- **Rare / quarterly** (used a few times a year → idle gap > 90d between uses): e.g. reconcile-revenue-ssot, bctc-pdf-ingest.
- **Monthly**: ops-pnl-ingest, lusine-payroll-ingest.
- **Occasional**: promo-eval, ops-dashboard, sync-html-chart-from-ssot, stock-*.
- **Core infra** (pin for safety): luso-parsers, ops-col, vault-ops-automation, ops-review, ops-weekly-report.

Verified 2026-07-15 (warren-profile): pinned 18 critical/rare skills; `curator status` later confirmed `consolidate: on`.

## 3. Inspect / restore the archive
```
hermes curator list-archived      # lists archived skill dirs
hermes curator restore <name>     # move back from .archive/
```
BEFORE restoring, check if the archived name is a DUPLICATE of a live skill (common after renames/refactors). If a live counterpart exists, LEAVE it archived:
- deep-research-stock → live: stock-deep-research
- ops-pl-13_Monthly_PL_Breakdown → live: ops-pnl-ingest
- pdf-parse → live: liteparse
- personal-stock-ingest → live: stock-ingest

## 4. Enable LLM consolidation (optional, costs aux-model tokens)
OFF by default. Enable via config — there is NO CLI flag (`hermes curator --help` has no set subcommand):
```
hermes config set curator.consolidate true
hermes curator status | grep consolidate   # → "consolidate:    on"
```
Consolidation merges overlapping skills. If it merges wrongly later, disable: `hermes config set curator.consolidate false`.

## Pitfalls
- **Don't trust the "created_by: agent" gate.** Verify with `curator status`/`usage`. On profiles where all skills are counted agent-created, unpinned hand-built skills WILL be archived after 90d idle.
- **Pin is the only protection for rare skills** — there is no "exclude by name" config.
- **Consolidation is opt-in and uses tokens** — don't enable casually if the user dislikes auto-merges.

## References
- `references/warren-profile-quirk.md` — verified scope behavior + pinned list + archive dupes (2026-07-15).
