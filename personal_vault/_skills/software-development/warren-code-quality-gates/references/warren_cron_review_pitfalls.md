# Warren Cron / Parser Diff Review — Wrong-Depth & Duplication Pitfalls

Durable review checklist for L'Usine ops cron + orchestrator diffs (`profile/scripts` crons, `vault/.scripts` orchestrators/parsers). Captured 2026-07-28 from an `lto_weekly_cron.py` vs `google_review_monday_cron.py` review.

## The wrong-depth axis (apply to every cron/parser diff)
A "wrong-depth" change is a band-aid: the symptom is patched at ONE call site while sibling sites keep the same flaw, OR a special-case escape is added instead of fixing the shared mechanism. When you see one, ask: *"is there another cron/parser with the same shape that still has the bug?"* If yes, the fix belongs at the shared layer, not the call site.

## Warren-specific pitfalls verified this session

### 1. VAULT_ROOT resolution — two-tree architecture
- Crons live in TWO trees: `profile/scripts/` (no_agent cron wrappers) and `vault/.scripts/` (orchestrators/parsers).
- `VAULT_ROOT = SCRIPT_DIR.parent` ONLY works when the script lives in `vault/.scripts` (parent = vault). For a cron in `profile/scripts`, `SCRIPT_DIR.parent` = `warren-profile/` which has NO `10_OPERATION_DATA` → every path (LOG_FILE, PARSER, REGEN) is wrong.
- `google_review_monday_cron.py` exists as TWO byte-identical copies (`profile/scripts` + `vault/.scripts`). The `profile/scripts` copy's `SCRIPT_DIR.parent` resolves to the wrong tree.
- **Deeper fix:** one `resolve_vault_root()` (env `WARREN_VAULT` → documented fallback) used by ALL crons. Do NOT hardcode `C:\Users\khoans\…` literals (`lto_weekly_cron.py:40`) — that is a machine-specific band-aid.
- **Risk if missed:** silent wrong-path reads/writes; two copies invite drift.

### 2. TG send — DRY applied at one site only
- `lto_weekly_cron.py` imports the shared `profile/scripts/_send_telegram.py` (`from _send_telegram import send_telegram`).
- `google_review_monday_cron.py` inlines its own `_get_bot_token` + `_send_telegram` (comment: "copy từ col_deterministic_watcher.py") — duplicated logic.
- **Deeper fix:** both import `_send_telegram`. **Reconcile before switch:** inline returns `bool`; module returns `dict` `{"ok":…}`; module sets `parse_mode=HTML`, inline sets none. A blind swap changes google's return contract + render.

### 3. compute_current_week_label — SAME NAME, DIFFERENT SEMANTICS
- `lto_weekly_cron.py`: returns PREVIOUS week (Monday-of-yesterday) — measures the week that closed Sunday.
- `google_review_monday_cron.py`: returns CURRENT week (direct `date.today().isocalendar()`) — measures this week.
- Naive "move the 3 functions to `_utils.py`" silently breaks one. **Do NOT merge as-is.**
- **Deeper fix:** explicit `compute_iso_week(ref, offset: int)` (-1 LTO / 0 Google) OR rename to `compute_prev_week_label` / `compute_current_week_label`.
- **Precedent:** shared-week-util was already DEFERRED as RISKY (commit `10c702c`); a year-boundary week-spam bug was fixed in `8364473` (use Monday calendar year to match `grabfood_parser.py:386`). Week math is a known footgun — never touch without regression tests.

### 4. should_skip — coupled to each log's header format
- LTO requires `PROMO MEASUREMENT (B+C)` suffix; Google matches `## <week_id>` only.
- Different functions wearing the same name. **Deeper fix:** parametrize with `header_marker`, or leave duplicated. Low value to merge.

### 5. Two independent "Monday of ISO week" implementations
- `lto_weekly_cron.py:53-58` (`_monday_of_yesterday` + isocalendar) vs `weekly_lto_sql.py:44` (`_monday_of_week`, jan4 formula). Must stay in sync; year-boundary risk.

## Duplication decision rule (cron-lib consolidation)
When tempted to extract `compute_current_week_label` / `should_skip` / TG-send into a shared module:
- **TG send:** share NOW (low risk, high value) — reconcile return type + parse_mode first.
- **Week-label & skip:** keep duplicated-but-RENAMED until a parametrized lib (`week_offset`, `header_marker`) ships WITH regression tests. Do not blind-copy the 3 functions into `_utils.py` (parser-domain; would also misplace them).

## Verification recipe (wrong-depth check)
For each duplicated helper across cron files:
1. `grep -rn "def <fn>" profile/scripts vault/.scripts` → list every definition.
2. Diff their BODIES, not just names — same name ≠ same behavior (see #3).
3. Path resolution: from the DEPLOYED script dir, assert `(Path(__file__).parent.parent / "10_OPERATION_DATA").exists()` is True.
4. Week math: assert `compute_iso_week(date(2027,1,4))` (and a year-boundary date) round-trips with the orchestrator's `_monday_of_week`.
