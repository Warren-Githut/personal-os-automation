---
name: bctc-pdf-ingest
description: "⚠️ DEPRECATED — merged into stock-ingest (warren-profile). BCTC PDF ingest pipeline: extract text, reconcile broker vs audited, propagate to 5 files. See stock-ingest SKILL.md for canonical rules."
version: 1.1
tags: [trading, bctc, pdf, thesis, vnstock, personal_os, deprecated]
---

# /stock-ingest — BCTC PDF Ingest Pipeline (see stock-ingest skill)

> **⚠️ CANONICAL SOURCE: `stock-ingest` skill (warren-profile)**
> This skill is a lightweight pointer. All canonical rules live in:
> `C:\Users\khoans\AppData\Local\hermes\profiles\warren-profile\skills\stock-ingest\SKILL.md`

## Quick Ref

| Topic | Location |
|-------|----------|
| Pipeline (9 steps) | `stock-ingest` skill |
| Propagation Rules (5 files) | `stock-ingest` skill » Propagation Rules |
| Research Queue auto-update | `stock-ingest` skill » Research Queue auto-update |
| YAML integrity pre-commit | `stock-ingest` skill » YAML integrity check |
| Root cause analysis | `stock-ingest` skill » Căn nguyên |

## Key Lessons (2026-06-23)

### Propagation Gap Fix
**Problem:** Before 2026-06-23, BCTC ingest only updated `BCTC - Rolling.md`, missing Thesis.md, Anti-thesis.md, Catalyst-watch.md, Candidates_Watchlist.md.
**Fix:** Enforced 5-file propagation rule in stock-ingest skill.

### YAML Pipe Error
**Problem:** `Candidates_Watchlist.md` had `|last_updated:` (pipe at start of YAML field), breaking frontmatter parsing.
**Fix:** YAML integrity pre-commit check: no pipes, no non-standard data_status, yaml.safe_load() pass.

### data_status: active — Wrong Schema
**Problem:** `data_status: active` used in multiple thesis files. AGENTS.md only defines `data_status: stub` (for files with no real data).
**Fix:** Removed `data_status: active` from all 030-Companies/ files. Never use this field unless file is truly a stub.

### Research Queue Stagnation
**Problem:** When tickers were added to Candidates_Watchlist (MWG, HPG), no Research Queue items were auto-created. Completed ingests (PVD, MWG) didn't auto-check queue items.
**Fix:** Research Queue auto-update rule: THÊM/UPDATE dòng khi ingest, chuyển status từ ⬜/⏳ → ✅.

## Related Commands
- `stock-ingest` — canonical BCTC → thesis pipeline (canonical: warren-profile)
- `stock-capture` — Trading news/broker report → pulse files pipeline