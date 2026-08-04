# Revenue Formatting Truncation Bug

## Discovery (2026-06-22 — Hourly Cover Parser v4.5)

Warren noticed revenue numbers in the Executive Summary were off: 
`688.0tr` displayed but actual net revenue was `688,919,720`.

## Root Cause

Python f-string formatting with `int()` truncation:

```python
# WRONG — int() truncates toward zero
f"... | {int(sys_r/1e6):.1f}tr |"
# sys_r = 688,919,720
# sys_r/1e6 = 688.91972
# int(688.91972) = 688    ← truncates, loses 919,720 VND
# f"{688:.1f}" = "688.0"  ← displays as 688.0tr

# CORRECT — let :.1f round naturally
f"... | {sys_r/1e6:.1f}tr |"
# sys_r/1e6 = 688.91972
# f"{688.91972:.1f}" = "688.9"  ← proper rounding
# displays as 688.9tr
```

The `:.1f` format specifier ALREADY rounds to 1 decimal. Adding `int()` on top pre-truncates the value before formatting, destroying precision.

## Impact

Up to ~1M VND lost per revenue display. With 4 display locations per parser (Executive Summary, Weekly Roll-up × 3 stores + system, MTD section), the cumulative display error could be substantial.

## Fix Checklist

Search all parsers for the pattern `{int(X/1e6):.1f}` and replace with `{X/1e6:.1f}`:

| Pattern | Fix |
|---------|-----|
| `{int(sys_r/1e6):.1f}tr` | `{sys_r/1e6:.1f}tr` |
| `{int(t['revenue_net']/1e6):.1f}tr` | `{t['revenue_net']/1e6:.1f}tr` |
| `{int(sn/1e6):.1f}tr` | `{sn/1e6:.1f}tr` |
| `{int(sn/NET_FACTOR/1e6):.1f}tr` | `{sn/NET_FACTOR/1e6:.1f}tr` |

## Prevention

- When writing revenue display code, test with a borderline value: `f"{688919720/1e6:.1f}"` should give `"688.9"`, not `"688.0"`
- Code review item: flag any `int(x / divisor)` before a format spec
- The format spec (`:.1f`, `:.0f`, etc.) rounds correctly on its own — only use `int()` when you need integer arithmetic, not for display