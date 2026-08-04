---
name: skill-audit-pitfalls
description: "warren audit false-positives: nested, dotfolder, prose."
version: 1.0.0
author: Hermes
category: devops
tags: [warren-profile, audit, skills, overlap, hygiene]
related_skills: [hermes-skill-audit, skill-bundle-audit, audit-claim-verification]
---
# skill-audit-pitfalls

## Why this skill exists

2026-07-26 warren-profile skill audit produced multiple false-positives that a reviewer-node (critic) caught. The base `hermes-skill-audit` skill is user-owned / external (do NOT patch it). These warren-specific pitfalls are captured here so future audits don't repeat them.

## Pitfalls (verify against disk, not assumptions)

1. **Nested skill resolution.** Skills live in category subfolders (`software-development/skill-dedup`, `ops/telegram-py-checklist`, `data-science/sqlserver-ikkopos-client`). A flat `ls <root>/<name>` returns nothing → looks "missing". ALWAYS resolve with `find <root> -maxdepth 2 -type d -name <name>` before concluding absent. Cron `skills:[...]` resolves by name across the tree, so it still works.

2. **Dotfolder script refs are NOT broken.** Many SKILL.md reference `scripts/foo.py` that actually live in `vault/.scripts/` or `profile/scripts/` (dotfolder convention, SOUL §5.2). A relative-existence check from the skill dir reports "missing" — false alarm. Resolve candidate missing scripts against `vault/.scripts/`, `profile/scripts/`, then whole vault, then whole profile BEFORE calling it broken.

3. **Prose placeholders are NOT broken refs.** `scripts/X.py`, `scripts/foo.py`, `references/X.md`, `scripts/_dump.txt` appear inside docs / pitfall examples / copy-paste templates. Filter them (regex `(^|/)(X|x)\.(py|md|sh)$|foo\.py|_dump\.txt`) before counting broken refs.

4. **Dangling-pointer claims need context.** A live SKILL.md mentioning an archived skill name (e.g. `pdf-parse`, `deep-research-stock`) is usually an **archive→live mapping table** written on purpose (e.g. in `hermes-curator-hygiene`), NOT a broken `related_skills` link. Verify no literal `related_skills: [archived-name]` before flagging. In the 2026-07-26 audit, 4 "dangling pointers" were all intentional mappings — false alarm.

5. **Critic must READ context, not COUNT mentions.** A subagent that regex-scans for skill names / path tokens and reports "N broken" without reading whether the token is docs vs real reference will over-claim (167 broken → actually ~44, mostly low-impact). Instruct any reviewer-node to classify each hit as real / prose / cross-folder / mapping before reporting.

6. **execute_code is blocked in some sessions** (approval mode) — use terminal bash loops for filesystem scans, not Python subprocess.

## Recommended audit sequence

1. `find <root> -maxdepth 2 -type d -name <skill>` for every name (never flat ls).
2. md5-compare profile vs global copies → IDENTICAL (redundant) / DIVERGED (keep).
3. For broken-ref scan: extract `scripts/|references/|assets/|templates/` tokens, drop prose placeholders, then resolve each basename across skill dir + vault/.scripts + profile/scripts + whole vault + whole profile. Only count STILL-MISSING after all 5.
4. For "dangling archive" claims: grep `related_skills:` for the archived name; if absent, it's a mapping doc, not broken.
5. Spawn reviewer-node with explicit instruction to classify, not just count.
