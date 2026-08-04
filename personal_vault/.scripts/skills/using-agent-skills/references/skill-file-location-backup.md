# Skill File Location & Backup Governance (Warren-laptop, 2026-07-12)

## The problem
Custom Hermes skills for warren-profile live at:
```
C:/Users/khoans/AppData/Local/hermes/profiles/warren-profile/skills/<name>/
```
This path is **OUTSIDE** the vault git repo (`C:/Users/khoans/Documents/Warren_OS_Local`).
`git` run inside the vault repo reports `"<path> is outside repository"` for any skill
edit → you CANNOT commit/push skill changes through the vault repo.

## Backup workflow (approved by Warren 2026-07-12)
1. Edit skill in place at `AppData/.../skills/<name>/SKILL.md` (this is what Hermes loads at runtime).
2. Copy the changed file into the vault (which IS in the tracked repo):
   ```
   vault/_archives/skills/<name>_SKILL_backup_YYYY-MM-DD.md
   ```
3. Commit/push the vault repo normally — the backup rides along with other vault changes.

## DO NOT
- `git init` a separate repo inside the skills folder and push to GitHub.
  Reason: skills contain L'Usine work-product (ops logic, store targets, revenue
  patterns). Pushing to an external remote from a **company laptop** = data-exfiltration
  risk / likely IT-policy violation. Warren explicitly rejected this on 2026-07-12.

## Bundled vs custom (reminder)
- Bundled skills: `C:/Users/khoans/AppData/Local/hermes/skills/common/...` → DO NOT EDIT.
- Custom skills: `.../profiles/warren-profile/skills/...` → editable, overrides bundled.
- `using-agent-skills` exists in BOTH trees — always edit the **warren-profile** copy.
