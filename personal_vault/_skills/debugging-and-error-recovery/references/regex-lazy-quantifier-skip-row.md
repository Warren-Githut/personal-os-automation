# Regex Lazy Quantifier Silently Skips First Data Row

## Symptom

A regex that captures markdown table rows returns data starting from the **second** row instead of the first. The first data row is silently consumed by a preceding lazy `.*?`.

## Example (gen_today.py, fixed 2026-07-04)

```python
# BAD — lazy .*? before capture group eats first data row
pattern = r"### Detail — Store\s*\n.*?\n\|.*?\n\|.*?(\n\|[^#]+)"
#                                                   ^^^^^^^^
#                              .*? tries empty → fails → expands →
#                              consumes "| 28/06 | CN | 44.2tr |..."
#                              capture starts from "| 27/06 | T7 |..."
```

```python
# GOOD — remove the lazy .*? before capture group
pattern = r"### Detail — Store\s*\n.*?\n\|.*?\n(\|[^#]+)"
#                                          ^^^^^^^
#                              capture starts from first data row
```

## Mechanism

In `\|.*?(\n\|[^#]+)`:
1. `\|` — matches the pipe at start of first data row
2. `.*?` — lazy, tries empty string
3. `(\n\|[^#]+)` — needs `\n|` next... but next char is space/date, not newline
4. `.*?` expands greedily until `(\n\|[^#]+)` can match
5. Eventually `.*?` consumes entire first data row
6. Capture group starts from second row's `\n|`

## Fix

Remove `\|.*?` before the capture group. Start capture directly from the first data row's pipe:

```
\|.*?(\n\|[^#]+)  →  (\|[^#]+)
```

## Detection

Verify by checking which row `entries[0]` returns. If it's the second-latest instead of the latest, suspect this pattern.

```python
# Test regex against known input
m = re.search(bad_pattern, text, re.DOTALL)
if m:
    first_row = m.group(1).split("\n")[1]  # skip leading \n
    print(first_row)  # Should be "| 28/06 | CN |...", not "| 27/06 |..."
```

## Prevention

- Never put a lazy `.*?` before a capture group that's meant to capture the first match
- If you need to skip to a specific line, use explicit anchors (`^`) or non-capturing groups before the capture
- Test with minimal input: 2-3 rows of data, confirm first row is captured
