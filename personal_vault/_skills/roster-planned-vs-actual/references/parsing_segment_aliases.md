# Roster Parsing Segment Aliases

Mapping of Telegram text segments to structured fields.

## Alias table

| Telegram text | Structured field | Notes |
|---------------|-----------------|-------|
| Mgmt, Management, RM, ARM, Shift, SM | FOH_Mgmt | Management layer |
| Lead, Sup, Captain, Floor | FOH_Lead | Floor supervisors |
| SA, Service, Agent, Svc | FOH_SA | Service agents |
| Bar | FOH_Bar | Bar team |
| CDP, BOH_Lead | BOH_Lead | Chef de Partie |
| Cook, Commis, Demi, BOH, BOH_Cook | BOH_Cook | Line cooks |
| Cleaner, Clean | Cleaner | Dishwasher/cleaner |

## Parsing behavior

- Case-insensitive matching
- Multiple entries per line supported (comma-separated)
- "BOH" without qualifier defaults to BOH_Cook (ambiguous — prefer "CDP" + "Cook" split)
- Total (= Xxh) is mandatory — cross-checked against sum of segments
- Date format: DD/MM or DD-MM (numeric only)

## Store detection

Stores detected by header pattern: `LU3 Roster`, `LU5 Roster`, `LU7 Roster`.
Each header applies to all following day-lines until next store header.

## Week detection

Week start extracted from header: `15-21 Sep 2026` → 20260915.
File naming: `YYYYMMDD.txt` where date = Monday of that week.
