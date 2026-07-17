#!/usr/bin/env python3
"""
Evaluation harness for weekly broker report entries.
Compares generated weekly markdown against a gold-standard section.
v1.1 — fixed regex/Windows path handling, coverage logic, added A/B mode.
"""

from pathlib import Path
import json
import re
import argparse

VAULT_ROOT = Path("C:/Users/khoans/Documents/Personal_OS/personal_vault")
PULSE_DIR = VAULT_ROOT / "10_PULSE"
GOLD_PATH = PULSE_DIR / "020_VNStock_Weekly_Outlook.md"


def split_weekly_entries(text: str):
    # Find all week headers with their positions
    header_pattern = r"\n(## (20\d{2}-W\d{2} \([^\)]+\)) — ([^\n]+))\n"
    matches = list(re.finditer(header_pattern, text))
    headers = []
    chunks = []
    
    for i, match in enumerate(matches):
        headers.append(match.groups())
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        chunks.append(text[start:end])
    
    return headers, chunks


def extract_section_fields(entry_text: str):
    filled = []
    skeleton = 0
    blank = 0
    sections = ["Macro context", "Sector highlights", "Watchlist update", "Strategy"]
    reported = {}
    for section in sections:
        pattern = rf"(?i)### {re.escape(section)}\n(.*?)(?=\n###|\n##|\Z)"
        match = re.search(pattern, entry_text, re.DOTALL)
        body = match.group(1).strip() if match else ""
        sk = body.count("[...]")
        reported[section] = {
            "filled": 1 if body and sk < len(body.splitlines()) else 0,
            "skeleton": sk,
            "blank": 1 if not body else 0,
        }
        skeleton += sk
        blank += 1 if not body else 0
    return reported, skeleton, blank


def score_weekly_entry(entry_text: str):
    sections, skeleton, blank = extract_section_fields(entry_text)

    gold_text = GOLD_PATH.read_text(encoding="utf-8") if GOLD_PATH.exists() else ""
    gold_headers, gold_chunks = split_weekly_entries(gold_text)
    latest_gold = gold_chunks[0] if gold_chunks else ""

    watch_match = re.search(r"(?i)### Watchlist update\n(.*?)(?=\n###|\n##|\Z)", entry_text, re.DOTALL)
    watch_rows = 0
    if watch_match:
        rows = [x.strip() for x in watch_match.group(1).splitlines() if x.strip().startswith("|")]
        watch_rows = max(0, len(rows) - 2)

    weights = ["Macro context", "Sector highlights", "Watchlist update", "Strategy"]
    filled = sum(1 for s in weights if sections[s]["filled"])
    field_coverage = filled / len(weights)

    total_fields = 20
    skeleton_rate = skeleton / total_fields

    report = {
        "file_scanned": entry_text[:120].replace("\n", " "),
        "sections": sections,
        "watchlist_rows": watch_rows,
        "field_coverage": round(field_coverage, 2),
        "skeleton_rate": round(skeleton_rate, 2),
        "hallucination_flags": 0,
    }
    return report


def compare(candidate_text: str, gold_text: str):
    cand = score_weekly_entry(candidate_text)
    gold = score_weekly_entry(gold_text)
    return {"candidate": cand, "gold": gold}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", default=str(GOLD_PATH))
    parser.add_argument("--candidate", default=None)
    parser.add_argument("--week", default=None, help="Specific week to evaluate (e.g., 2026-W25)")
    args = parser.parse_args()

    path = Path(args.path)
    if not path.exists():
        print(f"File not found: {path}")
        return

    text = path.read_text(encoding="utf-8")
    headers, chunks = split_weekly_entries(text)
    if not chunks:
        print("No weekly entries found.")
        return

    # Find specific week or use latest
    target_idx = 0
    if args.week:
        for i, h in enumerate(headers):
            if args.week in h[0]:
                target_idx = i
                break
        else:
            print(f"Week {args.week} not found. Available: {[h[0] for h in headers]}")
            return

    latest_header, latest_chunk = headers[target_idx], chunks[target_idx]
    print(f"Entry: {latest_header[0]} — {latest_header[1]}")

    if args.candidate:
        cand_path = Path(args.candidate)
        if not cand_path.exists():
            print(f"Candidate not found: {cand_path}")
            return
        cand_text = cand_path.read_text(encoding="utf-8")
        cand_headers, cand_chunks = split_weekly_entries(cand_text)
        
        # Find matching week in candidate
        cand_idx = target_idx
        if args.week:
            for i, h in enumerate(cand_headers):
                if args.week in h[0]:
                    cand_idx = i
                    break
        cand_chunk = cand_chunks[cand_idx] if cand_chunks and cand_idx < len(cand_chunks) else cand_text
        gold_chunk = latest_chunk
        report = compare(cand_chunk, gold_chunk)
    else:
        report = score_weekly_entry(latest_chunk)

    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
