# Log-Based Previous Week Parsing

**Pattern: Extract previous week's data from log file to build `prev_parsed` for delta calculations.**

---

## Why Parse Log Instead of Re-fetching GSheet

- GSheet may only have current week's data
- Log file preserves historical weeks
- Faster (no network call)
- Immutable historical record

---

## Pattern: Extract Previous Week Block from Log

```python
def parse_prev_week_from_log(log_path: Path, current_week_start: date):
    """Parse previous week's data from existing log file."""
    try:
        content = log_path.read_text(encoding="utf-8")
        prev_week_start = current_week_start - timedelta(days=7)
        prev_iso_week = prev_week_start.isocalendar()[1]
        prev_week_id = f"{prev_week_start.year}-W{prev_iso_week:02d}"

        # Extract the section for previous week
        pattern = rf"(## {re.escape(prev_week_id)}.*?)(?=\n## |\Z)"
        match = re.search(pattern, content, re.DOTALL)
        if not match:
            return []

        week_block = match.group(1)
        return parse_week_block(week_block)
    except Exception as e:
        print(f"⚠️  Could not parse prev week from log: {e}")
        return []
```

---

## Parse Week Block into `parsed_rows` Format

```python
def parse_week_block(week_block: str):
    """Parse a week block from log into parsed_rows format."""
    parsed = []
    
    # Find store sections
    store_pattern = re.compile(r"### (LU3|LU5|LU7):.*?(?=\n### |\n### Weekly Roll-up|\Z)", re.DOTALL)
    for store_match in store_pattern.finditer(week_block):
        store = store_match.group(1)
        store_text = store_match.group(0)
        
        # Parse daily breakdown table
        day_table_match = re.search(r"\| Day \|.*?\n\|[-\s|]+\n(.*?)\n\n", store_text)
        if day_table_match:
            day_rows = day_table_match.group(1).strip().split("\n")
            day_map = {"T2": "mon", "T3": "tue", "T4": "wed", "T5": "thu", "T6": "fri", "T7": "sat", "CN": "sun"}
            for row in day_rows:
                if "|" in row:
                    parts = [p.strip() for p in row.split("|")[1:-1]]
                    if len(parts) >= 3:
                        day_label = parts[0]
                        covers = parts[1]
                        rev_str = parts[2]
                        day_short = day_map.get(day_label, day_label.lower())
                        try:
                            covers_val = int(covers) if covers and covers != "--" else 0
                        except ValueError:
                            covers_val = 0
                        try:
                            rev_val = float(rev_str.replace("tr", "").strip()) * 1e6 if "tr" in rev_str else 0
                        except ValueError:
                            rev_val = 0
                        if covers_val > 0 or rev_val > 0:
                            parsed.append({
                                "store": store,
                                "day": day_short,
                                "covers": covers_val,
                                "revenue": rev_val,
                            })
        
        # Parse peak day hourly if available
        peak_hourly_match = re.search(r"\*\*Peak day \(([^)]+)\) hourly:\*\*\n\| Hour \| Covers \| Revenue \|\n\|[-\s|]+\n(.*?)\n\n", store_text)
        if peak_hourly_match:
            peak_day_label = peak_hourly_match.group(1)
            peak_day_map = {"T2": "mon", "T3": "tue", "T4": "wed", "T5": "thu", "T6": "fri", "T7": "sat", "CN": "sun"}
            peak_day = peak_day_map.get(peak_day_label, peak_day_label.lower())
            
            hourly_rows = peak_hourly_match.group(2).strip().split("\n")
            for row in hourly_rows:
                if "|" in row:
                    parts = [p.strip() for p in row.split("|")[1:-1]]
                    if len(parts) >= 3:
                        hour_str = parts[0]
                        covers = parts[1]
                        rev_str = parts[2]
                        try:
                            hour = int(hour_str.replace(":00", ""))
                            covers_val = int(covers) if covers and covers != "--" else 0
                            rev_val = float(rev_str.replace("tr", "").strip()) * 1e6 if "tr" in rev_str else 0
                        except ValueError:
                            continue
                        if covers_val > 0 or rev_val > 0:
                            parsed.append({
                                "store": store,
                                "day": peak_day,
                                "hour": hour,
                                "covers": covers_val,
                                "revenue": rev_val,
                            })
    return parsed
```

---

## Usage in Parser `run()`

```python
def run():
    week_start, week_end = week_bounds()
    # ... fetch & parse current week ...
    
    prev_parsed = []
    if LOG_FILE.exists():
        prev_parsed = parse_prev_week_from_log(LOG_FILE, week_start)

    entry = build_entry(week_start, week_end, parsed, prev_parsed)
    # ...
```

---

## Hourly Cover Specifics

For hourly cover parser, `prev_parsed` format:
```python
[
    {"store": "LU3", "day": "mon", "covers": 100, "revenue": 1500000},
    {"store": "LU3", "day": "mon", "hour": 7, "covers": 50, "revenue": 500000},
    # ...
]
```

Must handle both daily and hourly entries in same list.

---

## Error Handling

```python
def parse_prev_week_from_log(log_path: Path, current_week_start: date):
    try:
        # ... parsing logic ...
        return parse_week_block(week_block)
    except Exception as e:
        print(f"⚠️  Could not parse prev week from log: {e}")
        return []  # Empty list = no delta, not a failure
```

Return empty list on error — delta calculation will show "baseline" instead of error.