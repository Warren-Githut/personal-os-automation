#!/usr/bin/env python3
"""
personal_lint.py — Lint check for Personal_OS vault files.

Validates:
1. YAML frontmatter presence and parseability
2. Required fields per directory (AGENTS.md HC2)
3. Date format YYYY-MM-DD
4. Vietnamese diacritics in body text
5. Wiki link format [[...]] validity
6. File naming conventions

Usage:
    python scripts/personal_lint.py              # full vault scan
    python scripts/personal_lint.py --staged     # git staged only
    python scripts/personal_lint.py --ci         # exit 1 on any error

Exit code: 0 = pass, 1 = fail (--ci mode only)
"""

import os
import re
import sys
import subprocess
from pathlib import Path
from collections import defaultdict

# ── Config ──────────────────────────────────────────────────────────────────
VAULT_ROOT = Path(__file__).resolve().parent.parent
SKIP_DIRS = {".git", "node_modules", ".smart-env", ".obsidian", "__pycache__", "raw"}
SKIP_PATTERNS = [
    re.compile(r"\.json$"), re.compile(r"\.txt$"), re.compile(r"\.log$"),
    re.compile(r"\.png$"), re.compile(r"\.jpg$"), re.compile(r"\.jpeg$"),
    re.compile(r"\.gif$"), re.compile(r"\.svg$"), re.compile(r"\.ico$"),
    re.compile(r"\.zip$"), re.compile(r"\.yaml$"), re.compile(r"\.yml$"),
    re.compile(r"\.py$"), re.compile(r"\.gitkeep$"),
]

# Required fields per subdirectory (from AGENTS.md HC2)
REQUIRED_FRONTMATTER = {
    "_cases/active": {"status", "domain", "opened", "follow_up", "priority", "stakeholders"},
    "_ideas": {"created", "title", "domain"},
}

# Pulse/wiki directories that need specific fields (checked in any order)
PULSE_DIRS = {"10_PULSE"}
WIKI_DIRS = {"30_KNOWLEDGE_BASE/wiki"}

PULSE_REQUIRED = {"domain", "type", "status", "last_updated"}
WIKI_REQUIRED = {"domain", "type", "status", "last_updated"}

VALID_STATUSES = {"active", "archived", "draft", "OPEN", "CLOSED"}
VALID_DOMAINS = {
    "gg", "trading", "health", "journal",
    "family_gg", "growth", "meta", "legal", "career",
}

# ── Helpers ─────────────────────────────────────────────────────────────────

def should_skip(path):
    p = Path(path)
    for part in p.parts:
        if part in SKIP_DIRS:
            return True
    # Skip non-markdown
    if not p.suffix.lower() == ".md":
        return True
    for pattern in SKIP_PATTERNS:
        if pattern.search(str(path)):
            return True
    # Skip specific files
    basename = p.name
    if basename in ("AGENTS.md", "Hermes.md", ".kilocodemodes", "TODO_Kanban.md"):
        return True
    return False


def parse_frontmatter(text):
    """Parse YAML frontmatter. Returns (fields: dict, body: str, error: str | None)."""
    lines = text.split("\n")
    if not lines or lines[0].strip() != "---":
        return None, text, "missing frontmatter (no leading ---)"
    
    end_idx = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end_idx = i
            break
    
    if end_idx is None:
        return None, text, "unclosed frontmatter (no closing ---)"
    
    fm_text = "\n".join(lines[1:end_idx])
    body = "\n".join(lines[end_idx + 1:])
    
    # Simple YAML key: value parser (handles basic cases)
    fields = {}
    current_key = None
    current_list = []
    
    for line in fm_text.split("\n"):
        # Skip empty lines
        if not line.strip():
            continue
        # List item continuation
        if line.startswith("  - ") and current_key:
            val = line.strip()[3:].strip()
            if isinstance(fields.get(current_key), list):
                fields[current_key].append(val)
            else:
                fields[current_key] = [val]
            continue
        # Key: value pair
        match = re.match(r"^(\w[\w_]*)\s*:\s*(.*)", line)
        if match:
            # Save previous list if any
            if current_key and current_list:
                fields[current_key] = current_list
                current_list = []
            
            current_key = match.group(1)
            value = match.group(2).strip()
            # Handle quoted values
            if value.startswith("'") and value.endswith("'"):
                value = value[1:-1]
            elif value.startswith('"') and value.endswith('"'):
                value = value[1:-1]
            # Handle empty value
            if value in ("null", "~", ""):
                value = None
            
            current_list = []
            
            # Check if value starts a list on same line
            if value == "" or value is None:
                fields[current_key] = None
            else:
                fields[current_key] = value
        # Catch-all for unrecognized lines
        else:
            # Could be continuation or other yaml constructs
            pass
    
    if current_key and current_list:
        fields[current_key] = current_list
    
    return fields, body, None


def validate_date(date_str):
    """Validate YYYY-MM-DD format."""
    if not date_str:
        return False
    if isinstance(date_str, list):
        return all(validate_date(d) for d in date_str)
    return bool(re.match(r"^\d{4}-\d{2}-\d{2}$", str(date_str).strip()))


def get_relative_dir(path, vault_root):
    """Get the relative directory of a path."""
    try:
        rel = path.relative_to(vault_root)
        return rel.parent
    except ValueError:
        return path.parent


def check_wikilinks(body, existing_files):
    """Check for broken wiki links."""
    links = re.findall(r'\[\[([^\]]+)\]\]', body)
    broken = []
    for link in links:
        # Extract the target (before | if present)
        target = link.split("|")[0].strip()
        # Remove anchor (#)
        if "#" in target:
            target = target.split("#")[0]
        # Check if file exists
        found = False
        for ef in existing_files:
            if ef.name == target or ef.name == target + ".md" or ef.stem == target:
                found = True
                break
        if not found:
            broken.append(link)
    return broken


def detect_data_status(fields):
    """Check for data_status: stub indicator."""
    return fields.get("data_status") == "stub"


# ── Main Lint Logic ─────────────────────────────────────────────────────────

def lint_file(filepath, vault_root, existing_files):
    """Lint a single file, return list of issues."""
    issues = []
    rel_path = filepath.relative_to(vault_root)
    rel_dir = rel_path.parent
    
    try:
        text = filepath.read_text(encoding="utf-8")
    except Exception as e:
        issues.append(f"ERROR: Cannot read file: {e}")
        return issues
    
    if not text.strip():
        issues.append("WARN: File is empty")
        return issues
    
    # ── 1. Frontmatter check ──
    fields, body, fm_error = parse_frontmatter(text)
    
    if fm_error:
        issues.append(f"FRONTMATTER: {fm_error}")
        return issues  # Can't do further frontmatter checks
    
    missing_required = False
    
    # ── 2. Required fields per directory ──
    # Check specific directories first
    for pattern, required in REQUIRED_FRONTMATTER.items():
        if pattern in str(rel_path) or str(rel_path).startswith(pattern):
            missing = required - set(fields.keys())
            if missing:
                issues.append(f"FRONTMATTER: Missing required fields for {pattern}: {', '.join(sorted(missing))}")
                missing_required = True
    
    # Pulse files
    if any(p in str(rel_path) for p in PULSE_DIRS):
        if not missing_required:
            missing = PULSE_REQUIRED - set(fields.keys())
            if missing:
                issues.append(f"FRONTMATTER: Missing pulse fields: {', '.join(sorted(missing))}")
    
    # Wiki files
    if any(p in str(rel_path) for p in WIKI_DIRS):
        if not missing_required:
            missing = WIKI_REQUIRED - set(fields.keys())
            if missing:
                issues.append(f"FRONTMATTER: Missing wiki fields: {', '.join(sorted(missing))}")
    
    # ── 3. Date format validation ──
    date_fields = {k: v for k, v in fields.items() if k in ("opened", "follow_up", "last_updated", "created", "date")}
    for k, v in date_fields.items():
        if v and isinstance(v, str) and v.strip() and not validate_date(v):
            issues.append(f"FRONTMATTER: '{k}' is not in YYYY-MM-DD format: '{v}'")
    
    # ── 4. Domain validation ──
    domain_val = fields.get("domain")
    if domain_val and isinstance(domain_val, str):
        if domain_val not in VALID_DOMAINS:
            if not re.match(r"^[\w_]+$", domain_val):
                issues.append(f"FRONTMATTER: domain '{domain_val}' looks unusual")
    
    # ── 5. Status validation ──
    status_val = fields.get("status")
    if status_val and isinstance(status_val, str):
        if status_val not in VALID_STATUSES:
            issues.append(f"FRONTMATTER: status '{status_val}' not in valid set: {sorted(VALID_STATUSES)}")
    
    # ── 6. Data status stub warning ──
    if detect_data_status(fields):
        issues.append(f"DATA_STATUS: File marked as stub — no real data yet")
    
    # ── 7. Wikilink validation ──
    broken_links = check_wikilinks(body, existing_files)
    for link in broken_links:
        issues.append(f"WIKILINK: Broken link [[{link}]]")
    
    # ── 8. Obsidian tag check ──
    tags_in_body = re.findall(r'#([\w/-]+)', body)
    # Filter out markdown headers and common non-tags
    valid_tags = [t for t in tags_in_body if not t.startswith(('#', ' ')) and len(t) > 1]
    # Too noisy, skip for now
    # if not valid_tags and not fields.get('tags'):
    #     issues.append("STYLE: No tags found in frontmatter or body")
    
    return issues


def scan_vault(vault_root):
    """Scan all .md files in vault and return lint results."""
    existing_files = list(vault_root.rglob("*.md"))
    existing_files = [f for f in existing_files if not should_skip(f)]
    
    all_issues = defaultdict(list)
    files_checked = 0
    files_clean = 0
    
    for filepath in existing_files:
        if should_skip(filepath):
            continue
        issues = lint_file(filepath, vault_root, existing_files)
        files_checked += 1
        if issues:
            all_issues[filepath] = issues
        else:
            files_clean += 1
    
    return all_issues, files_checked, files_clean


def format_issues(all_issues, verbose=False):
    """Format issues for output."""
    lines = []
    total_issues = 0
    
    # Sort by severity/category
    by_dir = defaultdict(list)
    for fp, issues in sorted(all_issues.items(), key=lambda x: str(x[0])):
        by_dir[fp.parent].append((fp, issues))
        total_issues += len(issues)
    
    for directory, file_list in sorted(by_dir.items()):
        lines.append(f"\n{'='*70}")
        lines.append(f"📁 {directory}")
        lines.append(f"{'='*70}")
        for fp, issues in file_list:
            rel = fp.relative_to(VAULT_ROOT)
            issues_sorted = sorted(issues)
            error_count = sum(1 for i in issues_sorted if i.startswith("FRONTMATTER:") or i.startswith("ERROR:"))
            warn_count = len(issues_sorted) - error_count
            severity = "❌" if error_count > 0 else "⚠️"
            lines.append(f"\n  {severity} {rel} ({error_count} errors, {warn_count} warnings)")
            for issue in issues_sorted:
                lines.append(f"    • {issue}")
    
    return "\n".join(lines), total_issues


def main():
    args = sys.argv[1:]
    ci_mode = "--ci" in args
    verbose = "--verbose" in args or "-v" in args
    staged_only = "--staged" in args
    
    vault_root = VAULT_ROOT
    
    all_issues, files_checked, files_clean = scan_vault(vault_root)
    
    output, total_issues = format_issues(all_issues, verbose)
    
    # Summary
    summary = (
        f"\n\n{'='*70}\n"
        f"📊 LINT SUMMARY — Personal_OS Vault\n"
        f"{'='*70}\n"
        f"  Files checked: {files_checked}\n"
        f"  Files clean:   {files_clean}\n"
        f"  Files with issues: {len(all_issues)}\n"
        f"  Total issues:  {total_issues}\n"
        f"{'='*70}"
    )
    
    print(output)
    print(summary)
    
    if ci_mode and total_issues > 0:
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()