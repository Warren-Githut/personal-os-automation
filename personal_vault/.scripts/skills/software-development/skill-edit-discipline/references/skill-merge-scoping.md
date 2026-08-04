# Skill Merge / Converge Scoping — Recipe & Decision Table

> Companion to skill-edit-discipline Pitfall 10. Run this BEFORE proposing any
> "merge these two skills" or "dedup over add" plan. Catches the two failure
> modes that bit session 2026-07-25: (a) underestimating blast radius,
> (b) mistaking mode-differentiated skills for true duplicates.

## 1. Grep the FULL tree for BOTH skill names

```bash
cd /c/Users/khoans/AppData/Local/hermes/profiles/warren-profile
grep -rln "skill-a" skills cron memories pending 2>/dev/null
grep -rln "skill-b" skills cron memories pending 2>/dev/null
# also check vault + SOUL for hard references
grep -rln "skill-a" "C:/Users/khoans/Documents/Warren_OS_Local/vault/00_CORE_LOGIC" 2>/dev/null
```

- Count hits PER FILE. A naive read of the 2 candidate SKILL.md files misses
  cross-references inside other skills' bodies, `references/*.md`, and memory.
- **Session 2026-07-25 reality:** `code-simplification` appeared in ~25 files
  (skills + reference docs + 1 memory), NOT 2. A "merge + re-point" plan would
  have been 25-file churn — rejected in favor of light-converge (Option 1).

## 2. Classify the relationship

| Signal | TRUE DUPLICATE → merge | MODE-DIFFERENTIATED → cross-link only |
|--------|------------------------|----------------------------------------|
| Trigger/intent | Same job, same cost | Different cost/intent tiers |
| Example | two "summarize" skills | `code-simplification` (inline, cheap, L'Usine pitfalls) vs `simplify-code` (4-agent parallel, expensive, 4 altitudes) |
| Correct fix | absorb one into other, delete | add router route + mutual "Relationship" sections |
| Warren rule | "merge over keep" applies | "merge over keep" YIELDS — converge via link |

## 3. Check for a bundled shadow

```bash
ls -la /c/Users/khoans/AppData/Local/hermes/skills/common/**/skill-a/ 2>/dev/null
```
- If a bundled copy exists, deleting the profile override resurrects the bundled
  version (WITHOUT custom content like L'Usine pitfalls). The survivor MUST be
  the profile override, never the bundled one.

## 4. Edit-guard check (router only)

`using-agent-skills` is manually-authored (created_by=None); memory f02db674
records the runtime may refuse autonomous patches. When editing it, prepare a
ready-to-apply diff for Warren to apply manually if the guard trips.

## 5. Decision flow

```
Think two skills overlap?
  ├─ grep full tree → how many real references?
  │    └─ >5 → light-converge (cross-link), NOT destructive merge
  ├─ mode-differentiated? → cross-link + router routes (KEEP BOTH)
  ├─ true duplicate? → merge, BUT survivor = profile override (not bundled)
  └─ editing using-agent-skills? → prep manual-edit diff fallback
```
