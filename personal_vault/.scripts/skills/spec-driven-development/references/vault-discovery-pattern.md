# Vault Discovery Pattern

## Problem
Need to locate shared vault across different environments (dev machine, CI, other profiles) without hardcoded paths per profile.

## Solution: Priority-Based Auto-Detection

```python
_KNOWN_VAULT_PATH = Path("/c/Users/khoans/Documents/Warren_OS_Local/vault")

def get_vault_root() -> Path:
    # 1. Explicit override (CI, other machines)
    if vault := os.environ.get("VAULT_ROOT"):
        return Path(vault).resolve()
    
    # 2. Known fixed path (current dev machine)
    if _KNOWN_VAULT_PATH.exists():
        return _KNOWN_VAULT_PATH
    
    # 3. Skill-relative fallback (pip install portable)
    skill_root = Path(__file__).resolve().parents[1]
    candidate = skill_root / "vault"
    if candidate.exists():
        return candidate.resolve()
    
    raise RuntimeError(f"Vault not found. Tried:\n  1. VAULT_ROOT env var\n  2. Known path: {_KNOWN_VAULT_PATH}\n  3. Skill-relative: {candidate}\n\nSet VAULT_ROOT or ensure vault exists at known path.")
```

## Priority Order
1. **`VAULT_ROOT` env var** — Explicit override for CI/other machines
2. **Known fixed path** — Zero-config for your primary machine
3. **Skill-relative fallback** — Portable installs via `pip install`

## Usage in Commands
```python
from .vault_resolver import get_scripts_dir, get_cases_dir

def my_command():
    scripts_dir = get_scripts_dir()  # vault/scripts/
    sys.path.insert(0, str(scripts_dir))
    from ops_cases_cli import main
    return main()
```

## Benefits
- **Zero config** for you — works out of the box
- **CI ready** — set `VAULT_ROOT` in pipeline
- **Portable** — skill works when pip-installed elsewhere
- **Clear error** — actionable guidance when not found