# Stock Profile Creation — 2026-06-23

## Context
Warren wanted to split stock/investing from `personal_profile` into a dedicated `stock-profile` because memory about health/sleep/family (GG access, court dates, sleep quality) was polluting stock research context.

## Process
Followed `using-agent-skills` flow:
1. `interview-me` — extracted real intent (memory pollution, not skill availability)
2. `spec-driven-development` — wrote spec: Objective, Commands, Project Structure, Testing, Boundaries, Success Criteria
3. `planning-and-task-breakdown` — created 8 tasks across 4 phases

## Architecture Decision

**Junction entire `skills/` directory** (Option A), not just `personal-commands/`:

```python
import subprocess, os, shutil

junc_path = r'C:\Users\khoans\AppData\Local\hermes\profiles\stock-profile\skills'
target = r'C:\Users\khoans\AppData\Local\hermes\profiles\warren-profile\skills'

if os.path.exists(junc_path):
    shutil.rmtree(junc_path)

result = subprocess.run(
    ['cmd.exe', '/c', 'mklink', '/D', junc_path, target],
    capture_output=True, text=True, shell=True
)
```

## Memory Strategy
- **Move (never copy)** — stock memory leaves personal_profile entirely
- Zero overlap between profiles
- Cron jobs migrate to stock-profile

## Future Renames (Deferred)
- `deep-research-stock` → `stock-deep-research`
- `personal-stock-ingest` → `stock-ingest`
- Not blocking; do gradually

## Verification
- Switch to stock-profile → `capture-stock`, `deep-research-stock` work
- Memory: no sleep/family/GG mentions when discussing stock
- Switch to personal_profile → no BCTC/EPS/watchlist memories