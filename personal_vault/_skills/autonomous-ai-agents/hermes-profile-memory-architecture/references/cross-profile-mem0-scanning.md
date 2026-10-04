# Cross-Profile Mem0 Scanning Pattern

## Problem

When a user has multiple Hermes profiles (e.g. warren, personal, stock), each with its own isolated Mem0 instance, **the `mem0_*` tools (mem0_list, mem0_search, mem0_delete) have NO profile parameter**. From an agent session in warren-profile, you can only access warren-profile's mem0.

To scan/cleanup ALL profiles' memories in one job, you need a different approach.

## Discovery (2026-06-26)

Warren has 3 profiles (warren, personal, stock). During mem0 cleanup, `mem0_list` returned 37 memories — all L'Usine ops related. Zero personal or stock memories. This confirmed:
1. The 3 profiles are sharing ONE Mem0 instance (default setup)
2. Or personal/stock profiles simply haven't accumulated memories yet

The `hermes-profile-memory-architecture` skill doc states: "Mem0 config is per-profile (`$HERMES_HOME/mem0.json`) — each profile can have different memory databases."

## Solution: Python Script with Multiple Configs

```python
"""Cross-profile Mem0 scanner — queries all 3 profiles."""
import json
import os
from mem0 import Memory

# Profile configs (adjust paths per setup)
PROFILES = {
    "warren": os.path.expanduser("~/.hermes/profiles/warren-profile/mem0.json"),
    "personal": os.path.expanduser("~/.hermes/mem0.json"),  # default profile at root
    "stock": os.path.expanduser("~/.hermes/profiles/stock-profile/mem0.json"),
}

def scan_profile(name, config_path):
    """Return all memories for a profile."""
    if not os.path.exists(config_path):
        return {"error": f"Config not found: {config_path}"}
    
    with open(config_path) as f:
        cfg = json.load(f)
    
    m = Memory.from_config(cfg)
    memories = m.get_all()  # returns list of {id, memory, ...}
    return {"name": name, "count": len(memories), "memories": memories}

def scan_all():
    results = {}
    for name, path in PROFILES.items():
        results[name] = scan_profile(name, path)
    return results

if __name__ == "__main__":
    import json
    print(json.dumps(scan_all(), indent=2, ensure_ascii=False))
```

## Prerequisites

1. **Each profile MUST have its own isolated Mem0 database** — if profiles share one instance, cross-profile scanning is redundant.
2. **All profile configs must be readable** from the profile running the script (usually warren-profile).
3. **mem0 library must be importable** — `pip install mem0ai` system-wide.

## Usage Pattern

In a cron job or agent session:
1. Agent writes above script to temp file
2. `terminal("python3 /tmp/mem0_scanner.py")` → get JSON output
3. Agent parses JSON, applies noise detection criteria per profile
4. Formats report, presents to user

## Alternative: Separate Cron Per Profile

Simpler but gives 3 messages instead of 1 combined report:
- Each profile has its own cron job (CN 09:00)
- Each lists its own memories via `mem0_list` (no cross-profile needed)
- Each sends its own Telegram report
- User approves each independently
