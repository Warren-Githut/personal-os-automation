# Profile Consolidation Case Study: Warren's Single Canonical Source (2026-06-22)

## Context

**User:** Warren (Head of Ops, L'Usine Saigon) — non-IT, Vietnamese-first, system thinker

**Before (3 profiles with skills):**
| Profile | Skills | Vault | Domain |
|---------|--------|-------|--------|
| `warren-profile` | 75 (canonical) | `Warren_OS_Local/vault` | L'Usine ops (LU3/LU5/LU7) |
| `lusine-profile` | 45 | `Warren_OS_Local/vault` | L'Usine ops (legacy, leaner) |
| `personal_profile` | 49 | `Stock_OS/stock_vault` | Personal finance, trading, health, legal |

**Decision:** Strip ALL skills from `lusine-profile` and `personal_profile`. Keep `warren-profile` as the single canonical source for ALL Hermes skills. The other 2 profiles become "thin shells" — no skills, zero commands, vault access only.

## Why Not Merge?

The earlier analysis (2026-06-18) recommended merging all profiles into one. Warren's decision is different:

| Approach | Action | When |
|----------|--------|------|
| **Merge** | Delete 2 profiles, keep 1 with all skills + domain-namespacing | When user wants ONE profile for everything |
| **Single Canonical Source** | Keep profiles but strip skills from all but master | When user wants separate profiles for different vault contexts, but ALL commands come from ONE place |

Warren chose Single Canonical Source because:
1. `warren-profile` is already the primary work profile (95% usage)
2. `personal_profile` is occasionally useful for its AGENTS.md / vault context
3. "Tôi ko muốn những profile còn lại có bất kỳ command/script/parser/skill nào cả"
4. No unique skills in non-master profiles (verified: 0 unique in personal_profile)

## Pre-Requisites Verified

Before stripping:
- ✅ `personal_profile` had 0 unique skills (all 49 already in warren-profile's 75)
- ✅ 7 cron jobs all reference warren-profile skills or vault scripts — no profile-specific paths
- ✅ vault-structure-audit SKILL.md synced across all 3 profiles (warren canonical)

## Actual Execution

**Phase 1 (same session):** vault-structure-audit --execute
- 31 frontmatter normalizations (priority + status casing)
- 3 BOM strips (LESSONS.md + 2 AGENTS.md)
- Personal vault frontmatter_template schema fix (work → personal domain)
- Root READMEs created for both vaults
- 9 duplicate case files resolved (active copies of closed cases deleted)

**Phase 2 (planned, not yet executed):**
- `rm -rf ~/AppData/Local/hermes/profiles/lusine-profile/skills/`
- `rm -rf ~/AppData/Local/hermes/profiles/personal_profile/skills/`

## Result State (Target)

```
warren-profile  (75 skills)  ← ALL commands, scripts, parsers, skills
lusine-profile  (0 skills)   ← thin shell, vault .obsidian + config only
personal_profile (0 skills)  ← thin shell, vault .obsidian + config only
```

## Post-Mortem Correction (2026-06-23)

**What went wrong:** The initial "Single Canonical Source" strategy stripped ALL skills from non-master profiles. This broke cross-profile skill loading because skills are per-profile — Hermes Desktop only loads from the active profile's `skills/` directory.

**Fix applied:** Windows directory junction (`mklink /D` via Python subprocess) from:
- `personal_profile/skills/personal-commands/` → `warren-profile/skills/personal-commands/`

**Lesson:** "100% centralized" requires cross-profile access solution. Strip skills from thin profiles, but create junctions for shared skill categories so they remain accessible. Verify by switching to thin profile and loading a skill — not just by checking file count in master profile.

**Technique documented in:** `references/cross-profile-junction-technique.md`

**Different from "merge profiles":** Single Canonical Source keeps profiles for their AGENTS.md, vault paths, and Obsidian config — but strips executable code. User switches profiles for vault context, switches to master for commands. This is simpler to understand: "There's only ONE place where commands live."

This is the right answer for non-IT users who want:
- One mental model ("my commands are in warren-profile")
- Zero maintenance overhead (no syncing skills across profiles)
- Full control (can delete or keep thin shells without breaking anything)