#!/usr/bin/env python3
"""
{{LOG_NAME}} Parser v{{VERSION}}
Source: GSheet tab "{{TAB_NAME}}" — {{DESCRIPTION}}
Output: 10_OPERATION_DATA/{{LOG_FILE}}

{{VERSION_SUFFIX}}: Uses _frontmatter_base for self-maintaining property table
"""

import io, sys, urllib.request, urllib.error, json, re
from datetime import date, datetime, timedelta
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

from _utils import fetch_gviz, gviz_cell, build_col_map, week_bounds, prev_week_bounds, make_week_id
from _frontmatter_base import run_parser_with_frontmatter, PROPERTY_DEFAULTS_BASE

# ── Config ────────────────────────────────────────────────────────────────────────
SHEET_ID  = "1ZtIocc_Ic1z-tO1JGd4ZLnRB_7ZHHkvpJ5emaWJyeEE"
SHEET_GID = "{{GID}}"  # tab "{{TAB_NAME}}"
VAULT_ROOT = Path(__file__).parent.parent.parent.parent
LOG_FILE   = VAULT_ROOT / "vault" / "10_OPERATION_DATA" / "{{LOG_FILE}}"

# Store mapping (adjust per parser)
STORE_MAP = {
    "GSheet Store Name 1": "LU3",
    "GSheet Store Name 2": "LU5",
    "GSheet Store Name 3": "LU7",
}
STORES = ["LU3", "LU5", "LU7"]

PARSER_VERSION = "{{VERSION}}"

# ── Property Table (Source of Truth) ─────────────────────────────────────────────
PROPERTY_DEFAULTS = {
    **PROPERTY_DEFAULTS_BASE,
    "name": "{{LOG_NAME}}",
    "data_source": {
        "sheet_id": SHEET_ID,
        "sheet_name": "{{TAB_NAME}}",
        "gid": SHEET_GID,
        "parser": "vault/10_OPERATION_DATA/parsers/{{PARSER_FILE}}",
        "parser_version": PARSER_VERSION
    },
    "cross_refs": [
        "01_Weekly_Revenue_Log.md (context)",
        "04_LTO_Weekly_Log.md (LTO orders)",
        "07_COL_Weekly_Log.md (Labor context)"
    ],
    "key_definitions": {
        "metric_name": "formula or description"
    },
    "targets": {
        "threshold_name": 100
    }
}

# ── Fetch ────────────────────────────────────────────────────────────────────────
def fetch_sheet():
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:json&gid={SHEET_GID}"
    try:
        with urllib.request.urlopen(url, timeout=20) as resp:
            text = resp.read().decode("utf-8")
    except urllib.error.URLError as e:
        print(f"ERROR: Không kết nối được GSheet — {e}")
        sys.exit(1)
    match = re.search(r"google\.visualization\.Query\.setResponse\(([\s\S]*)\)", text)
    if not match:
        raise ValueError("Cannot parse gviz response")
    table = json.loads(match.group(1))["table"]
    return table["cols"], table["rows"]

# ── Parse Logic ──────────────────────────────────────────────────────────────────
def parse_sheet(cols, rows):
    """Parse raw GSheet rows into structured data. Returns dict for build_entry."""
    # 1. Find column indices
    col_indices = {}
    for i, col in enumerate(cols):
        label = (col.get("label") or "").strip().lower()
        # Map GSheet column names to expected fields
        # {{COLUMN_MAPPING}}
    
    # 2. Filter by week (use week_bounds from _utils)
    # {{FILTER_LOGIC}}
    
    # 3. Parse each row into structured dict
    # {{PARSE_ROW_LOGIC}}
    
    return {"parsed_data": []}

# ── Build Entry ──────────────────────────────────────────────────────────────────
def build_entry(week_start, week_end, data):
    iso_week = week_start.isocalendar()[1]
    week_id = f"{week_start.year}-W{iso_week:02d}"
    date_range = f"{week_start.strftime('%d/%m')}–{week_end.strftime('%d/%m/%Y')}"
    
    L = []
    L.append(f"## {week_id} | {date_range}")
    L.append("")
    L.append("### Executive Summary")
    L.append("- System: ...")
    L.append("- Top/Bottom: ...")
    L.append("- Key Takeaway: ...")
    L.append("")
    
    L.append(f"### Weekly Roll-up (Δ vs W{iso_week-1})")
    L.append("| Store | Metric | ... |")
    L.append("|---|---|---|")
    for store in STORES:
        L.append(f"| {store} | ... | ... |")
    L.append(f"| **System** | **...** | **...** |")
    L.append("")
    
    L.append("### Daily Detail")
    for store in STORES:
        L.append(f"### {store}: ...")
        L.append("| Date | ... |")
        L.append("|---|---|")
        L.append("| ... | ... |")
        L.append("")
    
    L.append("---")
    return "\n".join(L)

# ── Main ─────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    run_parser_with_frontmatter(
        log_file=LOG_FILE,
        property_defaults=PROPERTY_DEFAULTS,
        parser_version=PARSER_VERSION,
        sheet_id=SHEET_ID,
        sheet_gid=SHEET_GID,
        fetch_sheet_fn=fetch_sheet,
        parse_sheet_fn=parse_sheet,
        build_entry_fn=build_entry,
        week_bounds_fn=week_bounds
    )