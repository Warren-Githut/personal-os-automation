#!/usr/bin/env python3
"""Clean up sleep log: remove test entries, deduplicate, sort newest on top."""

from pathlib import Path
import re
from datetime import datetime

SLEEP_LOG = Path("C:/Users/khoans/Documents/Personal_OS/personal_vault/10_PULSE/051_Sleep_Log.md")

content = SLEEP_LOG.read_text(encoding="utf-8")

# Split into template (before first ---) and entries
template_end = content.find("\n---\n", content.find("\n# 051"))
template = content[:template_end + 5]  # include the ---\n

# Parse entries
entries_text = content[template_end + 5:]

# Find all entries: starts with ### YYYY-MM-DD
entry_pattern = r"(### \d{4}-\d{2}-\d{2}.*?)(?=\n### |\Z)"
entries_raw = re.findall(entry_pattern, entries_text, re.DOTALL)

print(f"Found {len(entries_raw)} raw entries")

# Parse each entry: extract date, source, and collect best per date
entries_by_date = {}
for entry in entries_raw:
    date_match = re.search(r"### (\d{4}-\d{2}-\d{2})", entry)
    if not date_match:
        continue
    date = date_match.group(1)
    
    # Extract source
    source_match = re.search(r"\*\*Source:\*\* ([^\n]+)", entry)
    source = source_match.group(1).strip() if source_match else "unknown"
    
    # Skip test entries (direct_paste from test dates > 16/6)
    # Only keep real data up to 16/6
    date_obj = datetime.strptime(date, "%Y-%m-%d")
    if date_obj > datetime(2026, 6, 16):
        print(f"Skipping test entry: {date} ({source})")
        continue
    
    # Keep best entry per date (prefer non-direct_paste, then longer content)
    if date not in entries_by_date:
        entries_by_date[date] = entry
    else:
        # Prefer non-direct_paste, or longer entry
        existing_source = re.search(r"\*\*Source:\*\* ([^\n]+)", entries_by_date[date])
        existing_src = existing_source.group(1).strip() if existing_source else ""
        if "direct_paste" in source and "direct_paste" not in existing_src:
            # Keep existing (non-test)
            pass
        elif "direct_paste" not in source and "direct_paste" in existing_src:
            entries_by_date[date] = entry
        elif len(entry) > len(entries_by_date[date]):
            entries_by_date[date] = entry
        print(f"Kept {date} from {source}")

# Sort by date descending (newest first)
sorted_dates = sorted(entries_by_date.keys(), reverse=True)

# Rebuild content
new_entries = []
for date in sorted_dates:
    new_entries.append(entries_by_date[date].strip())

new_content = template + "\n\n" + "\n\n".join(new_entries) + "\n"

# Update last_updated
from datetime import datetime
new_content = re.sub(r'last_updated: \d{4}-\d{2}-\d{2}', f'last_updated: {datetime.now().strftime("%Y-%m-%d")}', new_content)

# Write
Path("C:/Users/khoans/Documents/Personal_OS/personal_vault/10_PULSE/051_Sleep_Log.md").write_text(new_content, encoding="utf-8")
print(f"Cleaned log: {len(sorted_dates)} unique dates, sorted newest on top")
for d in sorted_dates:
    print(f"  {d}")