# push_gcal.py .env Path Mismatch

> Hit: 2026-07-03 Menu GP monthly calendar creation

## Problem

`push_gcal.py` reads `GOOGLE_SA_CREDENTIALS` and `GOOGLE_CALENDAR_ID` from `vault/.env`. The `.env` default path points to:

```
vault/_private/lusine-calendar-sa-key.json
```

But the actual SA key lives at:

```
%LOCALAPPDATA%/hermes/google_service_account.json
# = C:\Users\khoans\AppData\Local\hermes\google_service_account.json
```

## Fix

Pass env vars explicitly in the terminal command — do NOT rely on `.env` defaults:

```bash
GOOGLE_SA_CREDENTIALS="/c/Users/khoans/AppData/Local/hermes/google_service_account.json" \
GOOGLE_CALENDAR_ID="nguyen.s.khoa@gmail.com" \
python3 vault/scripts/push_gcal.py \
  --summary "Event title" \
  --date YYYY-MM-DD --time HH:MM \
  --rrule "FREQ=MONTHLY;BYMONTHDAY=5"
```

## Root Cause

The `.env` file at `vault/.env` has a stale path. The SA key was moved to `%LOCALAPPDATA%/hermes/` but `.env` wasn't updated. Rather than fixing .env (which may have other side effects), pass env vars per-command.
