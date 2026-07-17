#!/usr/bin/env python3
"""Capture sleep logs from _inbox/01_unprocessed/ -> append to 10_PULSE/051_Sleep_Log.md (newest on top, Vietnamese co dau)."""

import argparse
import os
import re
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

VAULT_ROOT = Path(__file__).parent.parent
INBOX_UNPROCESSED = VAULT_ROOT / "_inbox" / "01_unprocessed"
INBOX_PROCESSED = VAULT_ROOT / "_inbox" / "02_processed_archived"
SLEEP_LOG_FILE = VAULT_ROOT / "10_PULSE" / "051_Sleep_Log.md"

# Sleep log pattern to parse: "Health log june 14: :hospital: Health: 6h50 | quality 92 | 63kg | 17h | Huyết áp: 98/71"
SLEEP_PATTERN = re.compile(
    r"health\s*log\s+\w+\s+\d{1,2}\s*[:：]\s*"
    r":hospital:\s*Health:\s*(?P<sleep>\d+h\d+)\s*\|\s*"
    r"quality\s+(?P<quality>\d+)\s*\|\s*"
    r"(?P<weight>[\d.]+)kg\s*\|\s*"
    r"(?P<fasting>\d+h?)\s*\|\s*"
    r"Huyết\s*áp:\s*(?P<bp>[\d/]+)",
    re.IGNORECASE
)


def parse_frontmatter(content: str) -> dict:
    """Extract YAML frontmatter from markdown."""
    if not content.startswith("---"):
        return {}
    parts = content.split("---", 2)
    if len(parts) < 3:
        return {}
    try:
        import yaml
        return yaml.safe_load(parts[1])
    except Exception:
        # Simple fallback parsing
        fm = {}
        for line in parts[1].strip().split("\n"):
            if ":" in line:
                k, v = line.split(":", 1)
                fm[k.strip()] = v.strip().strip('"').strip("'")
        return fm


def read_file_frontmatter(filepath: Path) -> tuple[dict, str]:
    """Read file, return (frontmatter, body)."""
    content = filepath.read_text(encoding="utf-8")
    fm = parse_frontmatter(content)
    body = content.split("---", 2)[-1].strip() if content.startswith("---") else content
    return fm, body


def parse_sleep_metrics(text: str) -> dict | None:
    """Parse sleep metrics from Slack message text."""
    match = SLEEP_PATTERN.search(text)
    if not match:
        return None
    return match.groupdict()


def generate_insight(sleep: str, quality: str, weight: str, fasting: str, bp: str) -> str:
    """Generate Vietnamese insight based on parsed metrics."""
    insights = []
    
    # Sleep vs baseline (7h median)
    try:
        if 'h' in sleep:
            parts = sleep.split('h')
            hours = int(parts[0])
            minutes = int(parts[1]) if parts[1] else 0
            total_hours = hours + minutes / 60
        else:
            total_hours = float(sleep)
        
        if total_hours < 6.5:
            insights.append(f"Sleep {sleep} dưới baseline (7h median 10 ngày qua)")
        elif total_hours < 7:
            insights.append(f"Sleep {sleep} thấp hơn baseline 7h")
        else:
            insights.append(f"Sleep {sleep} đạt baseline")
    except:
        pass
    
    # Quality
    try:
        q = int(quality)
        if q >= 90:
            insights.append(f"Quality {quality} vẫn ổn")
        elif q >= 80:
            insights.append(f"Quality {quality} ổn định")
        else:
            insights.append(f"Quality {quality} cần quan tâm")
    except:
        pass
    
    # Blood pressure
    try:
        if '/' in bp:
            sys_bp, dia_bp = map(int, bp.split('/'))
            if sys_bp >= 140 or dia_bp >= 90:
                insights.append(f"BP {bp} cao cần theo dõi")
            elif sys_bp < 100 or dia_bp < 60:
                insights.append(f"BP {bp} thấp nhưng trong healthy range")
            else:
                insights.append(f"BP {bp} bình thường")
    except:
        pass
    
    # Fasting
    try:
        fasting_h = int(fasting.replace('h', ''))
        if fasting_h >= 16:
            insights.append(f"Fasting {fasting} consistent")
        else:
            insights.append(f"Fasting {fasting} dưới window")
    except:
        pass
    
    # Weight
    insights.append(f"Weight {weight}kg ổn định")
    
    return ". ".join(insights) + " [MOD]"


def ensure_sleep_log_template(filepath: Path):
    """Ensure sleep log file has the template at top."""
    if filepath.exists():
        return
    
    today = datetime.now().strftime("%Y-%m-%d")
    template = f"""---
domain: health
type: pulse
status: active
last_updated: {today}
---

# 051 — Sleep Log

<!-- Daily sleep tracking: hours, quality, weight, fasting, and related health metrics. -->

> **Rule:** Newest on top -- newest entry first.
> **Quy tắc:** Newest on top -- mục mới nhất luôn đặt trên cùng, không append ở cuối. Khi thêm log/list/entry mới, chèn ngay sau block hướng dẫn này.
> Khi thêm entry mới: copy template ở cuối file, điền thông tin, rồi prepend ngay sau block rule này.

---

"""
    filepath.parent.mkdir(parents=True, exist_ok=True)
    filepath.write_text(template, encoding="utf-8")


def update_frontmatter_date(filepath: Path, new_date: str):
    """Update last_updated in frontmatter."""
    if not filepath.exists():
        return
    content = filepath.read_text(encoding="utf-8")
    lines = content.split("\n")
    for i, line in enumerate(lines):
        if line.startswith("last_updated:"):
            lines[i] = f"last_updated: {new_date}"
            break
    filepath.write_text("\n".join(lines), encoding="utf-8")


def build_entry_block(source_file: Path, date_str: str, metrics: dict, body_text: str) -> str:
    """Build the entry block for sleep log."""
    insight = generate_insight(
        metrics.get("sleep", ""),
        metrics.get("quality", ""),
        metrics.get("weight", ""),
        metrics.get("fasting", ""),
        metrics.get("bp", "")
    )
    
    # Use forward slash for path
    source_path = str(source_file.relative_to(VAULT_ROOT)).replace("\\", "/")
    
    return f"""### {date_str}
**Source:** {source_path}
**Type:** text

Sleep: {metrics.get('sleep', '')} | Quality: {metrics.get('quality', '')}/100 | Fasting: {metrics.get('fasting', '')} | Weight: {metrics.get('weight', '')}kg | Blood pressure: {metrics.get('bp', '')}

Insight:
{insight}

---
"""


def find_sleep_log_files(inbox_dir: Path) -> list[Path]:
    """Find all files in inbox with is_sleep_log: true."""
    files = []
    for f in inbox_dir.glob("*.md"):
        fm, _ = read_file_frontmatter(f)
        if fm.get("is_sleep_log") is True or str(fm.get("is_sleep_log")).lower() == "true":
            files.append(f)
    return sorted(files)


def capture_sleep_log(filepath: Path) -> bool:
    """Process a single sleep log file. Returns True if successful."""
    try:
        fm, body = read_file_frontmatter(filepath)
        
        # Extract date from filename: 2026-06-15_000121_health.md -> 2026-06-15
        date_match = re.match(r"(\d{4}-\d{2}-\d{2})", filepath.name)
        if not date_match:
            print(f"  Cannot parse date from filename: {filepath.name}")
            return False
        date_str = date_match.group(1)
        
        # Parse sleep metrics from body
        metrics = parse_sleep_metrics(body)
        if not metrics:
            print(f"  Cannot parse sleep metrics from: {filepath.name}")
            return False
        
        # Build entry block
        entry_block = build_entry_block(filepath, date_str, metrics, body)
        
        # Ensure sleep log file exists with template
        ensure_sleep_log_template(SLEEP_LOG_FILE)
        
        # Read current sleep log content
        content = SLEEP_LOG_FILE.read_text(encoding="utf-8")
        
        # Find insertion point: after the rule block (after "---" that ends the rule section)
        lines = content.split("\n")
        insert_idx = -1
        
        # Look for the first "---" after the rule block
        in_rule_block = False
        for i, line in enumerate(lines):
            if line.strip() == "---" and i > 10:  # After header
                in_rule_block = True
            elif in_rule_block and line.strip().startswith("### "):
                insert_idx = i
                break
            elif in_rule_block and line.strip() == "---" and insert_idx == -1:
                # End of rule block
                insert_idx = i + 1
        
        if insert_idx == -1:
            # Fallback: insert at end
            insert_idx = len(lines)
        
        # Insert new entry block
        new_lines = lines[:insert_idx] + [entry_block.rstrip()] + lines[insert_idx:]
        new_content = "\n".join(new_lines)
        
        # Update last_updated in frontmatter
        update_frontmatter_date(SLEEP_LOG_FILE, date_str)
        
        # Write updated content
        SLEEP_LOG_FILE.write_text(new_content, encoding="utf-8")
        
        print(f"  Appended to 051_Sleep_Log.md: {date_str}")
        return True
        
    except Exception as e:
        print(f"  Error processing {filepath.name}: {e}")
        import traceback
        traceback.print_exc()
        return False


def move_to_processed(filepath: Path):
    """Move processed file to 02_processed_archived/."""
    INBOX_PROCESSED.mkdir(parents=True, exist_ok=True)
    dest = INBOX_PROCESSED / filepath.name
    shutil.move(str(filepath), str(dest))


def main():
    parser = argparse.ArgumentParser(description="Capture sleep logs from _inbox/01_unprocessed/ -> 10_PULSE/051_Sleep_Log.md")
    parser.add_argument("file", nargs="?", help="Specific file to process (optional)")
    args = parser.parse_args()
    
    if args.file:
        files = [INBOX_UNPROCESSED / args.file]
    else:
        files = find_sleep_log_files(INBOX_UNPROCESSED)
    
    if not files:
        print("No sleep log files found to process")
        return
    
    print(f"Found {len(files)} sleep log file(s) to process")
    
    success_count = 0
    for f in files:
        print(f"Processing: {f.name}")
        if capture_sleep_log(f):
            move_to_processed(f)
            success_count += 1
    
    print(f"Done! Processed {success_count}/{len(files)} files")


if __name__ == "__main__":
    main()
