# warren-profile Curator — verified behavior (2026-07-15)

## Scope quirk
`hermes curator status` reported `agent-created skills: 113 total` on warren-profile, yet a `grep -rEi 'created_by|author|pinned'` across every `SKILL.md` found **zero `created_by:` fields**. → Curator counts ALL skills in a profile as agent-created in-scope, regardless of frontmatter. Hand-built skills are subject to 90d idle auto-archive.

## Pinned set (18, verified applied)
reconcile-revenue-ssot, bctc-pdf-ingest, ops-pnl-ingest, lusine-payroll-ingest,
stock-deep-research, stock-ingest, ops-dashboard, sync-html-chart-from-ssot,
promo-eval, ops-initiative-plan, ops-case-lifecycle,
luso-parsers, ops-col, vault-ops-automation, ops-review, ops-weekly-report.

All returned: "curator: pinned '<skill>' (will bypass auto-transitions)".

## Archive contents (check before restore)
`hermes curator list-archived` → 4 entries, ALL dupes of live skills (do NOT restore):
- deep-research-stock  → live: stock-deep-research
- ops-pl-13_Monthly_PL_Breakdown → live: ops-pnl-ingest
- pdf-parse            → live: liteparse
- personal-stock-ingest → live: stock-ingest

## Consolidation
Enabled via `hermes config set curator.consolidate true` → `config.yaml:curator.consolidate: true`.
`hermes curator status` then showed `consolidate: on`. (No CLI flag exists for this.)
