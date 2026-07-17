#!/usr/bin/env python3
"""Scan _inbox/01_unprocessed/ for trading items -> classify -> route to pulse files -> archive."""

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
PULSE_DIR = VAULT_ROOT / "10_PULSE"

PULSE_FILES = {
    "daily": "022_VNStock_Daily_Outlook.md",
    "macro": "021_VNStock_Macro.md",
    "weekly": "020_VNStock_Weekly_Outlook.md",
}


def parse_frontmatter(content: str) -> dict:
    if not content.startswith("---"):
        return {}
    parts = content.split("---", 2)
    if len(parts) < 3:
        return {}
    try:
        import yaml
        return yaml.safe_load(parts[1])
    except Exception:
        fm = {}
        for line in parts[1].strip().split("\n"):
            if ":" in line:
                k, v = line.split(":", 1)
                fm[k.strip()] = v.strip().strip('"').strip("'")
        return fm


def classify_route(text: str) -> str:
    """Classify trading content -> daily, macro, or weekly."""
    text_lower = text.lower()
    
    # Macro keywords
    macro_kw = ["fed", "lãi suất", "interest rate", "gdp", "cpi", "inflation", "ngân hàng trung ương", 
                "macro", "vĩ mô", "chính sách tiền tệ", "geopolitics", "địa chính trị"]
    
    # Weekly keywords
    weekly_kw = ["tuần", "weekly", "review", "xu hướng tuần", "sector flow", "dòng tiền", "portfolio",
                 "watchlist", "theo dõi", "mass", "ptsc", "mwg", "fpt", "vnindex tuần"]
    
    if any(kw in text_lower for kw in macro_kw):
        return "macro"
    if any(kw in text_lower for kw in weekly_kw):
        return "weekly"
    return "daily"


def extract_ticker(text: str) -> str | None:
    """Extract VN stock ticker from text."""
    # Common VN tickers
    tickers_re = re.compile(r'\b([A-Z]{3})\b')
    known = {"GAS", "NLG", "NVL", "FPT", "VIC", "VHM", "VCB", "BID", "CTG", "TCB", "MBB", "VPB", 
             "HPG", "HSG", "NKG", "PNJ", "MWG", "MSN", "SAB", "BVH", "GMD", "DHG", "IMP", "KDH",
             "POW", "PVD", "PVS", "GAS", "PLX", "STB", "EIB", "MSB", "SHB", "ACB", "TCH", "OCB",
             "LPB", "ABB", "VND", "SSI", "VCI", "HCM", "BCM", "TCM", "BSI", "VIX", "VNM", "MSN"}
    matches = tickers_re.findall(text)
    for m in matches:
        if m in known:
            return m
    return None


def generate_entry(date_str: str, ticker: str, route: str, text: str, source: str) -> str:
    """Generate pulse entry block based on route type."""
    
    # For weekly: use YYYY-WW format following template
    if route == "weekly":
        # Extract week from date_str (YYYY-MM-DD -> YYYY-WW)
        from datetime import datetime
        try:
            dt = datetime.strptime(date_str, "%Y-%m-%d")
            week_num = dt.isocalendar()[1]
            week_str = f"{dt.year}-W{week_num:02d}"
            # Calculate week range
            from datetime import timedelta
            monday = dt - timedelta(days=dt.weekday())
            sunday = monday + timedelta(days=6)
            week_range = f"tuần {monday.strftime('%d/%m')}–{sunday.strftime('%d/%m')}"
        except Exception:
            week_str = date_str.replace("-", "-W")
            week_range = "tuần DD/MM–DD/MM"
        
        # Extract key info for macro context
        text_lower = text.lower()
        # Simple extraction for display
        macro_lines = []
        if "s&p" in text_lower or "dow" in text_lower or "nasdaq" in text_lower:
            macro_lines.append("- Mỹ: S&P 500/Dow/Nasdaq biến động")
        if "giá dầu" in text_lower or "brent" in text_lower or "wti" in text_lower:
            macro_lines.append("- Dầu: Brent/WTI biến động")
        if "khối ngoại" in text_lower:
            macro_lines.append("- Khối ngoại: mua/bán ròng")
        if "vn-index" in text_lower or "vnindex" in text_lower:
            macro_lines.append("- VN-Index: biến động")
        if not macro_lines:
            macro_lines = ["- Trung Đông / dầu: | Lãi suất: | Lạm phát: | USD/VND:", "- VN-Index: | Khối ngoại: | Dòng tiền nội:"]
        
        return f"""## {week_str} ({week_range})

### Macro context
{chr(10).join(macro_lines)}

### Sector highlights
| Nhóm | Động lực | Rủi ro |
|---|---|---|
| [Dầu khí] | [...] | [...] |
| [Bất động sản] | [...] | [...] |
| [Ngân hàng] | [...] | [...] |

### Watchlist update
| Ticker | IV est | Price | MOS% | Action |
|---|---|---|---|---|
| [{ticker or 'VNM'}] | [...] | [...] | [...] | [...] |

### Holdings check (thesis intact?)
-

### Strategy
- Ngắn hạn: [...]
- Dài hạn: [...]
- Tránh: [...]

### Source
{source}
---
"""
    
    # For daily/macro: use narrative format
    auto_title = f"{ticker or ''} {text[:50]}".strip()
    
    return f"""## {date_str} — {auto_title}

### Narrative
{text[:200]}

### Impact assessment
- VN market impact: [...]
- Affected sectors: [...]
- Related tickers: [{ticker or 'N/A'}]

### Watch points
- [...]

### Source
{source}
---
"""


def find_trading_files(inbox_dir: Path) -> list[Path]:
    files = []
    for f in inbox_dir.glob("*.md"):
        fm, _ = read_file(f)
        if fm.get("domain") == "trading":
            files.append(f)
    return sorted(files)


def read_file(filepath: Path) -> tuple[dict, str]:
    content = filepath.read_text(encoding="utf-8")
    fm = parse_frontmatter(content)
    body = content.split("---", 2)[-1].strip() if content.startswith("---") else content
    return fm, body


def process_item(filepath: Path, route: str, direct_input: str = None, auto_route: bool = False):
    """Process a single trading item."""
    if direct_input:
        text = direct_input
        source = "Direct input"
        date_str = datetime.now().strftime("%Y-%m-%d")
    else:
        fm, body = read_file(filepath)
        text = body
        source = f"_inbox/01_unprocessed/{filepath.name}"
        date_match = re.match(r"(\d{4}-\d{2}-\d{2})", filepath.name)
        date_str = date_match.group(1) if date_match else datetime.now().strftime("%Y-%m-%d")
    
    # Determine route
    if route is None:
        route = classify_route(text)
    
    ticker = extract_ticker(text)
    
    # If route was explicitly provided (auto_route=True), skip confirmation
    if not auto_route:
        # Confirm with user
        print(f"\nItem: {text[:80]}...")
        print(f"Detected ticker: {ticker or 'N/A'}")
        print(f"Recommended route: {route} -> {PULSE_FILES[route]}")
        
        confirm = input("Route to this file? [y/n/custom]: ").strip().lower()
        if confirm == 'n':
            custom = input("Enter route (daily/macro/weekly): ").strip().lower()
            if custom in PULSE_FILES:
                route = custom
            else:
                print("Invalid route, skipping.")
                return None
        elif confirm and confirm != 'y':
            if confirm in PULSE_FILES:
                route = confirm
            else:
                print("Invalid route, skipping.")
                return None
    
    # Build and write entry
    entry = generate_entry(date_str, ticker, route, text, source)
    pulse_file = PULSE_DIR / PULSE_FILES[route]
    
    # Prepend to pulse file (newest on top) - insert AFTER template block if exists
    if pulse_file.exists():
        content = pulse_file.read_text(encoding="utf-8")
        lines = content.split("\n")
        insert_idx = None
        
        # For weekly file: find closing ``` of template block, insert after that
        if route == "weekly":
            in_code_block = False
            for i, line in enumerate(lines):
                if line.strip().startswith("```"):
                    in_code_block = not in_code_block
                    if not in_code_block:  # closing ```
                        insert_idx = i + 1
                        break
        else:
            # For daily/macro: find first ## header after frontmatter
            for i, line in enumerate(lines):
                if line.startswith("## ") and i > 0:
                    insert_idx = i
                    break
        
        if insert_idx is not None:
            lines.insert(insert_idx, entry.rstrip())
        else:
            lines.append(entry.rstrip())
        new_content = "\n".join(lines)
    else:
        new_content = entry
    
    pulse_file.write_text(new_content, encoding="utf-8")
    print(f"  Written to {PULSE_FILES[route]}")
    
    # Archive if not direct input
    if not direct_input:
        INBOX_PROCESSED.mkdir(parents=True, exist_ok=True)
        dest = INBOX_PROCESSED / f"_DONE_{filepath.name}"
        shutil.move(str(filepath), str(dest))
        print(f"  Archived to {dest.name}")
    
    return route


def main():
    parser = argparse.ArgumentParser(description="Capture trading items -> route to VNStock pulse files")
    parser.add_argument("input", nargs="?", help="Direct input text (optional)")
    parser.add_argument("--route", choices=["daily", "macro", "weekly"], help="Force route")
    parser.add_argument("--auto", action="store_true", help="Auto-process without confirmation (for non-interactive use)")
    args = parser.parse_args()
    
    if args.input:
        print("Processing direct input...")
        process_item(None, args.route, direct_input=args.input, auto_route=args.auto or args.route is not None)
        return
    
    items = find_trading_files(INBOX_UNPROCESSED)
    if not items:
        print("No trading items in _inbox/01_unprocessed/")
        return
    
    print(f"Found {len(items)} trading item(s)")
    for f in items:
        route = process_item(f, args.route, auto_route=args.auto or args.route is not None)
        if route:
            print(f"  ✅ Routed to {PULSE_FILES[route]}")


if __name__ == "__main__":
    main()
