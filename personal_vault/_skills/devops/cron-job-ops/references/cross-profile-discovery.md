# Cross-Profile Cron Discovery — references

> Companion to SKILL.md §10. Captured 2026-07-18: Warren (stock-profile session) asked about
> "review telegram sender" cron. `cronjob(action='list')` returned only stock-profile's 4 crons
> (none matching). The cron actually lived in **warren-profile**. Lesson: the tool is profile-scoped.

## Why this matters
`cronjob(action='list')` shows ONLY the active profile's jobs. Warren may ask about a cron from a
different profile (e.g. stock-profile session → warren-profile cron). The cron exists but is
invisible to the tool. Don't conclude "no such cron" — check other profiles.

## Profiles on this Windows host
- `warren-profile` — main, most crons (broker fetch, review watcher/sender, promo, backup...)
- `personal_profile` — health/sleep/personal automation
- `stock-profile` — stock-price-daily, frameworks-weekly (Telegram), mem0-cleanup, vault-health

## Recipe: discover a cron across all profiles

```bash
# Fast keyword scan (uses terminal grep — NOT search_files, MSYS false-negatives)
for p in warren-profile personal_profile stock-profile; do
  echo "=== $p ===";
  grep -o -i -E "telegram|sender|review|fetch|<keyword>" \
    "/c/Users/khoans/AppData/Local/hermes/profiles/$p/cron/jobs.json" | sort | uniq -c;
done
```

```bash
# Full read of one profile's jobs
read_file("C:/Users/khoans/AppData/Local/hermes/profiles/<profile>/cron/jobs.json")
```

## jobs.json location
```
C:/Users/khoans/AppData/Local/hermes/profiles/<profile>/cron/jobs.json
```
Top-level: `{ "jobs": [ {job}, ... ] }`. Each job object:

| field | meaning |
|-------|---------|
| `id` | job uuid (dùng cho `cronjob action=run/update/remove`) |
| `name` | human name (vd `review-telegram-sender`) |
| `schedule` | `{kind:"cron", expr, display}` OR `{kind:"interval", minutes, display}` |
| `script` / `prompt` | no_agent → `script` (bare name in profile/scripts/); agent → `prompt` |
| `no_agent` | true = chạy script Python (free), false = chạy LLM agent (tốn credit) |
| `enabled` / `state` | on/off, "scheduled" |
| `next_run_at` / `last_run_at` | ISO timestamps |
| `last_status` | "ok" / "error" |
| `last_error` | short summary — FULL raw in `cron/output/<job_id>/<ts>.md` |
| `completed` | run count (vd 4859 = đã chạy gần 5000 lần) |
| `deliver` | "local" / "all" / "telegram:<chat_id>" |

## Schedule — two shapes (don't misread)
- `kind:"cron"` → cron expression. `"0 9 * * *"` = 09:00 mỗi ngày. `"30 15 * * 1-5"` = 15:30 T2-T6.
- `kind:"interval"` → `"minutes": N`, display `"every Nm"`. `"minutes":1` = **mỗi 1 phút**.
  Common for watcher/sender pairs. NOT a daily/hourly cron despite the short interval.

## Example: review-telegram-sender (warren-profile)
```
id:        97c05046989a
name:      review-telegram-sender
schedule:  { kind:"interval", minutes:1 }   → runs EVERY 1 MINUTE
script:    review_telegram_sender.py
no_agent:  true
completed: 4859  (last_status ok)
deliver:   local
pairs with: review-queue-watcher (interval 1m) which preprocesses reviews → queue
```
→ To reduce Telegram send frequency, bump `minutes` from 1 to 5–10 (watcher still feeds within window).

## Pitfall: search_files false-negative
`search_files` trên Windows MSYS trả rỗng/rỗi dù file tồn tại. Luôn verify bằng `terminal`
`ls`/`grep` khi tìm jobs.json hoặc folder vault. (See STOCK_MEMORY lesson 2026-07-17.)
