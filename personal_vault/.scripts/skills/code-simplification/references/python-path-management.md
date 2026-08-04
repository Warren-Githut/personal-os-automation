# Python Path Management for Modular Projects

## Problem
Python modules in different directories need to import each other, but:
- Modules are in different directories
- Running from different working directories breaks imports
- Services run from different contexts (systemd, NSSM, batch file)

## Solution: Explicit PYTHONPATH Management

### 1. In Code (at entry point)
```python
# In telegram_bot.py
import sys
from pathlib import Path

SKILL_ROOT = Path(__file__).parent
sys.path.insert(0, str(SKILL_ROOT))
sys.path.insert(0, str(SKILL_ROOT.parent / "scripts"))

from case_brain_nl_handler import handle_message
```

### 2. In Batch File (.bat)
```bat
set PYTHONPATH=C:\Path\To\Skill;C:\Path\To\Shared\Scripts
python -m my_module
```

### 3. In PowerShell
```powershell
$env:PYTHONPATH = "C:\Path\To\Skill;C:\Path\To\Shared\Scripts"
python -m my_module
```

### 4. In NSSM Service
```powershell
& $nssm set $svcName AppEnvironmentExtra "PYTHONPATH=C:\Path\To\Skill;C:\Path\To\Shared"
```

## Common Patterns

### Pattern 1: Skill → Vault Scripts
```python
# Skill at: C:\skills\my-skill\my_module\
# Vault at:  C:\project\vault\scripts\

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
```

### Pattern 2: Shared Library
```
project/
├── shared/          # Common utilities
│   └── utils.py
├── service_a/       # Service A
│   └── main.py      # import sys; sys.path.insert(0, "../shared")
└── service_b/       # Service B
    └── main.py      # import sys; sys.path.insert(0, "../shared")
```

## Best Practices

| Rule | Implementation |
|------|----------------|
| **Explicit is better than implicit** | Always `sys.path.insert(0, ...)` at module top |
| **Use Pathlib** | `Path(__file__).resolve().parents[1] / "scripts"` |
| **Semicolon separator on Windows** | `path1;path2;path3` |
| **Colon separator on Unix** | `path1:path2:path3` |
| **Insert at index 0** | Ensures priority over site-packages |

## Windows vs Unix Separators

```python
import os
path_sep = ";" if os.name == "nt" else ":"
pythonpath = path_sep.join(paths)
os.environ["PYTHONPATH"] = pythonpath
```

## Common Pitfalls

| Pitfall | Symptom | Fix |
|--------|---------|-----|
| ModuleNotFoundError | `sys.path.insert(0, "/abs/path/to/module")` |
| Wrong module loaded | `sys.path.insert(0, ...)` not `append()` |
| Service can't import | Set `AppEnvironmentExtra PYTHONPATH=...` in NSSM |
| .bat file fails | `set PYTHONPATH=path1;path2` before `python -m` |

## Debugging

```bash
# Check current PYTHONPATH
python -c "import sys; print('\n'.join(sys.path))"

# Test import
python -c "import my_module; print('OK')"

# From specific directory
cd /project && PYTHONPATH=/shared python -m my_module
```