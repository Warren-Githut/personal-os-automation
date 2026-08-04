# L'Usine Excel Floating-Point Cleanup Pattern

> Recurring issue: L'Usine Export-to-Excel produces floating-point artifacts.
> Last triggered: Extra Hours June 2026 ingest (2026-07-02)

## Problem

All L'Usine operational Excel data (extra hours, working hours, etc.) produces
floating-point precision artifacts during export, e.g.:

```
82.99999999999997   → expected 83
24.999999999999993  → expected 25
1.9999999999999982  → expected 2
2.0000000000000018  → expected 2
```

These are **NOT data errors** — they are IEEE 754 floating-point representation
artifacts from how Excel stores calculation results.

## Pattern

```
# Python
OT_clean = round(raw_value, 1)

# For integer-ish values that should be whole:
OT_clean = round(raw_value)  # if all values should be integers
```

## When to apply

- Every extra hours / OT sheet
- Every working hours / rostering sheet
- Every COL (Cost of Labour) calculation
- Any L'Usine export where hours are computed via Excel formulas

## Historical examples

| Source Month | Raw Value | Cleaned |
|-------------|-----------|---------|
| June 2026 | 82.99999999999997 | 83.0 |
| June 2026 | 1.9999999999999982 | 2.0 |
| May 2026 | 320.49999999999994 | 320.5 |
| April 2026 | 49.99999999999999 | 50.0 |

## Do NOT

- Do NOT flag these as spreadsheet errors to Warren — they are normal float behavior
- Do NOT try to detect them via string matching — use `round(value, 1)` on every
  numeric column extracted from L'Usine Excel exports
