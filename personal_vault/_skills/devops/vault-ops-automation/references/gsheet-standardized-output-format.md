# GSheet Parser Standardized Output Format

**Mandatory for all automated GSheet parsers in `vault/10_OPERATION_DATA/parsers/`.**

---

## Log Entry Format (Mandatory)

Every parser MUST produce entries in this exact structure:

```markdown
## YYYY-WXX | DD/MM–DD/MM/YYYY

### 📋 Executive Summary
- **System**: [key metric] | [pass rate] | [total volume] | [total rev]
- **Top concern**: [specific issue with store names + %] OR "All stores within acceptable range"
- **Key Takeaway**: [actionable conclusion: "urgent X needed" / "monitor Y" / "maintain current ops"]

### ⚡ Flags / Systemwide Analysis
- [flag emoji] [store] [specific metric] — [context]
- [flag emoji] [aggregate metric] — [threshold crossed]
- [flag emoji] [system-wide pattern] — [cross-store correlation]

### Weekly Roll-up (Δ vs WXX)
| Store | Rev | Hours | COL% | Δ Rev | Δ Hrs | Δ COL | Pass |
|---|---|---|---|---|---|---|---|

### Daily Detail — StoreName
| Date | Day | Rev (tr) | Hrs | COL% | SPLH (VND) | vs LW | Status |
|---|---|---|---|---|---|---|---|

---

```

---

## Rules (Enforced)

| Rule | Description |
|------|-------------|
| **Executive Summary = 3 bullets** | System, Top concern, Key Takeaway — exactly 3 bullets, no more no less |
| **Systemwide first** | Flags, roll-up, summary tables BEFORE any store-level breakdown |
| **Store-level second** | Per-store daily/hourly/detail tables AFTER systemwide |
| **Newest on top** | Prepend/replace by `week_id` (`## YYYY-WXX \| ...`) |
| **Standard flags** | 🔴 >red threshold, 🟡 near threshold, ✅ pass |
| **Delta vs prev week** | Use `prev_parsed` parsed from log file (see `gsheet-log-prev-week-parse.md`) |
| **Monthly Summary block** | On month boundary (see COL parser for pattern) |
| **No duplicate weeks** | Replace existing `week_id` block; never duplicate |

---

## Entry Lifecycle

1. **Fetch** → GSheet via gviz API
2. **Filter** → rows in current Mon-Sun week (`week_bounds()`)
3. **Parse** → `parse_row()` → list of dicts
4. **Aggregate** → `store_agg()` per store + system totals
3. **Delta** → `prev_parsed` from log file (previous week)
4. **Build** → `build_entry()` → markdown string (format above)
4. **Write** → prepend/replace by `week_id` after `<!-- PARSER INSERTION POINT -->` marker

---

## Executive Summary Rules (Exactly 3 Bullets)

| Bullet | Content |
|--------|---------|
| **1. System** | Key aggregate metric + pass rate + total volume + total rev |
| **2. Top concern** | Specific store(s) + metric + % + emoji; OR "All stores within acceptable range" |
| **3. Key Takeaway** | Actionable: "urgent X needed" / "monitor Y" / "maintain current ops" |

---

## Flags Format

| Emoji | Meaning | Example |
|-------|---------|---------|
| 🔴 | Above red threshold / critical | `🔴 LU3 COL avg 22.3% — above red threshold` |
| 🟡 | Near threshold / warning | `🟡 LU5 COL avg 17.1% — near red threshold` |
| ✅ | Pass / healthy | `✅ 19/21 pass days (90%)` |

---

## Delta Format (vs Previous Week)

| Field | Format | Example |
|-------|--------|---------|
| Rev | `{d_rev:+.1f}%` | `+4.5%` / `-3.2%` |
| Hours | `{d_hrs:+.0f}h` | `+12h` / `-5h` |
| COL% | `{d_col:+.1f}pp` | `+1.2pp` / `-0.8pp` |

---

## Monthly Summary (Month Boundary)

Triggered when `week_start.month != prev_month`. Output block:

```markdown
## Monthly Summary — MonthName YYYY

**System:** Xh total | COL% X.X% | X/Y pass days

| Store | Total | FOH+BAR | BOH | Cleaner | Days | COL% |
|---|---|---|---|---|---|---|

*Δ vs prev month: Total Xh (+X.X%) | COL% +X.Xpp*

---
```

---

## Prepend/Replace Logic

```python
# In run():
week_header = f"## {week_id}"
if week_header in existing:
    # Replace existing week block
    pattern = rf"(## {re.escape(week_id)}.*?)(?=\n## |\Z)"
    replaced = re.sub(pattern, "", existing, flags=re.DOTALL).strip()
    new_content = entry + "\n\n---\n\n" + replaced if replaced else entry + "\n"
else:
    # Insert after marker
    marker = "<!-- PARSER INSERTION POINT"
    if marker in existing:
        pos = existing.index(marker)
        new_content = existing[:pos] + entry + "\n\n" + existing[pos:]
    else:
        new_content = existing.rstrip() + "\n\n" + entry + "\n"
```

---

## Quick Checklist for New Parsers

- [ ] Executive Summary = exactly 3 bullets
- [ ] Systemwide analysis (flags + roll-up) BEFORE store-level
- [ ] Store-level breakdown AFTER systemwide
- [ ] `prev_parsed` from log implemented (delta works)
- [ ] Monthly Summary on month boundary
- [ ] Insert after `<!-- PARSER INSERTION POINT -->` marker
- [ ] No duplicate week entries (replace by `week_id`)
- [ ] `LUSINE_HEADLESS=1` supported (exit 0 on no data)
- [ ] `PYTHONPATH` set to `10_OPERATION_DATA/scripts/modules` for `_utils` import