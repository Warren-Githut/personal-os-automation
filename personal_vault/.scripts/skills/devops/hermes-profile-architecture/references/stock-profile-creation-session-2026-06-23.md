# Stock Profile Creation — Session 2026-06-23

## Context
Warren wanted to split stock/investing from `personal_profile` into `stock-profile` because memory about health/sleep/family was polluting stock research context.

## Workflow
Followed the full engineering skill cascade:
1. `using-agent-skills` → `interview-me` (3 rounds, refined to 100%)
2. `spec-driven-development` → wrote spec
3. `planning-and-task-breakdown` → 4 phases, 8 tasks
4. `incremental-implementation` → executed slice by slice

## key Decision: Junction entire skills/ directory
Not just `personal-commands/`. Full skills junction so stock-profile sees ALL warren-profile skills (built-in + custom + ops).

## Commands Used

### Create profile
```bash
hermes profile create stock-profile --clone-from personal_profile
```

### Junction skills/
```python
import subprocess, os, shutil
junc_path = r'C:\Users\khoans\AppData\Local\hermes\profiles\stock-profile\skills'
target = r'C:\Users\khoans\AppData\Local\hermes\profiles\warren-profile\skills'
shutil.rmtree(junc_path)
subprocess.run(['cmd.exe', '/c', 'mklink', '/D', junc_path, target], shell=True)
```

### Memory split
**stock-profile MEMORY.md (stock-only):** BCTC OCR, EPS formula, pulse frontmatter, deep research flow
**stock-profile USER.md:** investor identity, LDR rule, integrity gate, capital segregation

**personal_profile MEMORY.md (keep):** tool pitfall, pulse rules, canonical profile
**personal_profile USER.md (keep):** personal identity (Saigon, separated, GG), workflow preferences

### Switch profiles
```bash
hermes profile use stock-profile   # set as sticky default
hermes profile list                # verify (◆ = active)
```

## Result
3 profiles:
- warren-profile (ops, default)
- stock-profile (investing, self-switch)
- personal_profile (health/family, self-switch)

Zero memory overlap. Junction dynamic. No cron to migrate.