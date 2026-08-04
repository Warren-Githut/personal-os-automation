# SOUL Slim Refactor — Warren 2026-07-15

## Before / After
| Metric | Before | After |
|--------|--------|-------|
| Words | 2,997 | 1,132 (−62%) |
| Lines | 346 | 142 |
| Bytes | 21.7 KB | 8.1 KB |

## What moved where
- **§2 Memory Loop** (write governance, raw-log format, git-commit proposal, 9-step protocol) → skill `compress-memory/SKILL.md`
- **§6 Session Start** (10-step load order) → skill `session-start/SKILL.md`
- **§3 Vault Structure** table + **§7 Quick Reference** tables → deleted from SOUL, replaced with one-line pointers to `Warren_OS_Local/AGENTS.md` and the existing index files (`00_WIKI_INDEX.md`, `00_OPERATION_INDEX.md`, etc.)
- **Kept in SOUL:** §1 Identity, §4 Comms, §5 Core Rules, §5.1 Zones, §7 Search Priority (renumbered from §8).

## Dangling-reference verification (bash, run after rewrite)
```bash
SOUL="$HERMES_HOME/SOUL.md"   # Desktop: C:/Users/<u>/AppData/Local/hermes/profiles/<p>/SOUL.md
# 1. dead internal section pointers (old § that no longer exists)
grep -nE "§2\.|§3\.|§6\.|§8" "$SOUL" || echo "no dead § pointers"
# 2. referenced files must exist
for f in "$VAULT/AGENTS.md" "$VAULT/00_CORE_LOGIC/ONTOLOGY.md" "$VAULT/00_CORE_LOGIC/WARREN_MEMORY.md" "$VAULT/00_CORE_LOGIC/pre_edit_checklist.md" "$VAULT/00_CORE_LOGIC/CONTEXT.md" "$VAULT/00_CORE_LOGIC/TODAY.md"; do
  [ -f "$f" ] && echo "OK   $f" || echo "MISS $f"
done
# 3. relative path resolves from agent cwd — find the real file
find "$REPO_ROOT" -iname "AGENTS.md" 2>/dev/null
# 4. skill targets exist
for s in session-start compress-memory; do
  [ -f "$HERMES_HOME/skills/$s/SKILL.md" ] && echo "OK $s" || echo "MISS $s"
done
```

## Pitfalls caught this session
- `USER_GUIDE.md` referenced by AGENTS.md/SOUL but **never existed** → do not point to it; use the real `Warren_OS_Local/AGENTS.md`.
- `vault/AGENTS.md` wrong — actual path is repo root `Warren_OS_Local/AGENTS.md`. Always `find` before trusting a hardcoded path.
- After renumber (§8→§7) the SOUL body still cited "§8 Search" → propagated to §7 before finishing.
