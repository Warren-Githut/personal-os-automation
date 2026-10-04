# Multi-Profile Skill Distribution Pattern

## Problem
Install the same skill (`lusine-cases`) into multiple Hermes profiles (warren-profile, lusine-profile, personal_profile) with shared vault.

## Solution: Manual Copy + Profile-Verified Install

### 1. Build Skill Package
```
lusine-ops/
├── SKILL.md              # name: lusine-cases, entrypoint: lusine_ops.cli:main
├── pyproject.toml
├── install_all_profiles.sh
├── lusine_ops/
│   ├── __init__.py
│   ├── vault_resolver.py
│   ├── cli.py
│   └── commands/
└── tests/
```

### 2. Install to All Profiles
```bash
#!/bin/bash
# install_all_profiles.sh
for profile in warren-profile lusine-profile personal_profile; do
    cp -r lusine-ops/ ~/.config/hermes/profiles/$profile/skills/lusine-cases/
done
```

### 3. Verify Per Profile
```bash
for profile in warren-profile lusine-profile personal_profile; do
    python3 -c "
import sys
sys.path.insert(0, f'/path/to/hermes/profiles/$profile/skills/lusine-cases')
from lusine_ops.cli import main
sys.argv = ['ops-cases', '--help']
main()
"
done
```

## Key Principles

| Principle | Implementation |
|-----------|----------------|
| **Single source of truth** | All logic in `vault/scripts/`, skill is thin wrapper |
| **Runtime vault discovery** | Skill finds vault at runtime via `VAULT_ROOT` or auto-detect |
| **No profile-specific code** | Same skill package works in all profiles |
| **Zero runtime config** | Auto-detects your vault path |

## Verification Checklist
- [ ] `ops-cases --help` shows 9 commands in each profile
- [ ] `ops-cases list` works in each profile  
- [ ] NL commands work: `update`, `edit`, `close-nl`
- [ ] Vault resolver finds correct path in each profile