# ONTOLOGY — `type:` Vocabulary Scan & Reconciliation

> Reusable probe for keeping `00_CORE_LOGIC/ONTOLOGY.md` in sync with the REAL vault `type:` values.
> Born 2026-07-11: Warren sent an external article on ontology-constrained agent memory; we adopted the *principle* (schema written down = guardrail) but NOT auto-KG extraction, and encoded the vault's existing typed-frontmatter structure into `ONTOLOGY.md`. First live "ontology check" caught 15 missing `type:` values immediately.

## When to run
- On-demand: Warren says `"ontology check"` / `"ontology còn khớp ko"`.
- As part of `/compress-memory` (added scan step).
- After any manual file/folder creation outside Hermes (drift catch).

## Scan command (vault root)
```bash
cd /c/Users/khoans/Documents/Warren_OS_Local/vault
# 1. All distinct type: values + counts
grep -rhoE '^type:[[:space:]]*[a-zA-Z_/]+' --include=*.md . | sed 's/^type:[[:space:]]*//' | sort | uniq -c | sort -rn
# 2. Top-level + depth-2 folder tree (detect new folders = new node class)
find . -maxdepth 1 -type d | sort
find . -maxdepth 2 -type d | grep -vE '^\./\.git' | sort
# 3. Which files use a NON-ontology type: (drift detail)
for t in reference spec log ssot rolling plan ...; do
  echo "--- type: $t ---"; grep -rl "^type:[[:space:]]*$t\$" --include=*.md . 2>/dev/null | head -4
done
```

## Verify coverage (all vault type: present in ONTOLOGY.md §2B)
```bash
vals=$(grep -rhoE '^type:[[:space:]]*[a-zA-Z_/]+' --include=*.md . | sed 's/^type:[[:space:]]*//' | sort -u)
missing=0
while IFS= read -r v; do
  [ "$v" = "string" ] && continue   # pseudo-value only in RULES.md comment
  grep -q "\`$v\`" 00_CORE_LOGIC/ONTOLOGY.md || { echo "MISSING: $v"; missing=1; }
done <<< "$vals"
[ "$missing" -eq 0 ] && echo "✅ ALL vault type: covered by ONTOLOGY.md"
```

## ONTOLOGY.md structure (canonical)
- §2A Domain Nodes (10 core: Store/Case/Supplier/Policy/KPI/Person/Dashboard/Initiative/Lesson/Decision) — semantic edges.
- §2B File-Class Nodes — **full `type:` vocabulary** (23 values from 2026-07-11 scan, counts included). Every new `.md` MUST use one of these.
- §3 Edge Types (wikilink / SSOT-chain / index→file / case→supplier / case→lesson / policy→decision) + source/target constraints.
- §4 Guardrails (zone 🔴: new folder / new `type:` / rename-SSOT = must ask Warren + update schema).
- §5 Reconciliation Protocol — 3 triggers that force Hermes to update ONTOLOGY.md.
- §6 `## 🔄 Reconciliation Log` — date + what-changed, so Warren can verify.

## Key principle (from the article, adapted)
External insight: *vector/flat memory breaks on multi-hop reasoning; knowledge graph only helps if schema is defined upfront (typed entities + typed edges), NOT left to LLM auto-extraction.*
Warren's adaptation: he ALREADY has a typed schema (frontmatter `type:`, index registry, wikilinks, SSOT chain) maintained by humans — better than LLM-extracted. So we WRITE IT DOWN as ONTOLOGY.md (guardrail) instead of adopting auto-KG. No file-watcher exists; reconciliation is event-driven (3 triggers above).
