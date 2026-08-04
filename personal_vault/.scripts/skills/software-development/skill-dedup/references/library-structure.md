# Library Structure Guidelines

## Goal
Structure the Hermes skill library as CLASS-LEVEL umbrellas. Each umbrella skill:
- Has a rich SKILL.md with identity, triggers, cross‑reference to related skills.
- Contains a `references/` directory for session‑specific detail (error transcripts, reproduction recipes, provider quirks) and condensed knowledge banks.
- May contain a `templates/` directory for starter files (configs, scaffolding).
- May contain a `scripts/` directory for reusable verification or fixture scripts.

## Directories
- `references/` – Markdown notes, external docs, API excerpts, session‑specific reproduction steps.
- `templates/` – Boilerplate configs, example files, scaffolding to copy.
- `scripts/` – Runable Python/batch scripts for verification, fixture generation, deterministic probes.

## Naming
- Class‑level names are lowercase, hyphenated, ≤64 chars, and reflect the function (e.g., `skill-dedup`, `audit-automation`).
- Avoid session‑specific codenames, PR numbers, or feature codenames.

## Publishing
- When adding a new umbrella, create the skill folder, add SKILL.md with required sections, and optionally add support files.
- Pin critical skills to prevent auto‑archive.
- Update `audit-automation` cross‑check notes when library‑drift is detected.

## Maintenance
- Run `skill-dedup` periodically to detect duplicate basenames vs front‑matter name collisions.
- Review `references/` for stale content; archive or purge when no longer relevant.
- When user corrects style, tone, or workflow, embed the correction as a pitfall or explicit step in the governing skill.