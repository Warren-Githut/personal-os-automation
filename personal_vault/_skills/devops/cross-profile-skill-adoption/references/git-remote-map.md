# Git Remote Map per Profile (2026-07-22, Warren approved)

> Dùng khi deploy skill cross-profile và cần commit/push. Tránh lãng phí thử push repo đã xóa.

## Reality check (máy Warren, 2026-07-22)

| Profile / Repo | Path | Git? | Remote | Push? |
|---|---|---|---|---|
| **vault Warren_OS_Local** | `C:/Users/khoans/Documents/Warren_OS_Local` | yes | `git@github.com:Warren-Githut/lusine-kilo-automation.git` (DELETED 404) | FAIL local commit only |
| **warren-profile** | `AppData/Local/hermes/profiles/warren-profile` | yes | trỏ vault repo đã xóa no valid remote | NEVER push local commit only |
| **stock-profile** | `AppData/Local/hermes/profiles/stock-profile` | yes | `https://github.com/Warren-Githut/stock-profile.git` | OK |
| **personal_profile** | `AppData/Local/hermes/profiles/personal_profile` | NO (.git absent) | n/a | n/a runtime only |
| **personal_vault** | `C:/Users/khoans/Documents/Personal_OS/personal_vault` | yes | `https://github.com/Warren-Githut/personal-os-automation.git` | OK (Bố hay gọi nhầm personal-os-vault) |

## Key facts
- `stock-profile/skills` + `personal_profile/skills` = symlink trỏ warren-profile/skills. Patch skill 1 lần = 3 profile chung.
- `skills/` bị `.gitignore` ở mọi profile skill patch KHÔNG vào git, chỉ nằm disk. Chỉ `SOUL.md` (tracked) đáng commit.
- `personal_vault` (Documents) là vault thật có git; `personal_profile` (AppData) là runtime, không git.

## Push recipe (deploy forced-critic style)
```bash
# 1. warren: patch skills (symlink shared) + SOUL.md note, commit local ONLY
cd /c/Users/khoans/AppData/Local/hermes/profiles/warren-profile
git reset >/dev/null 2>&1; git add SOUL.md; git commit -m "feat(safenet): forced critic note"
# KHÔNG push (no valid remote)

# 2. stock: SOUL.md note, commit + push
cd /c/Users/khoans/AppData/Local/hermes/profiles/stock-profile
git add SOUL.md; git commit -m "feat(safenet): forced critic note"; git push   # OK

# 3. personal: vault repo, SOUL note nếu có, commit + push
cd /c/Users/khoans/Documents/Personal_OS/personal_vault
git add <changed>; git commit -m "..."; git push   # OK
# personal_profile AppData: KHÔNG git, skip
```

## Gotchas
- `git add -A` trong profile repo cuốn rác state (gateway.pid, pending/memory/*.json, cron/jobs.json). Dùng `git reset` (mixed) + chỉ `git add SOUL.md`.
- Vault remote deleted đừng re-check / re-add remote trừ khi Bố bảo. Commit local là đủ.
- Bố nhớ repo personal là `personal-os-vault` nhưng thực tế là `personal-os-automation` dùng đúng tên khi `git remote -v`.
