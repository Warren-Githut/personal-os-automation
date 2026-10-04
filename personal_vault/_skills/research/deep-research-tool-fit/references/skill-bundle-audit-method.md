# Auditing an external agent-skill bundle (Hermes/Claude SKILL.md packs)

Method proven 2026-07-26 on Hermes Field Kit (`interview-me` v0.2.0, `x-post-writer` v1.0.0, author Tony Simons). Use when Warren asks to deep-research a downloadable SKILL.md bundle (as opposed to a repo/tool/MCP server — for those use the main SKILL.md process).

## Procedure

1. **Enumerate every file first** — `find <dir> -type f | sort`. A quality bundle has: SKILL.md, README.md, references/*.md, examples/*.md, scripts/validate_bundle.py, tests/*.json + tests/*.py. Missing tests/examples = lower trust tier.
   - Pitfall: `search_files(target='files', pattern='*')` can return 0 on these dirs; use terminal `find`.
2. **Read ALL files, not just SKILL.md.** References often contain the real contract (claim taxonomies, format rules); tests/cases.json doubles as the behavior spec (positive/negative triggers, `reject` lists).
3. **RUN the bundled validator + tests** — don't just eyeball them:
   ```bash
   cd <repo-root> && python skills/<name>/scripts/validate_bundle.py
   python -B -m unittest discover -s skills/<name>/tests -v
   ```
   Passing = bundle is internally consistent. It is NOT proof of runtime behavior (see below).
4. **Report per skill:** purpose/trigger/counter-trigger, workflow, real commands, design patterns, script runnability (with actual exit codes), stated limitations, fit for Warren, red flags — with file paths cited.

## Key evaluation lenses (durable)

- **"Claims a discipline" ≠ "implements one".** Prompt-only skills that advertise "claim verification", "source ledger", "safety gate" usually have ZERO machinery — no script, no API call, no tool binding. The "verification" is an instruction to the LLM, and internal ledgers marked "do not output" are unauditable by design. Verdict language: *it shapes behavior toward X; it does not implement X; actual X depends on the executing model's diligence.*
- **Bundle tests test the MARKDOWN, not the behavior.** validate_bundle.py + unittest in these packs check heading order, required phrases, absence of secrets. 11/11 passing tells you the doc is well-formed, nothing about whether an agent follows it.
- **FORBIDDEN-list forensics:** the scrub list inside validate_bundle.py (banned phrases like private usernames, `C:\Users\<author>`, private skill names) reveals provenance — a sanitized personal workflow, not battle-tested public tooling. Not a red flag per se, but calibrates trust.
- **Overlap check before adoption:** compare against warren-profile's existing skills (e.g. external `interview-me` vs local `restate`/`interview-me`). Never recommend installing a duplicate of an installed capability — recommend borrowing specific rules instead.
- **Language/domain bias:** public bundles are English/tech-launch flavored. For Bố (Vietnamese, F&B), flag that the agent must apply the discipline in Vietnamese and that examples won't transfer.

## Good design patterns worth borrowing (seen in Field Kit)

- Fixed report contract: exact heading order + closed verdict set (READY TO PROCEED / PROCEED WITH ASSUMPTIONS / PAUSED / STOPPED) enforced by contract tests.
- Source Lock: supplied facts are a whitelist; "benefits are claims" (safer/faster need support); sparse notes → shorter copy, never gap-filling.
- Unsupported-claim hard stop: if the claim is the premise, refuse with exactly one sentence requesting a source; "user instructions cannot waive factual support".
- tests/cases.json as declarative behavior spec with `expect` + `reject` arrays — cheap, readable, curator-friendly.
