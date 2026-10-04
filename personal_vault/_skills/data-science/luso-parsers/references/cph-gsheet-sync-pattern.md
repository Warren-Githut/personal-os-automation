# CPH → GSheet Sync Pattern (02_MASTER_CPH)

Captured 2026-07-08. Reusable whenever a vault-computed value must be pushed back
into a Google Sheet that another pipeline reads.

## Context

`/ops-col` (`vault/scripts/ops_col.py`) reads `02_MASTER_CPH` (gid `871133523`) to get
CPH rates, then computes wage = Σ(hours × CPH). The CPH source of truth moved to
`cph.json` + `12_Wage_Structure_by_Role_Monthly.md`. To keep `/ops-col` working without
manual GSheet edits, `payroll_cph.py` pushes CPH → GSheet automatically after each run.

## SSOT chain

```
HR XLSX → payroll_cph.py → cph.json + keeper md
                             ↓ [auto, sync_cph_gsheet.py]
                       GSheet 02_MASTER_CPH (A1:I, 9-col template)
                             ↑ read by ops_col.py (/ops-col)
```

## Sync script contract (`parsers/sync_cph_gsheet.py`)

- Reads `_accumulation/cph.json`.
- For each month (or `ref_period` arg), for LU3/LU5/LU7: build row
  `[YEARMONTH, Store, FOH Management, FOH Floor Lead, FOH Service Agent, FOH Bar Team,
   BOH Leader, BOH Cook, Cleaner]`.
- **Record shape:** `cph.json` months are `{period, records:[{store, function, cph, ...}]}`
  — FLAT list, NOT nested `data[store][month][func]`. Build a `{function: cph}` map per
  store before assembling the row. (Common bug: `rec.get(role, 0)` returns 0 because the
  record key is `function`, not the role name.)
- **Sync method = FULL REBUILD (not upsert/append).** Read header (row 0), build ALL rows
  from `cph.json` sorted YEARMONTH DESC (newest-on-top), clear `A2:I1000`, write
  `header + rows` via `values.update(range A1:I{n})`. Idempotent: re-running produces an
  identical sheet. Vault is SSOT → GSheet is a mirror; rebuild (not incremental append)
  prevents drift from manual edits. `ops_col.py load_cph()` keys by YEARMONTH dict, so row
  order is irrelevant to the reader.
- **Vacant (cph=0)** → write `0`. Correct as actuals; `ops_col.py resolve_cph()` falls back
  to last-known-good month, so 0 never leaks as a false rate.

## Auth (CRITICAL)

- SA key: `vault/.private/lusine-calendar-sa-key.json`.
- Scope MUST be `https://www.googleapis.com/auth/spreadsheets` (WRITE), NOT `...readonly`.
  Set in `vault/10_OPERATION_DATA/scripts/modules/_utils.py` `fetch_sheets_api()`.
- OAuth token (`google_token.json`) for `ops_col.py` was **REVOKED** (invalid_grant) on
  2026-07-08 — do NOT rely on it for write. SA key is the durable path.
- SA email `google-calendar-service-accoun@warren-os.iam.gserviceaccount.com` must be
  shared as Editor on the GSheet (already done for `02_MASTER_CPH`).

## GSheet layout

Row 0 = header (9 cols, exact Warren template):
`YEARMONTH | Store | FOH Management (Restaurant Manager, Assistant Manager, Shift Manager)
| FOH Floor Lead (Captain, Supervisor) | FOH Service Agent (Service Agent, Retail Agent)
| FOH Bar Team (all barista positions) | BOH Leader (Sous Chef, CDP) | BOH Cook (Commis/Demi) | Cleaner`

Data rows from row 1. `load_cph()` in `ops_col.py` skips rows 0-1 (header), parses
`row[0].isdigit()` as YEARMONTH. Numbers may arrive with `,` (e.g. `81,173`) — `load_cph`
strips it; sync can write raw ints.

## Verify after any edit

Temp `hermes-verify-*.py` under `%TEMP%`:
1. Re-read `cph.json` → pick a known cell (e.g. LU5 FOH Management 202606 = 106827).
2. Read GSheet `02_MASTER_CPH!A1:I8` via SA key service.
3. Assert the matching `(202606, LU5)` row's col 2 == cph.json value.
4. Assert SA key `scopes` includes `spreadsheets` (not readonly).

## Pitfalls

- **Wrong record key** (`rec.get(role)` instead of building `{function: cph}` map) → all
  synced rows = 0. Caught only by cross-checking GSheet vs cph.json.
- **Double `vault/` path** in sync script: `VAULT / "vault" / ".private"` → 404. VAULT is
  already the project root; use `VAULT / ".private"`.
- **Readonly SA scope** → write fails silently or with 403. Always verify scope before
  declaring sync "done".
