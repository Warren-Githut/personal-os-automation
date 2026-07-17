---
domain: meta
tags: ["meta"]
type: log
status: active
last_updated: 2026-06-08
name: DECISION_LOG
---

# Closed Decisions Archive

> Open decisions are tracked in vault directly. When closed → move here.

## 2026-05-17 — Rename vault folder `vault/` → `personal_vault/`
- **Why:** Obsidian dùng folder name làm display name. Cả 2 vault (Warren_OS_Local + Personal_OS) đều tên `vault` → không phân biệt được trong picker.
- **Alternatives considered:** giữ nguyên, dùng workspace bookmark thay vì rename.
- **Outcome:** rename folder, update toàn bộ hardcoded paths (auto_git_sync.ps1, run_auto_git_sync.cmd, settings.json, CLAUDE.md, README.md, DECISION_LOG). Git remote không đổi.

## 2026-05-17 — Vault structure: SEPARATE Personal_OS vault (not sub-folder of L'Usine)
- **Why:** privacy by structure (data ly thân/health/trade không lẫn git history L'Usine); persona riêng; permission/backup độc lập.
- **Alternatives considered:** sub-vault in Warren_OS_Local, shared with persona switch.
- **Outcome:** vault tại `C:/Users/khoans/Documents/Personal_OS/personal_vault/`, git + Drive sync như L'Usine.
