# 2026-07-27 — Google Review Monday cron: orchestrator↔parser week mismatch

## Files reviewed (warren-profile, Warren_OS_Local vault)
- `vault/.scripts/google_review_monday_cron.py` (vault copy) — wrapper run by no_agent cron `google-review-monday` (schedule `45 9 * * 1`, `next_run_at` 2026-08-03).
- `AppData/Roaming/Hermes/profiles/warren-profile/scripts/google_review_monday_cron.py` — the RUNNING copy (profile/scripts). **Differs** from vault copy: only cosmetic import moves + the intended `ok 05`→`ok rv` edit lives HERE. Week logic identical → bug applies to production.
- `vault/.scripts/gen_google_review_dashboard.py` — dashboard regen (correct).
- `vault/10_OPERATION_DATA/.parsers/google_review_parser.py` — parser (writes the week).
- `vault/.scripts/tests/test_google_review_monday_cron.py` — unit tests (false-green).
- `vault/10_OPERATION_DATA/05_Google_Review_Weekly_Log.md` — SSOT log (W20–W30 present).

## The bug
- Wrapper `compute_current_week_label(d)` → `d.isocalendar()` = **Monday-ISO CURRENT week**.
  - 2026-07-27 → `2026-W31`; 2026-08-03 (first real run) → `2026-W32`.
- Parser `detect_week()` is **Sunday-based**: `week_end = today - (weekday+1)%7`; `week_start = week_end - 6`. `build_entry` writes `week_start.isocalendar()` = **PRIOR** ISO week.
  - 2026-07-27 → writes `2026-W30`; 2026-08-03 → writes `2026-W31`.
- Mismatch on every run. Consequence chain:
  1. `should_skip(log, compute_current_week_label())` checks W31/W32 → never in log → always runs parser (guard inert).
  2. `format_tg_summary(log, compute_current_week_label())` searches `## W31|` / `## W32|` → never present → always returns fallback `"✅ … đã cập nhật (không tìm thấy entry để tóm tắt)"` — data-less, mislabeled green message.
  3. Real protection = parser's own in-body `if week_id in body` dedup; cron guard adds nothing and misleads logs (`week_id = 2026-W31` while W30 lands).

## Proof (execution, not assertion)
```
Run date 2026-07-27: cron_week=2026-W31 parser_writes=2026-W30 MATCH=False
   should_skip('2026-W31')=False  -> summary: '✅ 2026-W31 đã cập nhật (không tìm thấy entry để tóm tắt)'
Run date 2026-08-03: cron_week=2026-W32 parser_writes=2026-W31 MATCH=False
   should_skip('2026-W32')=False  -> summary: '✅ 2026-W32 đã cập nhật (không tìm thấy entry để tóm tắt)'
format_tg_summary(text, "2026-W30") -> '🟢 Google Review Weekly — 2026-W30\nSystem avg★: 5.0 | R/1k: 2.0'  # function is CORRECT, fed wrong week
format_tg_summary(text, "2026-W31") -> '✅ 2026-W31 đã cập nhật (không tìm thấy entry để tóm tắt)'
```

## Test blind spot (false-green)
`tests/test_google_review_monday_cron.py` hardcodes `2026-W30` in `test_should_skip_true` / `test_format_tg_summary`, and `test_week_label_monday_iso` asserts `compute_current_week_label(2026-07-27)=="2026-W31"` while *assuming* that matches the parser. Nothing calls `compute_current_week_label()` and feeds its result into guard/summary against the real log. 5 GREEN tests, integration bug invisible. The submission's "verified facts" (`compute_current_week_label() today = '2026-W31' (matches parser)`) was FALSE.

## Verdict
FAIL. Fix = wrapper must derive target week from the parser's `detect_week`/`make_week_id` (or pass `--week` and read back written `## <week_id>`). Then guard + summary target the week actually written.

## Other flags (not fails)
- `ok rv` deviation validated: `ops-cron-patterns/SKILL.md:188-189` reserves `ok 05` for capture-sleep on same bot `LUsineWorkBot`/chat `2117653672` → `ok rv` correct.
- Orphan empty `vault/05_Google_Review_Weekly_Log.md` (0 bytes) duplicates canonical `10_OPERATION_DATA/05_Google_Review_Weekly_Log.md`.
- TG summary omits "reply ok rv to commit/push" instruction the pattern doc expects.
- `search_files` returned 0 / IO-error on dotfolder paths (§9) — used `terminal` grep instead.
