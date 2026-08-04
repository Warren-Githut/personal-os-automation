# Vault Test Patterns

## Overview

Patterns for building Hermes skills that test vault/LLM system health (parsers, scripts, vault structure, skill integrity).

Canonical example: `battle-test` + `ab-test` skills in warren-profile.

---

## 1. Test Module Structure Convention

Every vault test module follows this shape:

```
scripts/
  utils.py                  ← Shared: VaultDiscoverer, YamlValidator, LinkChecker, Reporter, Timer
  test_vault_X.py           ← One battle test per file
    def run(vault_path, verbose) -> dict  (standard signature)
  battle_test_runner.py     ← Harness with --scope flag
  test_utils.py             ← Unit tests for utils
templates/                  ← Response format templates
SKILL.md                    ← Context wrapper + prompt core
```

### Standard `run()` signature

```python
def run(vault_path=None, verbose=False):
    vault_path, err = resolve_vault(vault_path, "test-name")
    if err:
        return err
    findings = []
    stats = {}
    with Timer() as timer:
        ...
    metrics = {"execution_time_s": round(timer.elapsed_s(), 2), ...}
    return make_verdict(findings, metrics, "test-name")
```

### Shared test helpers (utils.py)

```python
def resolve_vault(vault_path=None, test_name="test"):
    """Resolve vault path or return (None, fail_dict)."""
    ...

def make_verdict(findings, metrics, test_case):
    """Build pass/fail dict. Only CRITICAL/MAJOR cause FAIL."""
    ...
```

## 2. Severity-Aware Schema Mapping

```python
SCHEMA_MAP = [
    ("node_modules", set(), "INFO"),                    # skip
    ("10_OPERATION_DATA", SOP_FIELDS, "MAJOR"),         # strict
    ("_inbox", set(), "INFO"),                          # scratch
    ("00_CORE_LOGIC", {"name", "created"}, "MINOR"),
    ("", {"created"}, "MINOR"),                         # catch-all
]
```

- `set()` = skip check
- `name` missing + area severity >= MAJOR → escalates to CRITICAL
- Non-`name` fields use area's default severity

## 3. Pre-Commit Hook

Location: `{repo_root}/.git/hooks/pre-commit`

Key: `git diff --cached --name-only` returns paths **relative to repo root**, not vault dir. Must join with `REPO_ROOT` from `git rev-parse --show-toplevel`.

Only CRITICAL blocks commit (name missing in SOP area). MAJOR warns but allows.

## 4. Cross-Profile Distribution

```bash
cp -r skills/battle-test/* ~/.hermes/profiles/personal_profile/skills/battle-test/
```

Each profile needs its own copy of shared `utils.py`. Avoid cross-profile sys.path hacks.

## 5. Link Checker Indexed Cache

Pre-build a case-insensitive file stem index instead of per-link rglob:

```python
@classmethod
def build_index(cls, vault_path):
    index = set()
    for p in vault_path.rglob("*.md"):
        index.add(p.stem.lower())
    cls._index_cache[str(vault_path)] = index
```

## 6. A/B Test Structure

```
ab-test/
  SKILL.md
  scripts/
    ab_test_runner.py    ← --type parser|prompt|vault
    ab_parser.py         ← Strict vs Lenient
    ab_prompt.py         ← Concise vs Detailed
    ab_vault_struct.py   ← Tag vs Folder
```

Each comparator returns: `{winner, reason, A, B, delta}`
