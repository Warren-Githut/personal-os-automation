---
name: personal-vault-lint
description: >-
  Full vault health check for Personal_OS — evaluate red-flag triggers (AGENTS.md),
  verify vault integrity (frontmatter, git, stub files, ACTIVITY_LOG), track
  GG/court/sleep status, and produce a structured lint report. Runs as cron or on-demand.
trigger:
  - cron job: personal-lint
  - cron job: personal-vault-lint
  - manual: kiểm tra vault
  - manual: lint vault
  - manual: health check
  - manual: vault report
  - manual: /personal-lint
---

# Personal Vault Lint

## Overview

Periodic health check of the Personal_OS vault. Covers:
1. Red-flag trigger evaluation (per AGENTS.md red-flag table)
2. Vault integrity (frontmatter, stub files, git state, ACTIVITY_LOG)
3. Domain snapshots (health, GG, court)
4. Structured report with action items

Run daily via cron or on-demand when Warren requests a vault check.

## State-Awareness Phase (always first)

Before running any checks, absorb current state:

1. **`00_CORE_LOGIC/CONTEXT.md`** — life snapshot, active decisions, section 9
2. **`10_PULSE/Daily_Pulse.md`** — last 3-5 entries, check latest date
3. **`30_KNOWLEDGE_BASE/wiki/log.md`** — recent processing activity
4. **`_cases/active/`** — open cases, especially legal_divorce_court_GG_access.md
5. **`_inbox/01_unprocessed/`** — pending items count

## Red-Flag Trigger Evaluation

Per AGENTS.md red-flag table. Check ALL six:

| # | Trigger | How to check | Output |
|---|---|---|---|
| 1 | GG contact >7 days no log | Scan Daily_Pulse for last non-dash GG: line. Parse date from nearest header. | `N ngày since last GG contact` |
| 2 | Daily_Pulse gap >7 days | Read first `##` header in Daily_Pulse (newest on top). Compare to today. | `Last entry X days ago` |
| 3 | Sleep <6h x 5 nights | Read 051_Sleep_Log.md last 10 entries. Count nights <6h. | flag if >=5 |
| 4 | No equity thesis >6mo | N/A when 100% cash. Check each ticker thesis file. | — |
| 5 | Position >25% portfolio | N/A when 100% cash. Check CONTEXT.md allocation. | — |
| 6 | Polymarket 3 losing weeks | N/A when no active bot. | — |

Additional domain-specific checks:

| Domain | Check | Method |
|---|---|---|
| Legal | Court follow_up date passed | Read case file frontmatter `follow_up:`. Compare to today. Check post-17/6 CRITICAL GAP. |
| Health | Workout logged | Scan Daily_Pulse health lines for exercise mention. |
| Health | BP/weight trends | Read last 3 Daily_Pulse health entries, build mini table. |

## Vault Integrity Checks

### Stub detection
Search for `data_status: stub` across `30_KNOWLEDGE_BASE/wiki/` using `search_files`. List files with creation date from frontmatter `last_updated:`.

### Git state
```
git diff --name-status
git status --short
```
Check: uncommitted changes (M/D/A), untracked files, missing .gitignore.

### ACTIVITY_LOG gap
Read the vault's activity log last date header. Compare to today. If changes were made but ACTIVITY_LOG has no matching date, flag.
- Warren_OS_Local: `vault/10_OPERATION_DATA/morning_briefs/weekly_briefs_log.md`
- Personal_OS: `30_KNOWLEDGE_BASE/wiki/log.md` (or the active weekly log)
- ⚠️ RETIRED: old `_kilo/ACTIVITY_LOG.md` no longer exists — Kilo Code / Cursor retired 2026-07-09, Hermes Desktop is the only surface. Don't flag its absence.

### Inbox state
List `_inbox/01_unprocessed/` using `search_files(target=files)`. Empty means processed. Count any remaining files.

### Frontmatter validation (on-demand only, skip for cron brevity)

Scan all .md files excluding `raw/`. For each file:

1. **Structural check** (read first 15 lines, or parse with regex):
   - Starts with `---`?
   - Has a CLOSING `---` immediately after the YAML block (not a body horizontal rule)?
   - ⚠️ A raw count of `---` markers is a FALSE POSITIVE trap — body text uses `---` as section dividers. Use the regex in `references/frontmatter-lint-technique.md` to detect a true second YAML block. See Pitfalls: "Frontmatter-duplicate FALSE POSITIVE".

2. **Line-level error patterns** (grep for these anti-patterns):
   - `|field_name:` — **pipe** at start of YAML field (vỡ frontmatter, Obsidian đỏ)
   - `data_status: active` — **lạc schema**: AGENTS.md chỉ định nghĩa `data_status: stub` (cho file chưa có dữ liệu). Files có dữ liệu thật không được dùng field này.

3. **Required fields per directory** (per AGENTS.md):
   - `030-Companies/*/Thesis.md` — `domain`, `type`, `status`, `last_updated`, `ticker`, `company_name`
   - `030-Companies/*/BCTC*.md` — `domain`, `type`, `status`, `last_updated`, `ticker`, `source_files`
   - `030-Companies/*/Anti-thesis.md` — `domain`, `type`, `status`, `last_updated`, `ticker`
   - `030-Companies/*/Catalyst-watch.md` — `domain`, `type`, `status`, `last_updated`, `ticker`
   - `Candidates_Watchlist.md` — `domain`, `type`, `status`, `last_updated`, `tickers` (array), `related` (optional)

4. **Format validation** (parse raw YAML):
   - `last_updated: YYYY-MM-DD` (định dạng, không phải DD/MM)
   - `tickers` là array, không phải string
   - `source_files` là array, không phải string

5. **Consistency check** (030-Companies only):
   - `related` paths dùng format đồng nhất: `030-Companies/{NUMBER}-{TICKER}/{File}.md`
   - `review_log` entries có đúng format: `YYYY-MM-DD: action description`

Note: `execute_code` is blocked in cron mode. Use individual tools or `terminal` with grep.

## Report Format

Vietnamese co dau per HARD CONSTRAINT 7.

### Headers
```
## PERSONAL VAULT LINT REPORT - YYYY-MM-DD
```

### Red-Flag Table
```
### RED-FLAG TRIGGERS
| Trigger | Status | Detail |
```
Icons: FLAG, SAT HAN / CHU Y, OK, N/A, info

### Vault Integrity
```
### VAULT INTEGRITY
| Item | Status |
```

### Domain Snapshots
```
### HEALTH SNAPSHOT (last X days)
| Date | Sleep | Quality | Weight | Fasting | BP |
```
```
### COURT CASE
- follow_up: date
- Post-17/6: KNOWN or UNKNOWN
```

### Actions Needed
Priority prefixes:
- CRITICAL = GG, court overdue, sleep crisis
- IMPORTANT = uncommitted, stub files, ACTIVITY_LOG
- INFO = new ticker, stock pending, trend note

## Cron Job Mode

When running as cron (no user present):

- **SILENT rule**: If genuinely nothing new (all red-flags clear, integrity OK, no actions), respond exactly `[SILENT]` and nothing more. Suppresses delivery.
- **Never** ask questions or request clarification.
- If ANY red flag exists, ALWAYS report — never silent.
- **Tool restriction**: `execute_code` is blocked. Use: `search_files`, `read_file`, `terminal(git commands)`. Do NOT attempt `execute_code`.
- **Read-only**: Lint reports status. Do NOT modify vault files — report issues for user action.

## Pitfalls

- **Tool: execute_code blocked in cron.** Dont attempt it. Use search_files + read_file + terminal(git). For Python logic that cant be done with single tools, write a temp `.py` to disk (NOT under the vault — use a scratch path or `scripts/_lint_*.py` then `rm` after) and run via `terminal(python3 ...)`. This is the only Python path in cron mode.
- **Skill name alias — `personal-lint` ≠ `personal-vault-lint`.** The cron dispatcher skipped a run because the job called `personal-lint` (short name) but the skill is registered as `personal-vault-lint`. If a cron/command invokes `personal-lint` and returns "skill not found and skipped", treat it as THIS skill. Either rename the cron job to `personal-vault-lint` or add a dispatcher alias. Dont re-run the lint manually without noting the alias gap.
- **Frontmatter-duplicate FALSE POSITIVE.** Naively counting `---` markers (e.g. `len(re.findall(r'^---\s*$', txt, MULTILINE))`) catches markdown horizontal rules used as section dividers in body text (Sleep_Log has 42 such markers, all legitimate). A "duplicate frontmatter" flag is only real if a SECOND YAML block opens after the first closes: detect via `re.search(r'\n---\s*\n(.*?)\n---\s*\n', rest, DOTALL)` AND confirm it contains `^\w[\w-]*\s*:` key:value lines. Otherwise its a horizontal rule, not a dup-FM. See `references/frontmatter-lint-technique.md`.
- **GG contact detection.** The GG: line may say `-` (dash) for days. Last real contact = most recent date with actual text in GG: field.
- **Daily_Pulse ordering is newest-on-top.** The first `##` header is newest. Read from top, not bottom.
- **Court: follow_up vs actual outcome.** `follow_up` date means attention needed by then. The post-17/6 CRITICAL GAP is a separate flag indicating the court outcome is unknown.
- **Stub nuance.** Some stub files are by-design (RETRIEVAL_MAP.md auto-generated from index). Others (Net_Worth.md) are true stubs. Differentiate in report.
- **No double-reporting.** Each flag appears once.
- **Vietnamese in vault output.** Report body in Vietnamese. Tables, frontmatter, file names stay English.
- **MWG added mid-cycle.** Note new tickers as info, not a problem.
- **Triệt để purge = 4 layers.** Filename + content + hidden dirs + activity logs. A deprecated "X retired" note is ITSELF a trace — remove it too. See `references/deletion-discipline.md`.
- **False-positive guard.** A string match for a retired tool ≠ the tool. Verify file PURPOSE before deleting (e.g. `Personal_OS/tmp_agent_skills/` mentions "Cursor" but is an agent-skills framework TEMPLATE, not the Cursor app — deleting it would nuke a tech template). Read surrounding context first.
- **No auto-commit on purge.** After edits, show `git status` / `git diff --stat` and ASK before committing — unless Warren explicitly says commit. He often reviews first ("ko cho git gì luôn").
- **Filename scan MUST cover BOTH dot AND underscore prefix.** `*.kilo*` only matches `.kilo/`/`.kilocode/` — it SILENTLY MISSES `_kilo/`. Always scan `*_kilo*` too (and `*_cursor*` alongside `*.cursor*`). Missed this live 2026-07-09 → user caught leftover `_kilo/`. Full protocol + re-scan-confirmation step in `references/deletion-discipline.md`.
- **Memory anti-loop on purge lessons (Warren 2026-07-09).** After a purge, lessons go to `_personal_memory_raw.md` (unlimited SSOT) FIRST — never fight the `memory` tool's 2,200-char cap. Two stores are DISTINCT: (a) Hermes built-in = `memory` tool = 2200 cap, Hermes freely writes, Warren no opinion; (b) mem0 FAISS = SEPARATE unlimited, ONLY written by `/compress-memory`. Do NOT conflate them (SOUL.md §10 says "memory tool = mem0" — that refers to (a), not (b)). When `memory` tool nears cap → STOP, ghi raw, never delete-entry-to-fit. If `/compress-memory` has no tool exposing (b), report BLOCKED, rely on SSOT vault file. Looped 4× on this once by misreading — embedded in `references/deletion-discipline.md` Memory discipline section.
- **RESURRECTION-PROOF DELETION (Warren 2026-07-14).** Folder "xóa nhiều lần vẫn còn" = active cron/skill regenerate nó. Protocol: diagnose source (git tracked? commit re-add? skill hardcode write? cron `git add`? newest file after last delete?) → then 4-layer kill: `git rm -r --cached` + `rm -rf` + commit + patch generator skill + fix refs + verify. Full playbook in `references/deletion-discipline.md` RESURRECTION-PROOF DELETION. `_kilo/` case: 2 cron jobs regenerated `_kilo/ACTIVITY_LOG.md`; killed by redirecting both skills to `30_KNOWLEDGE_BASE/wiki/log.md`.
- **Symlink skills gotcha.** `personal_profile/skills/personal-commands` is a symlink → `warren-profile/skills/personal-commands` (same inode). Live skill source may NOT exist under personal_profile — grep warren-profile too. Patching via personal_profile path edits the canonical file; pass `cross_profile=True`.
- **Lint wikilink quirk.** `personal_lint.py` flags `[[folder]]` (no file) and `[[nested/path/file]]` as "Broken link" even though Obsidian resolves them. Use bare unique filename `[[01_about_GG]]` instead. Pre-existing broken links to non-existent files (e.g. `[[Co_Parenting_Log]]`) are NOT from your rename — leave them.
- **Vault rename/move protocol.** `git mv` (keep history) → grep ALL refs (00_WIKI_INDEX, 00_INDEX, RETRIEVAL_MAP, internal `related:`/`[[wikilink]]`, cross-folder, scripts/*.py) → fix in order → lint verify → commit SEPARATELY from deletions. Renumber files when moving into subfolder (`aa_x`→`01_x`); ask user first. Leave historical logs (STOCK_MEMORY.md, log.md) untouched. Full checklist in `references/deletion-discipline.md` PRE-FLIGHT rename/move.
- **RESURRECTION = 3 causes, not 1.** "Xóa rồi vẫn mọc lại" gần như luôn = (1) git-tracked: commit re-add (`git log -- <path>` thấu re-add; `rm -rf` một mình thất bại vì git index giữ); (2) cron/skill: cron job active chạy skill có step hardcode create/append vào path → recreate + commit theo lịch; (3) script: `.py` hardcode path. Permanent delete cần `git rm -r --cached` + `rm -rf` + `git commit` VÀ patch generator (skill/cron/script). Quy trình chẩn đoán đầy đủ trong `references/deletion-discipline.md` RESURRECTION DIAGNOSTIC.

## Related Skills

- `personal-inbox-routing` — processes inbox items. Lint checks inbox count but does not route.
- `personal-vault-lint` — (this skill) vault health check only.
- AGENTS.md — definitive source for red-flag trigger thresholds.

## References

- `references/canonical-schemas.md` — YAML frontmatter schemas cho all 030-Companies files (Thesis, BCTC, Anti-thesis, Catalyst-watch, Candidates_Watchlist). Includes anti-pattern table. Consult before creating/editing these files.
- `references/deletion-discipline.md` — purge protocol for retired tools/apps (Kilo/Cursor-class): 4-layer scan, false-positive guard, no-commit rule.
- `references/frontmatter-lint-technique.md` — correct FM detection (avoids `---` horizontal-rule false positives), field-completeness schema logic, cron-mode Python workaround, ad-hoc verification recipe.
- `references/vault-rename-move-discipline.md` — rename/move link-fix procedure + ROOT-CAUSE deletion (kill cron/skill generator via personal_profile→warren-profile symlink). Covers replace_all path-drop pitfall + py_compile verify gate.
