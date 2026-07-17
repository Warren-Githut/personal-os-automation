#!/usr/bin/env python3
"""
Google Calendar Event Pusher — Service Account auth.
Pushes events to a shared Google Calendar using a Google Service Account.

Usage:
  python push_gcal.py --summary "Meeting" --date 2026-06-01 --time 14:30 --location "LU3" --tags "#ops,#meeting"

  python push_gcal.py --summary "All-day event" --date 2026-06-01 --tags "#hr"

Environment:
  GOOGLE_SA_CREDENTIALS  — path to service-account JSON key file (required)
  GOOGLE_CALENDAR_ID     — calendar email or ID to write to (default: "primary")
                           Must be a calendar shared with the service account.

Output:
  Prints JSON to stdout with event details on success.
  Exits with code 0 on success, 1 on error.
"""

import argparse
import json
import os
import sys
from dotenv import load_dotenv

from datetime import datetime, timedelta, timezone
from pathlib import Path

TZ_BANGKOK = timezone(timedelta(hours=7))

# Tag → Google Calendar colorId mapping
# https://developers.google.com/calendar/api/v3/reference/events#resource
TAG_COLORS = {
    "labour": "1",       # Lavender
    "marketing": "2",    # Sage
    "menu-cogs": "3",   # Grape
    "operations": "4",   # Tangerine
    "p-and-l": "5",      # Banana
    "lu3": "6",          # Tangerine
    "lu5": "7",          # Peacock
    "lu7": "8",          # Graphite
    "hr": "9",           # Blueberry
    "grabfood": "10",    # Basil
    "pccc": "11",        # Tomato
}

# Priority → color mapping
PRIORITY_COLORS = {
    "high": "11",    # Tomato (red)
    "medium": "5",   # Banana (yellow)
    "normal": "1",   # Lavender
}


def pick_color(tags: list[str], priority: str | None = None) -> str | None:
    """Pick the best Google Calendar colorId from tags or priority."""
    # Priority wins for urgency
    if priority and priority.lower() in PRIORITY_COLORS:
        return PRIORITY_COLORS[priority.lower()]
    # Otherwise pick first matching tag
    for tag in tags:
        clean = tag.strip().lower().lstrip("#").replace("-", "_").replace(" ", "_")
        # Also check without the lusine- prefix
        if clean in TAG_COLORS:
            return TAG_COLORS[clean]
        if clean.startswith("lu"):
            if clean in TAG_COLORS:
                return TAG_COLORS[clean]
    return None


def build_description(
    summary: str,
    tags: list[str],
    location: str | None = None,
    extra_desc: str | None = None,
) -> str:
    """Build a rich description from input parameters."""
    lines = []
    if extra_desc:
        lines.append(extra_desc)
        lines.append("")
    if tags:
        lines.append("🏷️ Tags: " + " ".join(tags))
    if location:
        lines.append("📍 Location: " + location)
    lines.append("")
    lines.append("---")
    lines.append(f"Pushed by L'Usine vault pipeline @ {datetime.now(TZ_BANGKOK).isoformat()}")
    return "\n".join(lines)


def parse_datetime(date_str: str, time_str: str | None) -> tuple[dict, bool]:
    """
    Parse date/time into Google Calendar event start/end dict.
    Returns (start_end_dict, is_all_day).
    """
    dt = datetime.strptime(date_str, "%Y-%m-%d")
    if time_str:
        hour, minute = map(int, time_str.split(":"))
        dt = dt.replace(hour=hour, minute=minute, tzinfo=TZ_BANGKOK)
        end_dt = dt + timedelta(hours=1)  # Default 1-hour duration
        return (
            {
                "start": {"dateTime": dt.isoformat(), "timeZone": "Asia/Bangkok"},
                "end": {"dateTime": end_dt.isoformat(), "timeZone": "Asia/Bangkok"},
            },
            False,
        )
    else:
        # All-day event
        return (
            {
                "start": {"date": date_str, "timeZone": "Asia/Bangkok"},
                "end": {"date": (dt + timedelta(days=1)).strftime("%Y-%m-%d"), "timeZone": "Asia/Bangkok"},
            },
            True,
        )


def build_event_body(args: argparse.Namespace) -> dict:
    """Build the Google Calendar event body from parsed arguments."""
    time_spec, is_all_day = parse_datetime(args.date, args.time)

    tags = args.tags if args.tags else []
    color_id = pick_color(tags, args.priority)

    body = {
        "summary": args.summary,
        "description": build_description(args.summary, tags, args.location, args.description),
        **time_spec,
    }

    if args.location:
        body["location"] = args.location
    if color_id:
        body["colorId"] = color_id
    if args.recurrence:
        body["recurrence"] = [f"RRULE:{args.recurrence}"]
    if tags:
        body.setdefault("extendedProperties", {})
        body["extendedProperties"]["private"] = {
            "tags": ",".join(tags),
            "source": "personal-vault",
        }

    return body


def push_event(service, calendar_id: str, body: dict) -> dict:
    """Push event to Google Calendar and return created event."""
    event = service.events().insert(
        calendarId=calendar_id,
        body=body,
    ).execute()
    return event


def get_calendar_service():
    """Build and return an authenticated Google Calendar service."""
    from google.auth import load_credentials_from_file
    from googleapiclient.discovery import build

    cred_path = os.environ.get("GOOGLE_SA_CREDENTIALS")
    if not cred_path:
        print("ERROR: GOOGLE_SA_CREDENTIALS env var not set", file=sys.stderr)
        sys.exit(1)

    cred_file = Path(cred_path)
    if not cred_file.exists():
        print(f"ERROR: Credentials file not found: {cred_file}", file=sys.stderr)
        sys.exit(1)

    creds, _ = load_credentials_from_file(
        str(cred_file),
        scopes=["https://www.googleapis.com/auth/calendar.events"],
    )

    return build("calendar", "v3", credentials=creds)


def main():
    load_dotenv(Path.home() / ".env")
    sys.stdout.reconfigure(encoding="utf-8")  # Fix Unicode print
    parser = argparse.ArgumentParser(
        description="Push event to Google Calendar via Service Account",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    parser.add_argument("--summary", required=True, help="Event title (required)")
    parser.add_argument("--description", default=None, help="Event description / notes")
    parser.add_argument("--date", required=True, help="Event date in YYYY-MM-DD format (required)")
    parser.add_argument("--time", default=None, help="Event time in HH:MM format (optional, 24h). Omitting creates all-day event.")
    parser.add_argument("--location", default=None, help="Event location (optional)")
    parser.add_argument("--tags", nargs="*", default=[], help="Tags (e.g., #ops #lu3). Used for color coding.")
    parser.add_argument("--priority", default=None, choices=["high", "medium", "normal"], help="Priority level (optional, affects color)")
    parser.add_argument("--recurrence", default=None, help='RRULE string (e.g., "FREQ=WEEKLY;BYDAY=MO")')
    parser.add_argument("--calendar-id", default=None, help="Calendar ID to push to (overrides GOOGLE_CALENDAR_ID env)")

    args = parser.parse_args()

    # Validate date format
    try:
        datetime.strptime(args.date, "%Y-%m-%d")
    except ValueError:
        print(f"ERROR: Invalid date format '{args.date}'. Use YYYY-MM-DD.", file=sys.stderr)
        sys.exit(1)

    # Validate time format if provided
    if args.time:
        try:
            datetime.strptime(args.time, "%H:%M")
        except ValueError:
            print(f"ERROR: Invalid time format '{args.time}'. Use HH:MM (24h).", file=sys.stderr)
            sys.exit(1)

    # Resolve calendar ID
    calendar_id = args.calendar_id or os.environ.get("GOOGLE_CALENDAR_ID", "primary")

    # Build event body
    body = build_event_body(args)

    try:
        service = get_calendar_service()
        created = push_event(service, calendar_id, body)
    except Exception as e:
        print(f"ERROR: Failed to push event: {e}", file=sys.stderr)
        sys.exit(1)

    # Output success to stdout for pipeline consumption
    result = {
        "status": "ok",
        "event_id": created.get("id"),
        "html_link": created.get("htmlLink"),
        "summary": created.get("summary"),
        "start": created.get("start"),
        "end": created.get("end"),
        "calendar_id": calendar_id,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    sys.exit(0)


if __name__ == "__main__":
    main()

