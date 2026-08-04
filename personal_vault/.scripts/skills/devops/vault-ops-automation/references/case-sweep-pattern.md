# Case Sweep Pattern — case_followup_orchestrator.py

Reproduced 2026-06-14. Daily/weekly sweep to clear overdue cases from TODAY.md.

## Problem
- TODAY.md shows "10 case quá hạn" — cases with past `follow_up` dates
- Calendar events exist for past dates (stale)
- Warren sees stale follow-ups daily, creates noise

## Root Cause
- `follow_up` in case frontmatter not updated after initial creation
- Orchestrator only runs on demand, not automatically
- `--update` flag needed to delete old GCal event + create new one

## Fix Pattern
```bash
# 1. Update frontmatter follow_up to future date
# 2. Re-run orchestrator with --update to delete old event + create new
python case_followup_orchestrator.py --slug <slug> --update
```

## Batch Script (for 10+ cases)
```bash
# Update frontmatter first (patch each case file)
# Then batch re-run:
for slug in "2026-05_delivery-man-khanh-resign" "2026-05_jasmine-tea-sourcing" ...; do
  python case_followup_orchestrator.py --slug "$slug" --update
done
```

## Follow-up Date Strategy
- HIGH priority: 2-4 business days out
- MEDIUM priority: 3-5 business days out
- Stagger same-day: 10:00, 10:15, 10:30, 10:45 (15-min increments)

## Cron Automation
```bash
hermes cronjob create --name "Daily Case Sweep" \
  --schedule "0 7 * * *" \
  --prompt "Run case_followup_orchestrator.py for all active cases with follow_up <= today. Update frontmatter to next business day, re-create GCal events with --update. Report HIGH priority overdue count." \
  --script "vault/scripts/case_followup_orchestrator.py" --no-agent
```

## Files
- `vault/scripts/case_followup_orchestrator.py` — orchestrator
- `vault/scripts/push_gcal.py` — GCal API (load_env, get_calendar_service, build_event)
- `vault/_cases/active/*.md` — case frontmatters (follow_up, followup_event_id)
- `vault/_kilo/LUSINE_TODO_Kanban.md` — Kanban "Follow-up Today" column
- `vault/_kilo/ACTIVITY_LOG.md` — activity log table

## Gotchas
- `--update` deletes old event by `followup_event_id` in frontmatter; if missing, searches by slug
- 404 on delete is OK (event already gone) — orchestrator warns but continues
- Kanban column "## Follow-up Today" must exist; orchestrator creates if missing
- If GCal auth fails, case file still updated — retry with same `--slug`