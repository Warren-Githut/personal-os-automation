# Custom Data Handler Pattern (Quick Wins Tracking)

## Session Origin
Created 2026-06-30 — Warren needed operators to send daily tracking numbers via Telegram, auto-logged to Google Sheets.

## Message Flow
```
Operator → @lusine_work_bot → handle_text()
    → quick_wins_handler.handle_quick_wins_message()
        → parse_message() or parse_template()    # Parse structured data
        → update_sheet()                         # Write to Google Sheets via SA key
    → Reply "✅ Đã ghi: LU5 Sunset Hour = 14"
```

## Bot Hook (in telegram_bot.py handle_text, BEFORE NL handler)
```python
from quick_wins_handler import handle_quick_wins_message
qw_result = handle_quick_wins_message(text)
if qw_result:
    await message.answer(qw_result, parse_mode=ParseMode.HTML)
    return
```

## Two Supported Formats

### Format 1: Single line
```
<STORE> <metric>: <number>
```
| Message | Store | Metric | Value |
|---------|-------|--------|-------|
| `LU5 tối: 14` | LU5 | Sunset Hour | 14 |
| `LU5 sunset: 14` | LU5 | Sunset Hour | 14 |
| `LU5 chiều: 14` | LU5 | Sunset Hour | 14 |
| `LU3 lunch: 8` | LU3 | POWER LUNCH | 8 |
| `LU5 power: 6` | LU5 | POWER LUNCH | 6 |
| `LU7 powerlunch: 38` | LU7 | POWER LUNCH | 38 |
| `LU7 sáng: 52` | LU7 | Morning Kickstart | 52 |
| `LU7 morning: 52` | LU7 | Morning Kickstart | 52 |
| `LU5 upsell: 5` | LU5 | Staff Upsell | 5 |

Colon after metric is optional: `LU5 tối 14` works too.

### Format 2: Multi-line template (emoji)
```
📊 QUICK WINS — 30/06 (Thứ 3)

🌅 Sunset Hour LU5: [14] / 14
🍽 POWER LUNCH LU3: [8] / 10
🍽 POWER LUNCH LU5: [6] / 10
🍽 POWER LUNCH LU7: [38] / 5
☕ Morning Kickstart LU7: [52] / 29
```

Parser scans each line for `[value]` pattern and maps display labels to (store, metric) via `_TEMPLATE_LINE_MAP`.

### Slash Commands
| Command | Response |
|---------|----------|
| `/summary` | Reads today's values from Sheet, returns HTML table |
| `/help` | Updated to include Quick Wins syntax |
| `/start` | Updated to include Quick Wins syntax |

## Google Sheet Structure

All data writes to tab **'Quick Wins Tracker'** in LU_COL_ENGINE_V4 sheet.
Sheet ID: `1ZtIocc_Ic1z-tO1JGd4ZLnRB_7ZHHkvpJ5emaWJyeEE`

### Section → Row mapping (verified 2026-06-30, after LU7 column insertion)

| Section | Header row | Data start (July 1) | Columns |
|---------|-----------|---------------------|---------|
| Sunset Hour LU5 | 2 | 3 | C=value, D=target(14) |
| POWER LUNCH LU3 | 36 | 37 | C=LU3, D=LU5, E=LU7, F=target(50) |
| Morning Kickstart LU7 | 70 | 71 | C=value, D=target(29) |
| Staff Upsell | 104 | 113 (3 rows/store/day) | C=value, D=target(50) |

**Important:** When inserting a new column (e.g. LU7 column E into POWER LUNCH), all sections BELOW shift right. The section row numbers above are POST-insertion.

### Row calculation
```python
july_first = date(2026, 7, 1)
day_offset = (target_date - july_first).days  # 0 = July 1, 30 = July 31
row = data_start + day_offset
```

**Pitfall:** For dates BEFORE July 1 (e.g. June 30), day_offset is negative. The current handler does NOT clamp — it writes to a row before the data area. Fix: either skip pre-July dates or add a buffer section.

### Staff Upsell row formula
```python
base_row = 113  # July 1, LU3
store_order = {"LU3": 0, "LU5": 1, "LU7": 2}
row = 113 + (day_offset * 3) + store_order[store]
```

### Latest targets (Jun-Jul 2026 Quick Wins)
| Initiative | Baseline | Week 1 | July Target |
|------------|----------|--------|-------------|
| POWER LUNCH LU3+LU5+LU7 | ~0 | 50/store/tuần | 50/store/tuần |
| Sunset Hour LU5 | 78/tuần (11/ngày) | 95/tuần | 100/tuần |
| Morning Kickstart LU7 | 171/tuần (24/ngày) | 205/tuần | 205/tuần |
| Staff Upsell | ~0 | 30/tuần | 50/tuần |

**Note:** All targets proved to use `/tuần` unit, not `/day` as originally written in the case file. The `/day` values were inadvertently used when `/tuần` was meant (e.g. 78/tuần ≠ 78/day). Verify unit consistency when setting new targets.

## Vietnamese Diacritics
The `\w+` regex matches diacritic characters, but dict keys use ASCII (e.g. key `"toi"` but user types `"tối"`). Normalize via character map before dict lookup. See SKILL.md for the full `_VIETNAMESE_MAP`.

## Multi-line Template Parser Design

```python
_TEMPLATE_LINE_MAP = {
    "sunset hour lu5": ("LU5", "toi"),
    "power lunch lu3": ("LU3", "lunch"),
    "power lunch lu5": ("LU5", "lunch"),
    "power lunch lu7": ("LU7", "lunch"),
    "morning kickstart lu7": ("LU7", "sang"),
}

def parse_template(text: str) -> list[dict]:
    results = []
    for line in text.strip().split('\n'):
        m = re.search(r'\[(\s*)(\d+)(\s*)\]', line)
        if not m:
            continue
        value = int(m.group(2))
        label_part = line[:m.start()].strip()
        label_clean = re.sub(r'^[^\w]+', '', label_part).strip().lower()
        for template_label, (store, metric) in _TEMPLATE_LINE_MAP.items():
            if template_label in label_clean:
                results.append({"store": store, "metric": metric, "value": value})
                break
    return results
```

**Key insight:** The dispatch order is template → single-line. Template is tried first because it has a distinct `[value]` pattern that won't match single-line messages. Single-line messages won't have brackets so they fall through.

## Key Files
- `vault/scripts/lusine-ops/lusine_ops/quick_wins_handler.py` — the handler module (parse_template, parse_message, update_sheet, get_summary)
- `vault/scripts/lusine-ops/lusine_ops/telegram_bot.py` — bot with QW hook registered
- Sheet: `LU_COL_ENGINE_V4` → tab `Quick Wins Tracker`
- `vault/_cases/active/2026-06-28_quick-wins-june-july-internal-execution-plan.md` — case file with targets

## Config: SECTION_CONFIG structure
```python
SECTION_CONFIG = {
    ("LU3", "lunch"): {"section": "powerlunch", "data_start": 37, "value_col": "C", "target_col": "F"},
    ("LU5", "lunch"): {"section": "powerlunch", "data_start": 37, "value_col": "D", "target_col": "F"},
    ("LU7", "lunch"): {"section": "powerlunch", "data_start": 37, "value_col": "E", "target_col": "F"},
    ("LU5", "toi"):   {"section": "sunset",     "data_start": 3,  "value_col": "C", "target_col": "D"},
    ("LU7", "sang"):  {"section": "morning",    "data_start": 71, "value_col": "C", "target_col": "D"},
}
```

All store + alias variations need entries. `SECTION_CONFIG` is the single source of truth for sheet mapping.

## Template Message (copy-paste for operator)
```
📊 QUICK WINS — <date> (<day>)

🌅 Sunset Hour LU5: [  ] / 14
🍽 POWER LUNCH LU3: [  ] / 10
🍽 POWER LUNCH LU5: [  ] / 10
🍽 POWER LUNCH LU7: [  ] / 10
☕ Morning Kickstart LU7: [  ] / 29
```

## Bot Restart (avoids MSYS path mangling)
```python
import subprocess, os
with open(r'C:\Users\khoans\AppData\Local\LUsineWorkBot\.env', encoding='utf-8-sig') as f:
    env_lines = f.readlines()
env = os.environ.copy()
for ln in env_lines:
    ln = ln.strip()
    if ln and not ln.startswith('#') and '=' in ln:
        k, v = ln.split('=', 1)
        env[k.strip()] = v.strip()
env['PYTHONPATH'] = r'C:\Users\khoans\Documents\Warren_OS_Local\vault\scripts'
proc = subprocess.Popen(
    [r'C:\Users\khoans\AppData\Local\Programs\Python\Python312\python.exe',
     '-m', 'lusine_ops.telegram_bot'],
    cwd=r'C:\Users\khoans\Documents\Warren_OS_Local\vault\scripts\lusine-ops',
    env=env, creationflags=subprocess.CREATE_NO_WINDOW,
    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
)
print(f'Bot PID: {proc.pid}')
```

**Always use Python subprocess from Hermes terminal** — never `cmd /c "start ..."` from bash, which MSYS path-mangles backslashes.

## Pitfalls Logged
1. **MSYS path mangling** — running `cmd /c "start ..."` from bash strips backslashes. Use Python subprocess with native Windows paths.
2. **Date before July 1** — negative day_offset writes to wrong row. Handle with clamp or guard.
3. **SA key can't create sheets** — service account lacks Drive scope. Add tabs to existing sheet instead.
4. **Row positions shift on column insert** — inserting a column shifts all content right. Update data_start values after structural edits.
5. **.bat :loop creates zombie processes** — killing python.exe doesn't kill the bat's cmd window. Use Python subprocess launch instead.
6. **Unit confusion (/day vs /tuần)** — targets in this project inadvertently used /day when /tuần was meant. Always verify units when setting new targets.
7. **Pydantic version conflict** — Hermes agent venv may interfere when launching bot from bash. Use `.bat` launcher or explicit PYTHONPATH to avoid.
