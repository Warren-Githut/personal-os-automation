---
purpose: "Report template for personal-vault-lint cron output"
last_used: 2026-06-23
---

# Lint Report Template

## Header
```
## PERSONAL VAULT LINT REPORT - YYYY-MM-DD
```

## Red-Flag Triggers Table
```
### RED-FLAG TRIGGERS
| Trigger | Status | Detail |
|---------|--------|--------|
| GG contact >7d | FLAG | Last GG contact logged: YYYY-MM-DD (N days). |
| Court follow-up | SAT HAN | follow_up: YYYY-MM-DD. Post-X result UNKNOWN. |
| Sleep <6h x 5 | OK | Last sleeps: ranges... |
| Daily_Pulse gap >7d | OK | Last entry: YYYY-MM-DD (N days). |
| Positions stale >6mo | N/A | 100% cash, no holdings. |
| Concentration >25% | N/A | No positions. |
```

## Vault Integrity Table
```
### VAULT INTEGRITY
| Item | Status |
|------|--------|
| Stub files | N files: list... |
| Inbox | OK | empty / N pending |
| ACTIVITY_LOG | gap / OK |
| Uncommitted changes | N files (M: X, D: Y, untracked: Z) |
| CONTEXT.md section 9 | Updated YYYY-MM-DD |
```

## Health Snapshot Table
```
### HEALTH SNAPSHOT (last N days)
| Date | Sleep | Quality | Weight | Fasting | BP |
|------|-------|---------|--------|---------|----|
| DD/MM | XhYm | N | Nkg | Nh | sys/dia |
```

## Court Case Section
```
### COURT CASE
- follow_up: YYYY-MM-DD (due tomorrow / overdue N days / OK)
- Post-[date] outcome: UNKNOWN / RECORDED
```

## Actions Needed
```
### ACTIONS NEEDED (khi Warren online)
1. CRITICAL {item} - description
2. IMPORTANT {item} - description
3. INFO {item} - description
```

## Status Icons (copy-paste)
- FLAG
- SAT HAN
- CHU Y
- OK
- N/A
- info

## Cron Mode Rules
- SILENT if ALL flags clear AND no actions
- NEVER silent if any red flag exists
- No execute_code, no questions
- Read-only report
