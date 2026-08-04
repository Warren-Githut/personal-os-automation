---
name: gsheet-row-ops
description: "Delete a GSheet row via batchUpdate (deleteDimension)."
version: 1.0.0
trigger: need to delete a specific Google Sheet row; the google-workspace helper cannot (only get/update/append/create)
category: productivity
related_skills: [google-workspace, gsheet-personal-sync]
---

# gsheet-row-ops — Google Sheets Row-Level Operations

> The bundled `google-workspace` skill's `sheets` subcommand exposes: `get`, `update`, `append`, `create`. For **row deletion** (`deleteDimension`), insertion (`insertDimension`), or other `spreadsheets.batchUpdate` operations, you need the Sheets REST API directly.

## Use Case

Delete a specific row from a Google Sheet (e.g., remove a test data row before re-testing an E2E pipeline).

## Prerequisites

- `google_api.py` script from `google-workspace` skill (provides credentials)
- Google Sheets API v4 (`googleapiclient`)

## Steps

### Step 1: Find the Sheet's internal sheetId

Sheets can have multiple tabs; `sheetId` is NOT the tab name but an internal integer. Get it via the API:

```python
from googleapiclient.discovery import build
import importlib.util

spec = importlib.util.spec_from_file_location('gapi', str(GOOGLE_API_SCRIPT_PATH))
gmod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gmod)

creds = gmod.get_credentials()
service = build('sheets', 'v4', credentials=creds)

meta = service.spreadsheets().get(
    spreadsheetId='YOUR_SPREADSHEET_ID',
    fields='sheets.properties'
).execute()

for s in meta['sheets']:
    p = s['properties']
    print(f'{p["title"]}: sheetId={p["sheetId"]}')
```

### Step 2: Find the 0-indexed row to delete

Use `sheets get` to read the target column, then find your target row index (0-indexed, excluding header row):

```python
# Data row 0 = first data row = sheet row 2 (after header)
# Read column A, find target_date, get its index
row_0based = 49  # example
```

### Step 3: Delete the row via batchUpdate

```python
body = {
    'requests': [{
        'deleteDimension': {
            'range': {
                'sheetId': TARGET_SHEET_ID,   # from Step 1
                'dimension': 'ROWS',
                'startIndex': row_0based,     # 0-indexed, inclusive
                'endIndex': row_0based + 1    # exclusive
            }
        }
    }]
}
result = service.spreadsheets().batchUpdate(
    spreadsheetId='YOUR_SPREADSHEET_ID',
    body=body
).execute()
```

### Common Pitfalls

| Problem | Cause | Fix |
|---------|-------|------|
| `No grid with id: 0` | Assuming sheetId=0 | Get the real sheetId from `spreadsheets.get` |
| `HttpError 400: Invalid requests` | startIndex/endIndex wrong | Must be 0-indexed, endIndex exclusive |
| Row deleted but data shifted | DeleteDimension shifts all rows below up | Verify surrounding rows after op |
| `HttpError 409` | Another API consumer active | Same 409 rule as Telegram getUpdates — serialize access |

## References

- Google Sheets API v4: [spreadsheets.batchUpdate](https://developers.google.com/sheets/api/reference/rest/v4/spreadsheets/batchUpdate)
- `deleteDimension` request: [DeleteDimensionRequest](https://developers.google.com/sheets/api/reference/rest/v4/spreadsheets/request#DeleteDimensionRequest)
