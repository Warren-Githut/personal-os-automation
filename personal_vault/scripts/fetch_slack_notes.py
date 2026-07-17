#!/usr/bin/env python3
"""Fetch Slack brain-dump messages and write to Personal_OS inbox.

Usage: python fetch_slack_notes.py [--since TIMESTAMP] [--hours N]

Writes markdown files to personal_vault/_inbox/01_unprocessed/
Updates personal_vault/_inbox/.last_fetch with latest timestamp.

Auto-routes "Health log ..." entries to 10_PULSE/051_Sleep_Log.md (newest on top).

Env vars required:
  SLACK_BOT_TOKEN_LIFE  -- bot token for Warren_Life workspace
"""

import argparse
import os
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

try:
    from slack_sdk import WebClient
    from slack_sdk.errors import SlackApiError
except ImportError:
    print("slack-sdk not installed. Run: pip install slack-sdk", file=sys.stderr)
    sys.exit(1)


VAULT_ROOT = Path(__file__).parent.parent
INBOX_UNPROCESSED = VAULT_ROOT / "_inbox" / "01_unprocessed"
LAST_FETCH_FILE = VAULT_ROOT / "_inbox" / ".last_fetch"
SLEEP_LOG_FILE = VAULT_ROOT / "10_PULSE" / "051_Sleep_Log.md"

# Channel ID for Warren_Life #brain-dump (verify with conversations_list)
BRAIN_DUMP_CHANNEL = "C0B4U1YS44Q"  # Warren_Life #brain-dump
SLACK_WORKSPACE = "Warren_Life"

DOMAIN_KEYWORDS = {
    "health": ["bác sĩ", "bệnh viện", "khám", "xét nghiệm", "thuốc", "health", "doctor", "hospital", "blood", "pressure", "weight", "cân nặng", "huyết áp", "health log"],
    "trading": ["mua", "bán", "cổ phiếu", "stock", "trading", "portfolio", "giá", "khớp lệnh", "vnindex", "hose", "hnx", "fpt", "vnm", "vcb", "gas", "nlg", "eps", "bvps"],
    "family_gg": ["con", "bé", "gg", "con gái", "con trai", "vợ", "chồng", "family", "parent", "kid", "school", "trường", "mẫu giáo"],
    "growth": ["học", "đọc", "sách", "course", "skill", "growth", "learn", "study", "idea", "ý tưởng", "dự án", "prompt", "gemini", "video"],
}

# Sleep log pattern: "Health log june 14: :hospital: Health: 6h50 | quality 89 | 63kg | 17h | Huyết áp: 100/72"
SLEEP_LOG_PATTERN = re.compile(
    r"health\s*log\s+(?P<date>\w+\s+\d{1,2})\s*[:：]\s*"
    r":hospital:\s*Health:\s*(?P<sleep>\d+h\d+)\s*\|\s*"
    r"quality\s+(?P<quality>\d+)\s*\|\s*"
    r"(?P<weight>[\d.]+)kg\s*\|\s*"
    r"(?P<awake>\d+h?)\s*\|\s*"
    r"Huyết\s*áp:\s*(?P<bp>[\d/]+)",
    re.IGNORECASE
)

MONTH_MAP = {
    "january": 1, "jan": 1, "february": 2, "feb": 2, "march": 3, "mar": 3,
    "april": 4, "apr": 4, "may": 5, "june": 6, "jun": 6,
    "july": 7, "jul": 7, "august": 8, "aug": 8, "september": 9, "sep": 9,
    "october": 10, "oct": 10, "november": 11, "nov": 11, "december": 12, "dec": 12,
}


def classify_domain(text: str) -> str:
    text_lower = text.lower()
    for domain, keywords in DOMAIN_KEYWORDS.items():
        if any(kw in text_lower for kw in keywords):
            return domain
    return "uncategorized"


def parse_sleep_log(text: str):
    """Parse sleep log from Slack message text.
    
    Returns dict with: date, sleep, quality, weight, awake, bp
    or None if not a sleep log.
    """
    match = SLEEP_LOG_PATTERN.search(text)
    if not match:
        return None
    
    d = match.groupdict()
    
    # Parse date "june 14" -> "2026-06-14"
    parts = d["date"].lower().split()
    if len(parts) != 2:
        return None
    month_str, day_str = parts
    month = MONTH_MAP.get(month_str)
    if not month:
        return None
    try:
        day = int(day_str)
    except ValueError:
        return None
    
    year = datetime.now().year
    date_str = f"{year:04d}-{month:02d}-{day:02d}"
    
    return {
        "date": date_str,
        "sleep": d["sleep"],
        "quality": d["quality"],
        "weight": d["weight"],
        "awake": d["awake"],
        "bp": d["bp"],
    }


def load_last_fetch() -> float:
    if LAST_FETCH_FILE.exists():
        try:
            content = LAST_FETCH_FILE.read_text(encoding="utf-8").strip()
            if content:
                return float(content)
        except Exception:
            pass
    return 0.0


def save_last_fetch(ts: float) -> None:
    INBOX_UNPROCESSED.mkdir(parents=True, exist_ok=True)
    LAST_FETCH_FILE.write_text(str(ts), encoding="utf-8")


def get_channel_id(client, channel_name: str):
    for page in client.conversations_list(types="public_channel,private_channel", limit=200):
        for ch in page["channels"]:
            if ch["name"] == channel_name:
                return ch["id"]
    return None


def fetch_messages(client, channel_id: str, oldest_ts: int):
    """Fetch messages using integer timestamps (required by Slack API)."""
    messages = []
    cursor = None
    latest_ts = int(time.time())

    while True:
        try:
            kwargs = {
                "channel": channel_id, 
                "oldest": str(oldest_ts), 
                "latest": str(latest_ts), 
                "limit": 200
            }
            if cursor:
                kwargs["cursor"] = cursor
            resp = client.conversations_history(**kwargs)
            messages.extend(resp["messages"])
            if not resp.get("has_more"):
                break
            cursor = resp["response_metadata"]["next_cursor"]
        except SlackApiError as e:
            print(f"  Slack API error: {e.response['error']}", file=sys.stderr)
            break

    filtered = []
    for m in messages:
        if m.get("type") != "message":
            continue
        if m.get("bot_id"):
            continue
        if m.get("subtype") in ("channel_join", "channel_leave", "channel_archive", "channel_unarchive"):
            continue
        text = m.get("text", "").strip()
        if "has joined the channel" in text or "has left the channel" in text:
            continue
        if not text and not m.get("files"):
            continue
        filtered.append(m)

    return filtered


def write_inbox_file(msg, domain: str, ts: str, is_sleep_log: bool = False):
    dt = datetime.fromtimestamp(float(ts), tz=timezone.utc)
    date_str = dt.strftime("%Y-%m-%d_%H%M%S")

    filename = f"{date_str}_{domain}.md"
    filepath = INBOX_UNPROCESSED / filename

    frontmatter = f"""---
domain: {domain}
source: slack
slack_ts: {ts}
status: unprocessed
created: {dt.strftime("%Y-%m-%d")}
user: {msg.get('user', 'unknown')}
is_sleep_log: {str(is_sleep_log).lower()}
---

"""
    text = msg.get("text", "").strip() or "[no text content - files only]"
    content = frontmatter + text
    filepath.write_text(content, encoding="utf-8")
    return filepath


def main():
    parser = argparse.ArgumentParser(description="Fetch Slack brain-dump -> write to _inbox/01_unprocessed/, sleep logs marked with is_sleep_log=true")
    parser.add_argument("--since", type=str, help="ISO timestamp or unix timestamp to fetch from")
    parser.add_argument("--hours", type=int, default=24, help="Hours to look back if --since not provided")
    parser.add_argument("--channel", default="brain-dump", help="Channel name (default: brain-dump)")
    args = parser.parse_args()

    if args.since:
        try:
            since_ts = datetime.fromisoformat(args.since.replace("Z", "+00:00")).timestamp()
        except ValueError:
            try:
                since_ts = float(args.since)
            except ValueError:
                print(f"Invalid timestamp format: {args.since}", file=sys.stderr)
                sys.exit(1)
    else:
        last_fetch = load_last_fetch()
        if last_fetch > 0:
            since_ts = last_fetch + 0.001
        else:
            since_ts = time.time() - args.hours * 3600

    token = os.getenv("SLACK_BOT_TOKEN_LIFE")
    if not token:
        print("Error: SLACK_BOT_TOKEN_LIFE environment variable not set", file=sys.stderr)
        sys.exit(1)

    client = WebClient(token=token)

    print(f"Fetching #{args.channel} since {datetime.fromtimestamp(since_ts, tz=timezone.utc)}...")
    channel_id = BRAIN_DUMP_CHANNEL
    print(f"  Using channel ID: {channel_id}")

    # Use integer timestamp for Slack API (required!)
    oldest_ts = int(since_ts)
    messages = fetch_messages(client, channel_id, oldest_ts)
    print(f"Fetched {len(messages)} new messages")

    if not messages:
        print("No new messages")
        return

    written = 0
    sleep_logged = 0
    max_ts = since_ts

    for msg in messages:
        ts = msg["ts"]
        text = msg.get("text", "").strip()

        if not text and not msg.get("files"):
            continue

        # Try parse sleep log first (only for health domain messages)
        sleep_entry = None
        domain = classify_domain(text)
        
        is_sleep_log = False
        if domain == "health":
            sleep_entry = parse_sleep_log(text)
            if sleep_entry:
                is_sleep_log = True
                print(f"[SLEEP LOG DETECTED] {sleep_entry}")
                sleep_logged += 1
        
        # Normal inbox routing (with is_sleep_log flag)
        try:
            filepath = write_inbox_file(msg, domain, ts, is_sleep_log)
            marker = " [SLEEP]" if is_sleep_log else ""
            print(f"  Written: {filepath.name}{marker}")
            written += 1
            if float(ts) > max_ts:
                max_ts = float(ts)
        except Exception as e:
            print(f"  Error writing {ts}: {e}", file=sys.stderr)

    save_last_fetch(max_ts)
    print(f"Done! Written {written} files to {INBOX_UNPROCESSED}, {sleep_logged} sleep logs detected")
    print(f"Last fetch updated: {max_ts}")


if __name__ == "__main__":
    main()
