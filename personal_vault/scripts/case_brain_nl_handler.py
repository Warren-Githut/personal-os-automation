#!/usr/bin/env python3
"""
case_brain_nl_handler.py

Brain-dump handler for L'Usine cases.
Input: raw text from Obsidian/Slack/Telegram
Output:
- [new case] -> create _cases/active/<slug>.md + sync 00_CASES_INDEX.md + send Telegram review
- [update case ...] -> append dated entry (newest on top) + review
- [edit case ...] -> in-place frontmatter/body edit + review
- [close case ...] -> close file + lesson learned/insight + review
"""

from __future__ import annotations

import sys
import os
import re
import shutil
import unicodedata
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional
from case_brain_nl_parser import (
    detect_prefix,
    find_case_by_query,
    parse_frontmatter,
    format_frontmatter,
    detect_section,
    detect_field,
    build_update_entry,
    inject_update_entry,
)

# VAULT_ROOT: Use env var or auto-detect from skill location
# Skill is at: ~/.hermes/profiles/*/skills/lusine-cases/
# Vault is at: ~/Documents/Warren_OS_Local/vault/
VAULT_ROOT = Path(os.getenv(
    "VAULT_ROOT",
    r"C:\Users\khoans\Documents\Warren_OS_Local\vault"
))
ACTIVE_DIR = VAULT_ROOT / "_cases" / "active"
CLOSED_DIR = VAULT_ROOT / "_cases" / "closed"
CASES_INDEX = VAULT_ROOT / "_cases" / "00_CASES_INDEX.md"


def run_orchestrator(args: list[str]) -> None:
    import subprocess
    cmd = [sys.executable, str(VAULT_ROOT / "scripts" / "case_followup_orchestrator.py")] + args
    subprocess.run(cmd, check=False)


def send_telegram(text: str) -> None:
    # Placeholder: integrate Telegram notify when available in runtime/CLI context
    print("[TELEGRAM REVIEW]\n" + text)


def today_str() -> str:
    return datetime.now().strftime("%Y-%m-%d")


def tomorrow_str() -> str:
    return (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")


def _slugify(text: str) -> str:
    """Convert text to slug: normalize unicode, remove diacritics, replace spaces/special chars with hyphens."""
    # Strip leading numbering: "2. ", "1) ", "10 - "
    import re
    text = re.sub(r'^\s*\d+[\s.)\-]+', '', text)
    
    text = unicodedata.normalize("NFD", text)
    # Explicitly handle Vietnamese Đ/đ before stripping combining marks
    text = text.replace('Đ', 'D').replace('đ', 'd')
    text = "".join(c for c in text if unicodedata.category(c) != "Mn")
    text = re.sub(r"[^\w\s-]", "", text.lower())
    text = re.sub(r"[\s-]+", "-", text).strip("-")
    return text[:48]


def build_case_body_from_payload(payload: str) -> str:
    fields = {
        "Vấn đề": None,
        "Bối cảnh": None,
        "Giải pháp đề xuất": None,
        "Thành công": None,
    }

    lines = payload.splitlines()

    # Collect leading text (before first heading) as Vấn đề
    leading_parts: list[str] = []
    i = 0
    while i < len(lines):
        stripped = lines[i].strip()
        if stripped.startswith("#"):
            break
        leading_parts.append(lines[i])
        i += 1

    if leading_parts:
        fields["Vấn đề"] = "\n".join(leading_parts).strip()

    # Parse sections starting from first heading
    current_section: Optional[str] = None
    buf: list[str] = []

    while i < len(lines):
        line = lines[i].rstrip("\n")
        stripped = line.strip()

        # Check if this line is a section heading
        matched_section = None
        for section_name in fields.keys():
            if stripped.lstrip("#").strip().lower().startswith(section_name.lower()):
                matched_section = section_name
                break

        if matched_section:
            # Save previous section
            if current_section and buf:
                existing = fields[current_section]
                new_content = "\n".join(buf).strip()
                fields[current_section] = (existing + "\n" + new_content) if existing else new_content
            current_section = matched_section
            buf = []
        else:
            if current_section:
                buf.append(line)
        i += 1

    # Save last section
    if current_section and buf:
        existing = fields[current_section]
        new_content = "\n".join(buf).strip()
        fields[current_section] = (existing + "\n" + new_content) if existing else new_content

    # If still no fields populated, try heuristic fallback
    if not any(fields.values()):
        text = "\n".join(lines).strip()
        parts = [p.strip() for p in re.split(r"\n{2,}", text) if p.strip()]
        if parts:
            fields["Vấn đề"] = parts[0]
            if len(parts) > 1:
                fields["Bối cảnh"] = parts[1]
            if len(parts) > 2:
                fields["Giải pháp đề xuất"] = "\n\n".join(parts[2:])

    # Build output with only populated sections in order
    ordered = ["Vấn đề", "Bối cảnh", "Giải pháp đề xuất", "Thành công"]
    sections = [s for s in ordered if fields.get(s)]
    if not sections:
        sections = list(fields.keys())

    return "\n\n".join(f"## {section}\n{fields[section]}" for section in sections)


def create_case_from_payload(payload: str, *, dry_run: bool = False) -> Path:
    slug = datetime.now().strftime("%Y-%m-%d") + "_" + _slugify(payload.splitlines()[0])
    path = ACTIVE_DIR / f"{slug}.md"

    frontmatter = {
        "status": "active",
        "store": "lu3",
        "opened": today_str(),
        "updated": today_str(),
        "priority": "medium",
        "follow_up": tomorrow_str(),
        "followup_event_id": "",
        "stakeholders": "Warren",
        "owner": "warren",
        "title": payload.splitlines()[0][:80] if payload.strip() else "Brain dump case",
        "tags": "ops,revenue",
        "slug": slug,
    }

    body = build_case_body_from_payload(payload)
    content = f"{format_frontmatter(frontmatter)}\n\n# {frontmatter['title']}\n\n{body}\n"

    if dry_run:
        print("[DRY-RUN] Would create:\n" + content)
        return path

    path.write_text(content, encoding="utf-8")
    run_orchestrator(["migrate-simplify", "--execute"])
    return path


def edit_case_by_nl(path: Path, payload: str, *, dry_run: bool = False) -> str:
    data, body = parse_frontmatter(path)
    data["updated"] = today_str()

    if payload.strip():
        data.setdefault("title", payload.splitlines()[0])

    # Modify frontmatter only for explicit field pattern
    field = detect_field(payload)
    if field:
        value = payload.strip()
        data[field] = value

    section = detect_section(payload)
    if section and payload.strip():
        body = re.sub(
            rf"(## {re.escape(section)}\n)(.|\n)*?(?=\n## |\Z)",
            rf"\1{payload.strip()}\n",
            body,
        )
        if section not in body:
            body = f"{body}\n\n## {section}\n{payload.strip()}\n"

    updated_body = inject_update_entry(body, build_update_entry(f"Edited: {payload.strip()}"))
    content = f"{format_frontmatter(data)}\n\n# {data.get('title', path.stem)}\n{updated_body}"
    if dry_run:
        print("[DRY-RUN] Would edit:\n" + content)
        return content
    path.write_text(content, encoding="utf-8")
    return content


def update_case_by_nl(path: Path, payload: str, *, dry_run: bool = False) -> str:
    data, body = parse_frontmatter(path)
    data["updated"] = today_str()
    entry = build_update_entry(payload)
    updated_body = inject_update_entry(body, entry)
    data.setdefault("title", payload.splitlines()[0][:80])
    content = f"{format_frontmatter(data)}\n\n# {data.get('title', path.stem)}\n{updated_body}"
    if dry_run:
        print("[DRY-RUN] Would update:\n" + content)
        return content
    path.write_text(content, encoding="utf-8")
    run_orchestrator(["followup", "--slug", path.stem, "--update"])
    return content


def close_case_with_review(path: Path, *, dry_run: bool = False) -> str:
    data, body = parse_frontmatter(path)
    success_section_match = re.search(r"## Thành công\n(.+?)(?:\n## |\Z)", body, re.S)
    success_text = success_section_match.group(1).strip() if success_section_match else "(no success criteria)"

    today = today_str()
    review_lines = [
        "## Close Review",
        f"- Closed: {today}",
        "- Lesson learned: (auto)",
        "- Insight: (auto)",
        f"- Success target: {success_text.splitlines()[0] if success_text else ''}",
    ]
    review = "\n".join(review_lines) + "\n"

    updated_body = inject_update_entry(body, review)
    data["status"] = "closed"
    data["updated"] = today
    data["followup_event_id"] = ""
    content = f"{format_frontmatter(data)}\n\n# {data.get('title', path.stem)}\n{updated_body}"
    if dry_run:
        print("[DRY-RUN] Would close:\n" + content)
        return content
    dest = CLOSED_DIR / path.name
    shutil.move(str(path), str(dest))
    run_orchestrator(["followup", "--slug", path.stem, "--close"])
    return content


def handle_message(text: str, *, dry_run: bool = False) -> Optional[str]:
    prefix, query, payload = detect_prefix(text)
    if not prefix:
        print("[WARN] No known prefix found. Use [new case], [update case ...], [edit case ...], or [close case ...].")
        return None

    if not payload and prefix not in ["[close case"]:
        print("[WARN] Empty payload after prefix.")
        return None

    if prefix.startswith("[new case"):
        path = create_case_from_payload(payload if payload else "Brain dump case", dry_run=dry_run)
        message = f"Created case: {path.name}\n\nPath: {path}\n\nPlease review and edit if needed."

    elif prefix.startswith("[edit case"):
        case_path = find_case_by_query(query)
        if not case_path:
            print(f"[ERROR] Case not found for edit query: {query!r}")
            return None
        content = edit_case_by_nl(case_path, payload, dry_run=dry_run)
        message = f"Edited case: {case_path.name}\n\n{content}"

    elif prefix.startswith("[update case"):
        case_path = find_case_by_query(query)
        if not case_path:
            print(f"[ERROR] Case not found for update query: {query!r}")
            return None
        content = update_case_by_nl(case_path, payload, dry_run=dry_run)
        message = f"Updated case: {case_path.name}\n\n{content}"

    elif prefix.startswith("[close case"):
        case_path = find_case_by_query(query)
        if not case_path:
            print(f"[ERROR] Case not found for close query: {query!r}")
            return None
        content = close_case_with_review(case_path, dry_run=dry_run)
        message = f"Closed case: {case_path.name}\n\nReview:\n{content}"

    else:
        print(f"[WARN] Unknown prefix: {prefix}")
        return None

    print(message)
    send_telegram(message)
    return message


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Case brain NL handler")
    parser.add_argument("message", nargs="?", help="Message to process")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done")
    args = parser.parse_args()

    if not args.message:
        print("Usage: case_brain_nl_handler.py '<message>' [--dry-run]")
        sys.exit(0)
    handle_message(args.message, dry_run=args.dry_run)