---
created: 2026-09-29
---
# Bulk Mirror Sync — AppData skills → vault/_skills/

> Khác `skill-sync` (sync 1 skill → `.scripts/skills/` SSOT). Mirror = bulk copy toàn bộ skills sang `_skills/` để GitHub track. Hermes vẫn load từ AppData.

## Khi nào dùng
- Cần backup toàn bộ skill library lên GitHub
- Sau khi patch nhiều skills, muốn snapshot
- Mới cài Hermes, muốn version-controlled skill library

## Script
`vault/scripts/sync_skills_to_vault.sh` — chạy manual hoặc cron weekly.

## Quy tắc
- **Hermes không đọc từ `_skills/`** — chỉ track. Primary = AppData.
- **`.gitignore` exclude:** `_skills/**/__pycache__/`, `_skills/**/.pytest_cache/` — chỉ giữ SKILL.md + references + scripts + templates.
- **Commit message:** `chore: sync skills from AppData (YYYY-MM-DD HH:MM)`
- **Log:** `vault/logs/sync_skills.log`

## Pitfall
- `cp -av` sang `_skills/` rồi git add → đang trong git-bash Windows → dùng `git add -f _skills/` nếu git ignore do cache exclude pattern.
- Commit trước khi patch xong → snapshot chứa bản dở. Mirror chỉ chạy khi đã patch xong (hoặc weekly cron tự động).
