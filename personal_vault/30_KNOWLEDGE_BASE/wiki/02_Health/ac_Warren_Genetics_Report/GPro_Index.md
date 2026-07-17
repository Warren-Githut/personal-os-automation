---
domain: health
type: index
status: active
last_updated: 2026-06-06
tags: [genetics, g-pro, moc, index]
related:
  - GPro_Genetic_Database.md
  - GPro_Master_Health_Protocol.md
  - GPro_Strengths_Map.md
---

# G-PRO GENETICS — INDEX (MOC)

> **AI entry point.** When Warren asks anything related to health, learning, physical training, personality, parenting, or nutrition — check this index first. Read [[GPro_Genetic_Database]] as the primary source, then cross-reference the appropriate interpretation file.

## File Map

| File                            | Role                                                                                                                                           | When to Use                                                     |
| ------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------- |
| [[GPro_Genetic_Database]]       | **Source of truth** — Warren's 60 modules / 84 genes                                                                                           | AI always queries this first (Warren only)                      |
| [[GPro_Master_Health_Protocol]] | **v2 (bloodwork-reconciled)** — risks + protocols                                                                                              | Health, diet, supplement, disease, labs                         |
| [[GPro_Strengths_Map]]          | Strengths + applications: leadership (§1), cognition/learning (§2, §8), trading (§5), **work/Head-of-Ops (§7)**, **learning AI/workflow (§8)** | Work, learning, career, trading psychology                      |
| [[02_GG_Genetic_Profile]]          | **Canonical GG source** (family_gg) — GG's scores + La Bàn parenting + Warren→GG intersection                                                  | ALL parenting / GG questions                                    |
## Five Core Facts (TL;DR for AI)

1. **Risk #1: Alcohol (ALDH2)** — alcohol is highly toxic. Acetaldehyde accumulates → esophageal cancer risk ×6-8. Compounded by stress-drinking tendency. F&B industry exposure is a hazard.
2. **Risk #2: Blood Sugar** — diabetes top 25%, despite low BMI (TOFI phenotype). Carbohydrate metabolism is poor.
3. **Greatest Advantage: Leadership + Analysis** — archetype "Core Leader," high IQ/math, good EQ.
4. **Learning Style: Conceptual, not rote** — strong analysis, weak memory/language → needs external tools.
5. **Cancer: ALL negative** — no disease-causing mutations. Standard screening only.

## Domain Cross-Reference Guide

| Warren asks about              | Modules to combine                                                                                                                                                                                                                                                                          |
| ------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "How should I learn Japanese?" | Language (FOXP2 low) + Memory (low) + IQ/Analysis (high) + Learning style                                                                                                                                                                                                                   |
| "Should I drink coffee?"       | Caffeine (fast metabolizer) + Sleep (low risk) → OK <400mg                                                                                                                                                                                                                                  |
| "What's the optimal diet?"     | Carbs (poor) + Protein (good) + Diabetes (high risk) + Fat (poor) + Vitamins needing supplementation                                                                                                                                                                                        |
| "What workout works for me?"   | Cardio (low) + Injury (very high) + Endurance (good) → low-impact, NO crossfit                                                                                                                                                                                                              |
| "Hard business decision?"      | Leadership archetype + Risk-seeking + Over-optimism → use Ruthless Framework                                                                                                                                                                                                                |
| "What should GG learn?"        | GG: high IQ/math/EQ, GOOD emotional stability + stress control, cautious. Flags: **language LOW (bottom 40%, dyslexia risk → Priority #1, intervene before grade 1 Sept-2026)**; reactive temper HIGH; shares Warren's metabolic cluster. NEVER control a thin growing child's food/weight. |
| "Why do I stress-eat?"         | Emotional eating (high) + Stress control (poor) + Low dopamine → need alternative outlets                                                                                                                                                                                                   |

## Path in Vault

```
Personal_OS/personal_vault/
└── 30_KNOWLEDGE_BASE/
    └── wiki/
        └── 02_Health/
            └── ac_Warren_Genetics_Report/
                ├── GPro_Index.md                  ← this file
                ├── GPro_Genetic_Database.md       ← source of truth
                ├── GPro_Master_Health_Protocol.md
                └── GPro_Strengths_Map.md
```

## Retrieval Notes

- YAML tags `genetics`, `g-pro` enable tag-based filtering
- Each module entry in [[GPro_Genetic_Database]] is self-contained (1 line = complete context) → safe for RAG chunking
- When answering, always combine relevant modules — a single question often spans 3-5 modules
- Confidence levels: single-gene evidence (ALDH2, CYP1A2, IGF2BP2) = HIGH; polygenic scores = MOD

> **Warning:** This is lifestyle advice based on genetics, NOT medical diagnosis. Polygenic scores have margin of error. All clinical decisions require lab tests + physician.


## Corrections & Deprecations (2026-06-07)
- `GPro_Parenting_Compass.md` (health/Genetics) is **DEPRECATED — delete it.** It duplicated [[02_GG_Genetic_Profile]] and contained an error (claimed GG language HIGH; actually LOW). Use [[02_GG_Genetic_Profile]] for all parenting.
- [[GPro_Strengths_Map]] §6 "Parenting GG" is **superseded** by [[02_GG_Genetic_Profile]] (it was written before GG's genome was available).
