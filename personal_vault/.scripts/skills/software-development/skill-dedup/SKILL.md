---
name: skill-dedup
description: Find and consolidate duplicate-named skills within a Hermes profile's skills directory. Detects name-collision traps (basename match vs actual frontmatter `name:`), classifies each pair as stub-vs-full (safe merge/delete) or divergent fork (must ask user), backs up before deleting, and proactively scans the whole problem class when the user says "fix all" / "dọn luôn". Use when the user reports a skill "has 2 versions" or you notice the same skill name resolving from two paths.
---

# Skill Dedup & Consolidation

## When to use
- User reports a skill loads the "wrong" version, or says a skill "has 2 copies" / "trùng tên".
- You are auditing the skill library and want one canonical file per skill name.
- User says "fix all" / "dọn luôn" after one fix — scan for the rest of the same problem class in the same pass.
- **Library‑Structure Signal**: The user wants the skill library shaped as CLASS‑LEVEL umbrellas with rich SKILL.md and a `references/` directory for session‑specific detail, not a flat list of narrow one‑off skills. When this preference appears, update the relevant skill to embed the pattern and add support files under `references/`, `templates/`, or `scripts/` as appropriate.

## Procedure
1. **Find duplicate basenames.** List all `SKILL.md` under the profile skills dir and surface names appearing in 2+ locations. Exact command in `references/dedup-workflow.md`.
2. **Verify the actual `name:` field, not just the folder.** Basename match is a FALSE-POSITIVE trap: folder `agent-skills/` held a skill whose frontmatter `name:` was `apply-agent-skills` — a different skill, keep both. Always read the YAML frontmatter before concluding a collision.
3. **Diff the true duplicates.** Classify each pair:
   - **stub-vs-full**: one file is a short stub that defers to another ("extends skills/common/...") while the other is the full process. → SAFE to merge the stub's unique additions into the full file, then DELETE the stub. (Case: `interview-me` — nested `productivity/interview-me` stub merged into top-level, then removed.)
   - **divergent forks**: both files are full skills with different version/content (dozens–hundreds of differing lines). → DO NOT auto-merge. Back up both, then ASK the user which to keep. Merging would silently drop real SOP content. (Case: `stock-price-sync`, `test-driven-development`, `vault-restructure` — each a different fork; user must choose.)
4. **Backup before any delete.** Copy both originals into `<skills>/_archive_<name>_<YYYY-MM-DD>/` so every delete is reversible.
5. **Decide per group** (zone 🔴 for structural change — ask the user which to keep/delete, unless it's a clear stub-vs-full where merge+delete is low-risk).
6. **Delete with `rm -rf`** (POSIX bash on Windows), NOT `rmdir //s //q` (that's cmd.exe syntax and fails under bash).

## Pitfalls
- **Basename ≠ name.** Folder `agent-skills` ≠ skill `apply-agent-skills`. Read frontmatter.
- **Divergent forks are NOT redundant.** Diff line counts; if >~50 lines differ, treat as separate skills. Auto-deleting loses real content.
- **patch tool path quirk (Windows):** `patch` resolves `/c/Users/...` as RELATIVE to the active workspace and refuses ("outside the active workspace"). Pass the Windows absolute path `C:\Users\khoans\...` instead. (Also: `execute_code` is blocked under cron profiles — use normal tools.)
- **Don't keep as a deprecated note.** Warren rule: when he says "xóa", DELETE ENTIRELY — never leave a "deprecated, see X" stub line. Same for skills: remove the folder, don't replace it with a redirect.

## User preferences (Warren)
- **Delete entirely, no deprecated residue.** `rm -rf` the folder; do not leave a pointer stub.
- **Proactive "fix all".** After fixing one duplicate, scan for the whole class and propose cleaning the rest in the same pass — don't wait to be asked per item.
- **Show the decision table.** For each duplicate group present: locations, line counts, classification (stub-vs-full / divergent), recommended keep/delete, then ask. Conclusion-first.

## Reference
- `references/dedup-workflow.md` — exact bash commands (find dups, verify name, diff, backup, delete) + the `interview-me` and 3-fork case studies.
- `references/library-structure.md` — guidelines for structuring the skill library as class‑level umbrellas, naming conventions, directory usage, and maintenance.
