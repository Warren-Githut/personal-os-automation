#!/usr/bin/env python3
"""
Test script to validate command file structure.
Validates: YAML frontmatter, required fields, required sections.
"""

import sys
import os
import re
import yaml
from pathlib import Path
from typing import List, Tuple, Dict, Any

REQUIRED_FRONTMATTER_FIELDS = ['description']
OPTIONAL_FRONTMATTER_FIELDS = ['updated', 'mode']
REQUIRED_SECTIONS = ['## Usage', '## Instructions']  # At minimum

def parse_frontmatter(content: str) -> Tuple[Dict[str, Any], str]:
    """Extract YAML frontmatter and body from markdown file."""
    if not content.startswith('---'):
        return {}, content
    
    parts = content.split('---', 2)
    if len(parts) < 3:
        return {}, content
    
    try:
        fm = yaml.safe_load(parts[1])
        body = parts[2].strip()
        return fm or {}, body
    except yaml.YAMLError as e:
        raise ValueError(f"Invalid YAML frontmatter: {e}")

def validate_command_file(filepath: Path) -> List[str]:
    """Validate a single command file. Returns list of errors (empty = valid)."""
    errors = []
    
    try:
        content = filepath.read_text(encoding='utf-8')
    except Exception as e:
        return [f"Cannot read file: {e}"]
    
    # 1. Validate frontmatter
    fm, body = parse_frontmatter(content)
    
    if not fm:
        errors.append("Missing YAML frontmatter (--- ... ---)")
    
    for field in REQUIRED_FRONTMATTER_FIELDS:
        if field not in fm:
            errors.append(f"Missing required frontmatter field: {field}")
        elif not fm[field] or not str(fm[field]).strip():
            errors.append(f"Empty required frontmatter field: {field}")
    
    # Validate 'updated' date format if present
    if 'updated' in fm and fm['updated']:
        date_str = str(fm['updated']).strip()
        if not re.match(r'^\d{4}-\d{2}-\d{2}$', date_str):
            errors.append(f"Invalid 'updated' date format (expected YYYY-MM-DD): {date_str}")
    
    # Validate 'mode' if present
    if 'mode' in fm and fm['mode']:
        mode_val = str(fm['mode']).strip().lower()
        if mode_val not in ['primary', 'secondary']:
            errors.append(f"Invalid 'mode' value (expected primary|secondary): {fm['mode']}")
    
    # 2. Validate required sections in body
    instruction_sections = ['## Instructions', '## PROTOCOL', '## Protocol', '## Steps', '## Protocol', '## STEPS']
    has_instructions = any(section in body for section in instruction_sections)
    
    if not has_instructions:
        errors.append("Missing required section: ## Instructions (or ## PROTOCOL / ## Steps)")
    
    # 3. Validate command name in Usage section
    usage_match = re.search(r'## Usage[\s\S]*?```\s*\n/([\w-]+)', body)
    if not usage_match:
        errors.append("Usage section missing command pattern (```\n/command-name)")
    else:
        cmd_name = usage_match.group(1)
        # Filename should match command name (without .md)
        expected_name = filepath.stem
        if cmd_name != expected_name:
            errors.append(f"Command name in Usage ('{cmd_name}') doesn't match filename ('{expected_name}')")
    
    return errors

def validate_directory(dirpath: Path) -> Dict[str, List[str]]:
    """Validate all .md files in a directory. Returns dict of filename -> errors."""
    results = {}
    md_files = list(dirpath.glob('*.md'))
    
    if not md_files:
        return {"_empty": [f"No .md files found in {dirpath}"]}
    
    for f in md_files:
        results[f.name] = validate_command_file(f)
    
    return results

def main():
    if len(sys.argv) < 2:
        print("Usage: python validate_commands.py <directory>")
        sys.exit(1)
    
    dirpath = Path(sys.argv[1])
    if not dirpath.exists():
        print(f"Directory not found: {dirpath}")
        sys.exit(1)
    
    results = validate_directory(dirpath)
    
    all_pass = True
    for filename, errors in results.items():
        if filename == "_empty":
            for e in errors:
                print(f"  ⚠ {e}")
            continue
        
        if errors:
            all_pass = False
            print(f"❌ {filename}")
            for e in errors:
                print(f"   - {e}")
        else:
            print(f"✅ {filename}")
    
    if all_pass and "_empty" not in results:
        print(f"\n✅ All {len(results)} command files valid")
        sys.exit(0)
    else:
        print(f"\n❌ Validation failed")
        sys.exit(1)

if __name__ == '__main__':
    main()