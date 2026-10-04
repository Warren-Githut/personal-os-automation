---
name: vault-content-placement
description: "Decide where to file new reference content in the Personal OS vault (stock-profile). Index-first, DEDUP-CHECK existing files BEFORE proposing a new file, and route by content type. Triggers on 'where do I add X to my vault', 'should I create a file for this formula/framework'."
type: skill
---

# Vault Content Placement — dedup-first filing

## When to use
- User shares a video/article/formula and asks "where should I add this to my vault?"
- User asks whether to create a new vault file for some reference content
- You are about to CREATE a new wiki file and have NOT confirmed the content isn't already there

## Workflow (in order)
1. **Index-first.** Read `30_KNOWLEDGE_BASE/wiki/RETRIEVAL_MAP.md`, then `00_WIKI_INDEX.md`. Know the canonical folder for the domain (investing → `03_Investing/`).
2. **DEDUP CHECK (critical, easy to skip).** BEFORE proposing a new file, SEARCH existing files for the same content. Company valuation formulas often already live inside `030-Companies/{TICKER}/Thesis.md` (e.g. GAS §5B "Peter Lynch PEG/PEGY"). Use `search_files` with a content pattern. If found — say "already in {file} §X" and STOP. Do NOT create a duplicate.
3. **Canonical vs legacy folder.** `03_Investing/` is canonical (in RETRIEVAL_MAP). `investing/` (lowercase) is LEGACY/STALE — do NOT write there. Same for any path not present in RETRIEVAL_MAP.
4. **Route by content type:**
   - Macro/sector mental model (oil, rates, FX spillovers) → `03_Investing/Frameworks.md` (append, newest on top; do NOT put valuation formulas here)
   - Valuation formula / ratio → usually ALREADY in a company Thesis.md valuation section; only create a dedicated `Valuation_CheatSheet.md` if it is genuinely cross-company AND absent everywhere
   - New company → `030-Companies/{TICKER}/` with Thesis / Anti-thesis / BCTC / Catalyst-watch
5. **Terse response** if user says "chỉ trả lời" / "only answer" — lead with the verdict, drop the explanation.

## Pitfalls
- **Proposing a new file without a dedup search.** Got caught this session: user shared a PEGY YouTube video; I proposed a new CheatSheet, but `031-GAS/Thesis.md §5B` already had PEG/PEGY with matching numbers. Always search first.
- **Writing to legacy `investing/` folder.** It is stale (e.g. VNINDEX 1300) and absent from RETRIEVAL_MAP. Use `03_Investing/`.
- **PEGY/PEG with negative growth.** Formula `PEGY = P/E / (growth% + yield%)` breaks when growth is negative. FY2024 GAS: growth -9% yielded a stored PEGY of 1.72 that does NOT match the formula. Flag the convention when growth < 0; the <1 "undervalued" rule only holds for positive growth.

## Verify
- After deciding, state the exact target path AND confirm via search that no duplicate exists.
- If creating: follow the stock-profile pre-edit checklist (frontmatter, Vietnamese diacritics, newest-on-top).

## References
- `references/valuation-formulas.md` — PEG/PEGY verification example (GAS §5B) + canonical formula definitions.
