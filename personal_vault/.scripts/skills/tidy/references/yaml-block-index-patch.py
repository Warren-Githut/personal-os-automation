#!/usr/bin/env python3
"""
yaml-block-index-patch.py — fix phantom file_path in CASES_INDEX YAML blocks

When: `patch` tool's `...` fuzzy matching fails across YAML `---` delimiters.
Use this pattern instead: split on `---` , str.replace() per block, join.

Usage:
  cd /c/Users/khoans/Documents/Warren_OS_Local/vault
  python3 _cases/../../references/yaml-block-index-patch.py

Or inline (one-shot):
  cd /c/Users/khoans/Documents/Warren_OS_Local/vault && python3 -c "
import re
with open('_cases/00_CASES_INDEX.md') as f:
    c = f.read()
blocks = c.split('---')
for i, b in enumerate(blocks):
    if 'case_id:' in b and 'file_path: \"[[_cases/closed/]]\"' in b:
        case_id = re.search(r'case_id:\\s*\"([^\"]+)\"', b).group(1)
        blocks[i] = b.replace('[[_cases/closed/]]', f'[[_cases/closed/{case_id}]'])
open('_cases/00_CASES_INDEX.md', 'w').write('---'.join(blocks))
"

See also: tidy skill §10 pitfalls table
"""
