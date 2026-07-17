#!/usr/bin/env python3
"""
Process sleep logs from _inbox/01_unprocessed/ or direct paste -> append to 10_PULSE/051_Sleep_Log.md.

Features:
- --paste: direct input from command line (Slack format)
- --watch: watch sleep log for manual edits (foreground, Ctrl+C to stop)
- --sync-gsheet: sync new entries to Google Sheet tab 'W-capture-sleep' (opt-in, confirmation required)
- Duplicate detection (date + sleep duration)
- Telegram notifications (disable with --no-notify)
"""

import argparse
import os
import re
import shutil
import signal
import sys
import time
import urllib.request
import json
import subprocess
from datetime import datetime
from pathlib import Path

# ============================================================================
# CONFIGURATION
# ============================================================================

VAULT_ROOT = Path("C:/Users/khoans/Documents/Personal_OS/personal_vault")
INBOX_UNPROCESSED = VAULT_ROOT / "_inbox" / "01_unprocessed"
INBOX_PROCESSED = VAULT_ROOT / "_inbox" / "02_processed_archived"
SLEEP_LOG = VAULT_ROOT / "10_PULSE" / "051_Sleep_Log.md"

# Google Sheets auto-sync (opt-in: pass --sync-gsheet)
GSHEET_ID = "1ZtIocc_Ic1z-tO1JGd4ZLnRB_7ZHHkvpJ5emaWJyeEE"
GSHEET_TAB = "W-capture-sleep"

def _find_google_api_script() -> Path | None:
    candidates = [
        os.environ.get("HERMES_HOME", ""),
        os.path.expanduser("~/.hermes"),
        "C:/Users/khoans/AppData/Local/hermes",
    ]
    for base in candidates:
        if not base:
            continue
        p = Path(base) / "skills" / "productivity" / "google-workspace" / "scripts" / "google_api.py"
        if p.exists():
            return p
    return None

# Regex: "Health log june 9: :hospital: Health: 7h15 | quality 93 | 63kg | 16h"
SLEEP_PATTERN = re.compile(
    r"Health log\s+(\w+\s+\d+).*?Health:\s*([\dh]+)\s*\|\s*quality\s*(\d+)\s*\|\s*([\d.]+kg)\s*\|\s*(\d+h)(?:\s*\|\s*Huyết áp:\s*([\d/]+))?",
    re.IGNORECASE
)

NOW = datetime.now()
CURRENT_YEAR = NOW.year
CURRENT_MONTH = NOW.month

MONTH_MAP = {
    'january': 1, 'jan': 1, 'february': 2, 'feb': 2, 'march': 3, 'mar': 3,
    'april': 4, 'apr': 4, 'may': 5, 'june': 6, 'jun': 6, 'july': 7, 'jul': 7,
    'august': 8, 'aug': 8, 'september': 9, 'sep': 9, 'october': 10, 'oct': 10,
    'november': 11, 'nov': 11, 'december': 12, 'dec': 12,
}

# Try importing telegram_notify
try:
    from telegram_notify import send_telegram
except ImportError:
    def send_telegram(message: str) -> bool:
        print("⚠️  telegram_notify not available, skipping Telegram")
        return False


# ============================================================================
# CORE PARSING FUNCTIONS
# ============================================================================

def parse_all_sleep_logs(content: str) -> list[dict]:
    """Parse ALL sleep metrics from health log content."""
    matches = SLEEP_PATTERN.findall(content)
    results = []

    for match in matches:
        date_str, sleep, quality, weight, fasting, bp = match

        parts = date_str.lower().strip().split()
        if len(parts) != 2:
            continue
        month_name, day_str = parts
        month = MONTH_MAP.get(month_name)
        if not month:
            continue
        day = int(day_str)

        year = CURRENT_YEAR
        if month > CURRENT_MONTH:
            year -= 1

        date_obj = datetime(year, month, day)
        date_key = date_obj.strftime("%Y-%m-%d")

        results.append({
            "date": date_key,
            "sleep": sleep.strip(),
            "quality": quality.strip(),
            "weight": weight.strip(),
            "fasting": fasting.strip(),
            "bp": bp.strip() if bp else None
        })

    return results


def get_duplicate_key(data: dict) -> str:
    """Generate duplicate key: date ONLY (not sleep duration)."""
    return data['date']


def is_duplicate(log_content: str, data: dict) -> tuple[bool, str]:
    """Check if entry with same date already exists in log.
    Returns (is_duplicate, existing_entry_key)"""
    dup_key = get_duplicate_key(data)
    # Check by date only (not sleep duration)
    pattern = rf"### {re.escape(data['date'])}"
    if re.search(pattern, log_content):
        return True, dup_key
    return False, ""


def build_entry(data: dict, source_file: str) -> str:
    bp_line = f" | Blood pressure: {data['bp']}" if data['bp'] else ""
    insight = generate_insight(data)

    return f"""### {data['date']}
**Source:** {source_file}
**Type:** text

Sleep: {data['sleep']} | Quality: {data['quality']}/100 | Fasting: {data['fasting']} | Weight: {data['weight']}{bp_line}

Insight:
{insight}

---"""


def generate_insight(data: dict) -> str:
    insights = []

    sleep_hours = parse_duration(data['sleep'])
    if sleep_hours < 7:
        insights.append(f"Sleep {data['sleep']} thấp hơn baseline 7h.")
    else:
        insights.append(f"Sleep {data['sleep']} đạt baseline.")

    q = int(data['quality'])
    if q >= 90:
        insights.append(f"Quality {data['quality']} vẫn ổn.")
    else:
        insights.append(f"Quality {data['quality']} cần cải thiện.")

    if data['bp']:
        systolic, diastolic = map(int, data['bp'].split('/'))
        if systolic < 90 or diastolic < 60:
            bp_status = "thấp"
        elif systolic > 140 or diastolic > 90:
            bp_status = "cao"
        else:
            bp_status = "bình thường"
        insights.append(f"BP {data['bp']} {bp_status}.")

    insights.append(f"Fasting {data['fasting']} consistent.")
    insights.append(f"Weight {data['weight']} ổn định.")

    return " ".join(insights) + " [MOD]"


def parse_duration(s: str) -> float:
    s = s.lower()
    if 'h' in s:
        parts = s.split('h')
        hours = int(parts[0])
        minutes = int(parts[1]) if len(parts) > 1 and parts[1] else 0
        return hours + minutes / 60
    return 0


# ============================================================================
# SLEEP LOG FILE OPERATIONS
# ============================================================================

def append_to_sleep_log(entries: list[str]) -> int:
    """Append new entries to sleep log (newest on top). Returns count."""
    log_content = SLEEP_LOG.read_text(encoding="utf-8")
    lines = log_content.split("\n")

    # Find insertion point: after first --- that follows "Rule:" / "Quy tắc:"
    insert_idx = 0
    for i, line in enumerate(lines):
        if ("Rule:" in line or "Quy tắc:" in line) and i > 0:
            for j in range(i + 1, len(lines)):
                if lines[j].strip() == "---":
                    insert_idx = j + 1
                    break
            break

    if insert_idx == 0:
        for i, line in enumerate(lines):
            if line.strip() == "---" and i > 0:
                insert_idx = i + 1
                break

    if insert_idx == 0:
        insert_idx = len(lines)

    # Prepend new entries (newest on top)
    new_block = "\n\n".join(entries)
    result_lines = lines[:insert_idx] + ["", new_block, ""] + lines[insert_idx:]

    # Update last_updated
    today = datetime.now().strftime("%Y-%m-%d")
    result = "\n".join(result_lines)
    result = re.sub(r'last_updated: \d{4}-\d{2}-\d{2}', f'last_updated: {today}', result)

    SLEEP_LOG.write_text(result, encoding="utf-8")
    return len(entries)


# ============================================================================
# GOOGLE SHEET SYNC (opt-in: --sync-gsheet)
# ============================================================================

def sync_to_gsheet(send_notify: bool = True) -> int:
    """Sync sleep log entries to Google Sheet tab 'W-capture-sleep' (idempotent).

    Reads existing dates from the sheet, appends only rows whose date is missing.
    Requires the --sync-gsheet flag at runtime (confirmation gate — Hermes only
    invokes this when Warren explicitly approves a GSheet write).

    Returns number of rows appended.
    """
    gapi = _find_google_api_script()
    if not gapi:
        print("⚠️  google_api.py not found, skipping GSheet sync")
        return 0

    try:
        existing = _gsheet_read_dates(gapi)
    except Exception as e:
        print(f"⚠️  GSheet read failed: {e}")
        return 0

    all_entries = _all_entries_from_log()
    rows_to_add = [e for e in all_entries if e["date"] not in existing]

    if not rows_to_add:
        print("✅ GSheet already up-to-date (no new rows)")
        return 0

    values = [_entry_to_row(e) for e in rows_to_add]
    try:
        _gsheet_append(gapi, values)
    except Exception as e:
        print(f"⚠️  GSheet append failed: {e}")
        return 0

    print(f"✅ Synced {len(rows_to_add)} row(s) to GSheet ({GSHEET_TAB})")
    if send_notify:
        send_telegram(f"✅ Synced {len(rows_to_add)} sleep row(s) to GSheet")
    return len(rows_to_add)


def _all_entries_from_log() -> list[dict]:
    """Parse all sleep entries from 051_Sleep_Log.md into row dicts (date ascending)."""
    content = SLEEP_LOG.read_text(encoding="utf-8")
    entry_re = re.compile(
        r"### (\d{4}-\d{2}-\d{2})\s*\n.*?Sleep: ([\dh]+) \| Quality: (\d+)/100 \| Fasting: (\d+h) \| Weight: ([\d.]+kg) \| Blood pressure: ([\d/]+)",
        re.DOTALL,
    )
    rows = []
    for m in entry_re.finditer(content):
        date, sleep, qual, fasting, weight, bp = m.groups()
        parts = sleep.split('h')
        h = int(parts[0]); mm = int(parts[1]) if len(parts) > 1 and parts[1] else 0
        total_h = round(h + mm / 60, 2)
        sys_bp, dia_bp = bp.split('/')
        rows.append({
            "date": date,
            "sleep_raw": sleep,
            "sleep_hours": total_h,
            "quality": int(qual),
            "fasting_h": int(fasting.replace('h', '')),
            "weight_kg": float(weight.replace('kg', '')),
            "bp_systolic": int(sys_bp),
            "bp_diastolic": int(dia_bp),
        })
    rows.sort(key=lambda r: r["date"])
    return rows


def _entry_to_row(e: dict) -> list:
    return [e["date"], e["sleep_raw"], e["sleep_hours"], e["quality"],
            e["fasting_h"], e["weight_kg"], e["bp_systolic"], e["bp_diastolic"]]


def _gsheet_read_dates(gapi: Path) -> set:
    cmd = [sys.executable, str(gapi), "sheets", "get", GSHEET_ID, f"'{GSHEET_TAB}'!A:A"]
    out = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    if out.returncode != 0:
        raise RuntimeError(out.stderr or out.stdout)
    data = json.loads(out.stdout)
    dates = set()
    for row in data:
        if row and row[0] and row[0] != "date":
            dates.add(str(row[0]))
    return dates


def _gsheet_append(gapi: Path, values: list) -> None:
    payload = json.dumps(values)
    cmd = [sys.executable, str(gapi), "sheets", "append", GSHEET_ID,
           f"'{GSHEET_TAB}'!A:H", "--values", payload]
    out = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    if out.returncode != 0:
        raise RuntimeError(out.stderr or out.stdout)


# ============================================================================
# PASTE / INBOX PROCESSING
# ============================================================================

def _ask_sync_gsheet() -> bool:
    """Prompt Warren for GSheet sync confirmation. Returns True if approved."""
    try:
        ans = input("\n🔄 Sync GSheet (W-capture-sleep)? Gõ 'ok' để đồng bộ, hoặc Enter để bỏ qua: ").strip().lower()
    except EOFError:
        # Non-interactive context (piped input) — default to NO sync, safe.
        print("   (non-interactive: skip GSheet sync)")
        return False
    if ans in ("ok", "yes", "y", "đồng ý", "dong bo"):
        return True
    return False


def process_paste(text: str, send_notify: bool = True) -> int:
    """Process direct paste input. Returns number of entries added.
    After writing to vault, prompts for GSheet sync confirmation."""
    print("📋 Processing paste input...")
    parsed_logs = parse_all_sleep_logs(text)

    if not parsed_logs:
        print("⚠️  No sleep data found in paste input.")
        return 0

    log_content = SLEEP_LOG.read_text(encoding="utf-8")

    new_entries = []
    skipped = 0

    for data in parsed_logs:
        is_dup, _ = is_duplicate(log_content, data)
        if is_dup:
            msg = f"⚠️ Duplicate sleep log for {data['date']} with sleep {data['sleep']}, skipped"
            print(msg)
            if send_notify:
                send_telegram(msg)
            skipped += 1
            continue

        source = "direct_paste"
        entry = build_entry(data, source)
        new_entries.append(entry)
        log_content += f"\n\n{entry}"
        print(f"✅ Parsed: {data['date']} ({data['sleep']})")

    if not new_entries:
        print(f"No new entries added. Skipped {skipped} duplicates.")
        return 0

    count = append_to_sleep_log(new_entries)
    print(f"✅ Vault updated: +{count} entry(ies)")

    if _ask_sync_gsheet():
        synced = sync_to_gsheet(send_notify)
        if synced:
            print(f"   GSheet: +{synced} row(s)")
    else:
        print("   GSheet: skipped (no sync)")

    if send_notify and count > 0:
        send_telegram(f"✅ Added {count} sleep log(s) from paste")

    return count


def process_file(f: Path, log_content: str) -> list[str]:
    """Process a single health log file. Returns new entries."""
    new_entries = []
    content = f.read_text(encoding="utf-8")
    parsed_logs = parse_all_sleep_logs(content)

    for data in parsed_logs:
        is_dup, _ = is_duplicate(log_content, data)
        if is_dup:
            msg = f"⚠️ Duplicate sleep log for {data['date']} with sleep {data['sleep']}, skipped"
            print(msg)
            send_telegram(msg)
            continue

        source = f"_inbox/01_unprocessed/{f.name}"
        entry = build_entry(data, source)
        new_entries.append(entry)
        log_content += f"\n\n{entry}"
        print(f"✅ Parsed: {f.name} -> {data['date']} ({data['sleep']})")

    if parsed_logs:
        dest = INBOX_PROCESSED / f.name
        shutil.move(str(f), str(dest))
        print(f"   Moved to processed")

    return new_entries


def process_inbox() -> int:
    """Process all health files in inbox.
    After writing to vault, prompts for GSheet sync confirmation."""
    INBOX_PROCESSED.mkdir(parents=True, exist_ok=True)

    health_files = list(INBOX_UNPROCESSED.glob("*health*.md"))
    if not health_files:
        print("No health log files found.")
        return 0

    log_content = SLEEP_LOG.read_text(encoding="utf-8")
    all_new_entries = []

    for f in sorted(health_files):
        new_entries = process_file(f, log_content)
        all_new_entries.extend(new_entries)
        for entry in new_entries:
            log_content += f"\n\n{entry}"

    if not all_new_entries:
        print("No new sleep entries to add.")
        return 0

    count = append_to_sleep_log(all_new_entries)
    print(f"✅ Vault updated: +{count} entry(ies)")

    if _ask_sync_gsheet():
        synced = sync_to_gsheet(send_notify=True)
        if synced:
            print(f"   GSheet: +{synced} row(s)")
    else:
        print("   GSheet: skipped (no sync)")

    return count


# ============================================================================
# FILE WATCHING (manual edit detection)
# ============================================================================

def watch_sleep_log(send_notify: bool = True):
    """Watch sleep log file for manual edits. Runs until Ctrl+C."""
    print(f"👀 Watching {SLEEP_LOG} for changes... (Ctrl+C to stop)")

    last_mtime = SLEEP_LOG.stat().st_mtime
    last_content = SLEEP_LOG.read_text(encoding="utf-8")

    def signal_handler(sig, frame):
        print("\n👋 Stopping watch...")
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)

    while True:
        try:
            current_mtime = SLEEP_LOG.stat().st_mtime
            if current_mtime != last_mtime:
                time.sleep(0.5)
                new_content = SLEEP_LOG.read_text(encoding="utf-8")

                if new_content != last_content:
                    new_entries = extract_new_entries(last_content, new_content)
                    if new_entries:
                        for entry in new_entries:
                            print(f"📝 Manual edit detected: new entry for {entry['date']}")
                            if send_notify:
                                send_telegram(f"✅ Manual sleep log detected for {entry['date']}")

                last_mtime = current_mtime
                last_content = new_content

            time.sleep(1)
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"⚠️  Watch error: {e}")
            time.sleep(5)


def extract_new_entries(old_content: str, new_content: str) -> list[dict]:
    """Extract newly added entries by comparing content."""
    old_blocks = set(re.findall(r'### (\d{4}-\d{2}-\d{2})', old_content))
    new_blocks = set(re.findall(r'### (\d{4}-\d{2}-\d{2})', new_content))
    added = new_blocks - old_blocks

    entries = []
    for date in added:
        pattern = rf"### {re.escape(date)}.*?(?=\n### |\Z)"
        match = re.search(pattern, new_content, re.DOTALL)
        if match:
            entry_text = match.group(0)
            sleep_match = re.search(r"Sleep: ([\dh]+)", entry_text)
            data = {"date": date, "sleep": sleep_match.group(1) if sleep_match else "?"}
            entries.append(data)
    return entries


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

def main():
    parser = argparse.ArgumentParser(description="Process sleep logs -> 051_Sleep_Log.md")
    parser.add_argument("--paste", type=str, help="Direct paste input (Slack format)")
    parser.add_argument("--watch", action="store_true", help="Watch sleep log for manual edits")
    parser.add_argument("--no-notify", action="store_true", help="Disable Telegram notifications")
    args = parser.parse_args()

    send_notify = not args.no_notify

    if args.watch:
        watch_sleep_log(send_notify)
    elif args.paste:
        process_paste(args.paste, send_notify)
    else:
        process_inbox()


if __name__ == "__main__":
    main()
