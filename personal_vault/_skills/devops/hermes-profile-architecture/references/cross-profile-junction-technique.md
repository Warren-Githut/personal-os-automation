# Cross-Profile Junction Technique (Windows)

## Problem

Skills are per-profile in Hermes. When skills are centralized in `warren-profile`, other profiles (e.g., `personal_profile`, `stock-profile`) can't load those skills — they only load from their own `skills/` directory.

## Solution

Windows directory junction (`mklink /D`) via Python subprocess. Unlike `ln -s` in git-bash (which creates a fake static copy), a real junction dynamically reflects the target directory's contents.

## Canonical Code

```python
import subprocess, os, shutil

def create_skill_junction(junc_path: str, target: str) -> bool:
    """Create Windows junction for cross-profile skill access.
    Returns True if successful, False otherwise."""
    if os.path.exists(junc_path):
        shutil.rmtree(junc_path)
    
    result = subprocess.run(
        ['cmd.exe', '/c', 'mklink', '/D', junc_path, target],
        capture_output=True, text=True, shell=True
    )
    
    success = result.returncode == 0 and os.path.islink(junc_path)
    if success:
        print(f"✅ Junction created: {junc_path} → {target}")
        print(f"   Contents: {os.listdir(junc_path)}")
    else:
        print(f"❌ Junction failed: {result.stdout} {result.stderr}")
    return success

# Usage:
create_skill_junction(
    r'C:\Users\khoans\AppData\Local\hermes\profiles\personal_profile\skills\personal-commands',
    r'C:\Users\khoans\AppData\Local\hermes\profiles\warren-profile\skills\personal-commands'
)
```

## Requirements

| Item | Detail |
|------|--------|
| OS | Windows 10/11 |
| Privilege | Developer Mode enabled (Settings → Privacy & Security → For Developers) |
| Python | `os.path.islink()` must return True after creation |
| Command | `cmd.exe /c mklink /D <junction_path> <target_path>` — both absolute |
| Anti-pattern | DO NOT use `ln -s` in git-bash/MSYS — creates fake symlink, `islink()` returns False |

## Verification

```python
import os

path = r'C:\...\personal_profile\skills\personal-commands'
target = r'C:\...\warren-profile\skills\personal-commands'

print('Is link:', os.path.islink(path))       # Must be True
print('Is dir:', os.path.isdir(path))          # Must be True
print('Contents:', os.listdir(path))           # Must match os.listdir(target)
print('Target contents:', os.listdir(target))  # Should be identical
```

## Dynamic Behavior

- New files added to `target/` appear in junctioned path automatically
- No need to recreate junction when new skills are added
- Works with Hermes Desktop's skill loader (uses `os.scandir()` which follows junctions)

## Recovery

If junction breaks (e.g., after Hermes update that recreates profile dirs):
```python
# Just re-run the create function — it checks exists + removes before creating
create_skill_junction(junc_path, target)
```

## Case Study

Applied 2026-06-23 for Warren's dual-profile setup:
- `personal_profile/skills/personal-commands/` → `warren-profile/skills/personal-commands/`
- `capture-stock` + `capture-sleep` accessible from personal_profile
- Parent git commit: `edf8815`