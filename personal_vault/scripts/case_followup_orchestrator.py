"""case_followup_orchestrator.py — Case Follow-up Calendar Orchestrator (Personal OS)

Usage:
    python case_followup_orchestrator.py --slug <slug>
    python case_followup_orchestrator.py --slug <slug> --close
    python case_followup_orchestrator.py --slug <slug> --update

Arguments:
    --slug      Case slug (filename without .md, includes YYYY-MM prefix)
    --close     Delete follow-up event and archive Kanban card
    --update    Force reschedule (delete old event, create new)

Dependencies:
    - push_gcal.py (same directory) — provides load_env, get_calendar_service, build_event

Personal OS differences from L'Usine version:
    - Kanban: TODO_Kanban.md (not LUSINE_TODO_Kanban.md)
    - Frontmatter: uses domain: instead of store:
"""

import argparse
import datetime
import os
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

from push_gcal import load_env, get_calendar_service, build_event, TIMEZONE

VAULT_ROOT = Path(__file__).parent.parent
ACTIVE_DIR = VAULT_ROOT / "_cases" / "active"
KANBAN_PATH = VAULT_ROOT / "TODO_Kanban.md"
ACTIVITY_LOG = VAULT_ROOT / "_kilo" / "ACTIVITY_LOG.md"
CLOSED_DIR = VAULT_ROOT / "_cases" / "closed"

PRIORITY_TIME_OFFSET = {"high": 0, "medium": 15, "low": 30}
PRIORITY_LABEL = {"high": "HIGH", "medium": "MEDIUM", "low": "LOW"}
PRIORITY_ORDER = {"high": 0, "medium": 1, "low": 2}


def parse_args():
    parser = argparse.ArgumentParser(description="Case follow-up calendar orchestrator (Personal OS)")
    parser.add_argument("--slug", required=True, help="Case slug (filename without .md)")
    parser.add_argument("--close", action="store_true", help="Delete event on case closure")
    parser.add_argument("--update", action="store_true", help="Force reschedule")
    return parser.parse_args()


def read_case_frontmatter(slug):
    path = ACTIVE_DIR / f"{slug}.md"
    if not path.exists():
        print(f"[ERROR] Case not found: {path}")
        sys.exit(1)
    content = path.read_text(encoding="utf-8")
    m = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
    if not m:
        print(f"[ERROR] Cannot parse frontmatter -- check YAML syntax in {slug}")
        sys.exit(1)
    yaml_text = m.group(1)
    data = {}
    for line in yaml_text.splitlines():
        if ":" in line:
            key, _, val = line.partition(":")
            data[key.strip()] = val.strip().strip('"').strip("'")
    data["_content"] = content
    data["_path"] = path
    return data


def get_same_day_cases(slug, follow_up_str, priority):
    same_day = []
    for f in ACTIVE_DIR.glob("*.md"):
        s = f.stem
        if s == slug:
            continue
        try:
            c = read_case_frontmatter(s)
            fu = c.get("follow_up", "")
            if fu == follow_up_str:
                same_day.append({"slug": s, "priority": c.get("priority", "medium").lower()})
        except Exception:
            pass
    same_day.append({"slug": slug, "priority": priority})
    same_day.sort(key=lambda x: PRIORITY_ORDER.get(x["priority"], 1))
    for i, c in enumerate(same_day):
        if c["slug"] == slug:
            return i * 15
    return PRIORITY_TIME_OFFSET.get(priority, 15)


def determine_followup_time(slug, case_data):
    follow_up_str = case_data.get("follow_up", "")
    if not follow_up_str:
        follow_up_dt = datetime.date.today() + datetime.timedelta(days=1)
    else:
        try:
            follow_up_dt = datetime.datetime.strptime(follow_up_str, "%Y-%m-%d").date()
        except ValueError:
            follow_up_dt = datetime.date.today() + datetime.timedelta(days=1)
    priority = case_data.get("priority", "medium").lower()
    offset = get_same_day_cases(slug, follow_up_str, priority)
    hour = 10 + offset // 60
    minute = offset % 60
    return follow_up_dt, f"{hour:02d}:{minute:02d}"


def find_existing_event(service, slug):
    calendar_id = os.environ.get("GOOGLE_CALENDAR_ID", "primary")
    now = datetime.datetime.utcnow().isoformat() + "Z"
    events_result = service.events().list(
        calendarId=calendar_id,
        timeMin=now,
        maxResults=100,
        singleEvents=True,
        orderBy="startTime",
        q=slug,
    ).execute()
    for event in events_result.get("items", []):
        if slug in event.get("summary", ""):
            return event.get("id"), event.get("htmlLink")
    return None, None


def delete_event(service, event_id):
    calendar_id = os.environ.get("GOOGLE_CALENDAR_ID", "primary")
    try:
        service.events().delete(calendarId=calendar_id, eventId=event_id).execute()
        return True
    except Exception as e:
        print(f"[WARN] Failed to delete event {event_id}: {e}")
        return False


def build_event_description(case_data, slug):
    domain = case_data.get("domain", "?")
    priority = case_data.get("priority", "medium")
    opened = case_data.get("opened", "?")
    updated = case_data.get("updated", opened)
    stakeholders = case_data.get("stakeholders", "?")
    file_path = f"_cases/active/{slug}.md"
    lines = [
        f"Case: {slug}",
        f"Domain: {domain}",
        f"Priority: {priority}",
        f"Opened: {opened}",
        f"Last updated: {updated}",
        f"Stakeholders: {stakeholders}",
        "",
        "--- Problem ---",
        "See case file for full details.",
        "",
        "--- Source ---",
        file_path,
    ]
    return "\n".join(lines)


def update_case_file_with_event_id(slug, event_id):
    path = ACTIVE_DIR / f"{slug}.md"
    content = path.read_text(encoding="utf-8")
    if "followup_event_id:" in content:
        new_content = re.sub(
            r'followup_event_id:\s*.*',
            f'followup_event_id: {event_id}',
            content,
        )
    else:
        new_content = re.sub(
            r'(stakeholders:.*?\n)',
            f'\\1followup_event_id: {event_id}\n',
            content,
        )
    path.write_text(new_content, encoding="utf-8")


def update_kanban(slug, case_data, follow_up_date):
    content = KANBAN_PATH.read_text(encoding="utf-8")
    domain = case_data.get("domain", "?")
    priority = case_data.get("priority", "medium")
    stakeholders = case_data.get("stakeholders", "?")
    column_header = "## Follow-up Today"
    card_line = (
        f"- [ ] {follow_up_date} -- [{slug}] {domain} #{priority}\n"
        f"\t  case:: [[_cases/active/{slug}]]\n"
        f"\t  stakeholders:: [{stakeholders}]"
    )
    if column_header not in content:
        insert_before = "## ✅ Done"
        new_column = f"\n\n{column_header}\n\n{card_line}\n\n"
        if insert_before in content:
            content = content.replace(insert_before, new_column + insert_before)
        else:
            content += f"\n\n{column_header}\n\n{card_line}\n"
    else:
        card_pattern = re.compile(
            rf'\[.*?\] .*? \[{re.escape(slug)}\] .*?(?:\n\t  .*)*'
        )
        if card_pattern.search(content):
            content = card_pattern.sub(card_line, content)
        else:
            col_pos = content.index(column_header) + len(column_header)
            content = content[:col_pos] + "\n" + card_line + content[col_pos:]
    KANBAN_PATH.write_text(content, encoding="utf-8")


def remove_from_kanban(slug):
    content = KANBAN_PATH.read_text(encoding="utf-8")
    lines = content.splitlines()
    filtered = []
    skip = False
    for line in lines:
        if skip:
            stripped = line.strip()
            if stripped.startswith("#") or not stripped:
                skip = False
                filtered.append(line)
            continue
        if f"[[_cases/active/{slug}]]" in line:
            skip = True
            continue
        if " -- " in line and f"[{slug}]" in line:
            skip = True
            continue
        filtered.append(line)
    KANBAN_PATH.write_text("\n".join(filtered) + "\n", encoding="utf-8")


def log_activity(slug, action, result):
    now = datetime.datetime.now()
    time_str = now.strftime("%H:%M")
    log_line = f"| {time_str} | {action} | [{slug}](_cases/active/{slug}.md) | {result} |"
    content = ACTIVITY_LOG.read_text(encoding="utf-8")
    lines = content.splitlines()
    header_idx = -1
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("|---") and i > 0:
            header_idx = i
            break
    if header_idx >= 0 and header_idx + 1 < len(lines):
        lines.insert(header_idx + 1, log_line)
        content = "\n".join(lines)
    else:
        content += "\n" + log_line
    ACTIVITY_LOG.write_text(content, encoding="utf-8")


def main():
    args = parse_args()
    slug = args.slug
    load_env()

    if args.close:
        if (ACTIVE_DIR / f"{slug}.md").exists():
            case_data = read_case_frontmatter(slug)
            event_id = case_data.get("followup_event_id", "")
            if event_id:
                try:
                    service = get_calendar_service()
                    if delete_event(service, event_id):
                        print(f"[OK] Deleted GCal event {event_id} for {slug}")
                except Exception as e:
                    print(f"[WARN] GCal API error during delete: {e}")
            else:
                try:
                    service = get_calendar_service()
                    existing_id, _ = find_existing_event(service, slug)
                    if existing_id:
                        delete_event(service, existing_id)
                        print(f"[OK] Deleted GCal event (found by slug) for {slug}")
                    else:
                        print(f"[OK] No existing event for {slug}")
                except Exception as e:
                    print(f"[WARN] GCal search failed: {e}")
            remove_from_kanban(slug)
            log_activity(slug, "GCAL DELETE", "Follow-up event deleted (case closed)")
        else:
            print(f"[INFO] Case {slug} not active -- nothing to clean up")
        return

    case_data = read_case_frontmatter(slug)
    follow_up_date, time_str = determine_followup_time(slug, case_data)
    date_str = follow_up_date.isoformat()
    domain = case_data.get("domain", "?")
    priority_raw = case_data.get("priority", "medium").lower()
    priority_label = PRIORITY_LABEL.get(priority_raw, "MEDIUM")
    parts = slug.replace("-", " ").replace("_", " ").split()
    if parts and parts[0].startswith("2026"):
        parts = parts[1:]
    short_desc = " ".join(parts[:5])
    summary = f"[{priority_label}] {domain.upper()} -- {short_desc}"
    description = build_event_description(case_data, slug)
    tags = f"case-followup,{domain}"
    priority_map = {"high": "high", "medium": "medium", "low": "normal"}

    try:
        service = get_calendar_service()
        existing_event_id = case_data.get("followup_event_id", "")
        if not existing_event_id:
            existing_id, _ = find_existing_event(service, slug)
            if existing_id:
                existing_event_id = existing_id
        if existing_event_id and args.update:
            delete_event(service, existing_event_id)
            print(f"[OK] Deleted old event for {slug}")
        link, event_id = build_event(
            service=service,
            summary=summary,
            date_str=date_str,
            time_str=time_str,
            tags=tags,
            priority=priority_map.get(priority_raw, "normal"),
            description=description,
            rrule="",
        )
        update_case_file_with_event_id(slug, event_id)
        update_kanban(slug, case_data, date_str)
        action = "GCAL UPDATE" if args.update else "GCAL CREATE"
        log_activity(slug, action, f"Event: {summary} -> {date_str} {time_str} | ID: {event_id[:20]}...")
        print(f"[OK] Follow-up set: {slug} -> {date_str} {time_str}")
        print(f"[OK] Link: {link}")
    except Exception as e:
        error_msg = str(e)
        print(f"[ERROR] GCal API error: {error_msg}")
        log_activity(slug, "GCAL FAIL", f"Error: {error_msg[:100]}")
        print(f"[WARN] Case file written -- calendar step skipped. Retry: python case_followup_orchestrator.py --slug {slug}")


if __name__ == "__main__":
    main()
