# Hermes Skill Development Pattern: Multi-Profile Shared Vault

## Context
Discovered during L'Usine case management NL skill development. A proper Hermes skill was created (`lusine-cases`) that wraps existing vault implementation, deployable to multiple Hermes profiles sharing a single vault.

## Pattern: Vault → Skill (Runtime Import)

### Architecture
```
vault/scripts/ (SOURCE OF TRUTH)
├── case_brain_nl_parser.py
├── case_brain_nl_handler.py
├── case_followup_orchestrator.py
└── ops_cases_cli.py

lusine-ops skill (THIN WRAPPER)
├── lusine_ops/vault_resolver.py    # Only logic not in vault
├── lusine_ops/cli.py               # Entrypoint: ops-cases
└── lusine_ops/commands/*.py        # Thin dispatch → vault modules
```

### Runtime Flow
```python
# lusine_ops/commands/update_nl.py
from lusine_ops.vault_resolver import get_vault_root
import sys
sys.path.insert(0, str(get_vault_root() / "scripts"))

from case_brain_nl_handler import handle_message
handle_message(full_text, dry_run=dry_run)
```

### Why This Works
- **Single source of truth**: All logic in `vault/scripts/`; edit once, all profiles pick up
- **Zero sync needed**: No build step, no copy-on-install
- **Skill stays tiny**: ~5 files, ~100 lines total
- **Profile-agnostic**: Same skill file works in warren-profile, lusine-profile, personal_profile

## Vault Discovery Pattern

```python
def get_vault_root() -> Path:
    # 1. VAULT_ROOT env var (explicit override for CI/other machines)
    if vault_env := os.environ.get("VAULT_ROOT"):
        vault_path = Path(vault_env).resolve()
        if vault_path.exists():
            return vault_path
        raise RuntimeError(f"VAULT_ROOT set but path does not exist: {vault_path}")

    # 2. Known fixed path (current development machine)
    if _KNOWN_VAULT_PATH.exists():
        return _KNOWN_VAULT_PATH.resolve()

    # 3. Skill-relative fallback (portable installs via pip)
    skill_root = Path(__file__).resolve().parents[1]  # lusine-cases/
    candidate = skill_root / "vault"
    if candidate.exists():
        return candidate.resolve()

    raise RuntimeError("Vault not found. Set VAULT_ROOT or ensure vault exists.")
```

**Design principle**: Zero-config for developer (auto-detects), overrideable for CI, clear error message.

## Skill Distribution: Local Install + Helper Script

```bash
# install_all_profiles.sh
for profile in warren-profile lusine-profile personal_profile; do
    hermes skill install . --profile "$profile"
done
```

- No registry account needed
- Runs once, installs to all profiles
- Skill appears in `hermes skills list` per profile

## Skill Naming: Avoid Conflicts

Check existing skills first:
```bash
ls ~/.hermes/profiles/<profile>/skills/ | grep lusine
```

Existing `lusine-ops` (COL/CPH analysis) caused conflict → renamed to `lusine-cases`.

## Natural Language Command Design

### Three Commands with Distinct Behaviors

| Command | Behavior | Format |
|---------|----------|--------|
| `[update case <fuzzy>] <payload>` | Append dated thread entry (newest on top) | `### YYYY-MM-DD HH:MM — Warren\n<payload>` |
| `[edit case <fuzzy>] <payload>` | In-place frontmatter/body edit | Modifies existing sections |
| `[close case <fuzzy>]` | Close + auto lesson learned/insight vs `## Thành công` | Moves to `closed/`, adds Close Review |

### Fuzzy Matching
- Token overlap on slug + title (stdlib only, no `thefuzz`)
- Threshold: 0.35 overlap score
- Case-insensitive, diacritic-insensitive

## Battle Test Pattern: 5 Flexible + 3 A/B

### 5 Flexible Scenarios (per NL module)
1. Prefix parsing: all 4 prefixes `[new/update/edit/close case]`
2. Dated block format: `### YYYY-MM-DD HH:MM — Warren`
3. Newest-on-top injection
4. Body building: free-form + structured headings
5. End-to-end thread append

### 3 A/B Tests (behavioral distinctions)
1. `edit` in-place vs `update` append
2. Close generates lesson learned vs success criteria
3. Fuzzy find matches partial name

## Code Simplification Patterns Applied (This Session)

| Pattern | Before | After | File |
|---------|--------|-------|------|
| Shared helper for duplicate logic | `detect_section` + `detect_field` | Single `_match_keywords` | parser |
| Delete dead constants | `WORKSPACE_ROOT`, `NO_CALENDAR_FLAG` | Removed | handler |
| Remove unused imports | 8 imports | 4 used imports | handler |
| Delete no-op functions | `extract_update_text()` | Marked `# no-op, API compat` | parser |
| Simplify title extraction | Tokenize + scan | Split lines, find first `#` | parser |
| Dead code elimination | `if resolution: pass` | Deleted | cli |
| Inline trivial function | `now_time_str()` (never called) | Deleted | handler |
| Hoist local imports | `def f(): import sys` | Top-level | cli |
| Consolidate imports | `import yaml` in function | Top-level | cli |

**Rule**: "If you delete it and tests still pass, it was dead code."

## Battle Test Results (This Session)

| Test Suite | Results |
|------------|---------|
| Orchestrator | 8/8 pass |
| NL Parser/Handler | 8/8 pass |
| Vault Resolver | 7/7 pass |
| Smoke Tests (3 profiles) | 6/6 pass |
| **Total** | **30/30 PASS** |

## Known Issues / Potential Concerns

1. **Close file move timing**: `shutil.move` happens before content fully written → closed file shows stale content. Mitigate: ensure write completes before move, or re-read after move.

2. **Fuzzy match threshold (0.35)**: May need tuning with more cases. Monitor false positives/negatives.

3. **Repeated `sys.path.insert`**: Each command wrapper inserts vault path. Could centralize in `commands/__init__.py` initialization.

4. **Skill name collision**: Always check `hermes skills list --profile <x>` before naming.

## Quick Reference: Skill Structure

```
lusine-ops/ (skill package)
├── SKILL.md              # Manifest (name: lusine-cases)
├── pyproject.toml
├── install_all_profiles.sh
├── lusine_ops/
│   ├── __init__.py
│   ├── vault_resolver.py   # Auto-detect + VAULT_ROOT override
│   ├── cli.py              # Entrypoint: ops-cases
│   └── commands/
│       ├── __init__.py
│       ├── list.py, detail.py, new.py, close.py
│       ├── followup.py, migrate.py
│       ├── update_nl.py, edit_nl.py, close_nl.py
└── tests/
    ├── test_vault_resolver.py
    └── test_smoke.py
```

## Deployment Checklist

- [ ] Install in all target profiles: `./install_all_profiles.sh`
- [ ] Verify `ops-cases --help` shows 9 commands in each profile
- [ ] Run all test suites (orchestrator + NL + resolver + smoke)
- [ ] Test NL prefixes: `[update case ...]`, `[edit case ...]`, `[close case ...]`
- [ ] Test CLI: `ops-cases update "name" "payload" --dry-run`
- [ ] Document in `_cases/README.md` and `scripts/QUICK_REFERENCE.md`