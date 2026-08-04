# Lock Protocol — Multi-Cron Coordination (.write_lock)

Khi nhiều LLM-driven cron jobs cùng prepend vào shared files (AUTOMATION_HEALTH.md, COST_LOG.md), dùng lock file để tránh corrupt dữ liệu.

## Lock File

`vault/.write_lock` — hidden file, auto-cleared.

## Shell Environment (⚠️ CRITICAL)

The `terminal` tool runs **git-bash (MSYS)**, NOT Windows cmd.exe. All lock commands must use POSIX syntax.

| Action | ❌ Windows cmd.exe (DO NOT USE) | ✅ POSIX / git-bash (USE THIS) |
|--------|-------------------------------|-------------------------------|
| Check lock | `if exist path (echo locked) else (echo free)` | `test -f path && echo locked \|\| echo free` |
| Check age (mod time) | `dir path` | `stat -c %Y path` |
| Create lock | `echo %time% > path` | `echo "$(date)" > path` |
| Release lock | `del path` | `rm -f path` |

> **Why this matters:** `if exist` is a cmd.exe builtin — git-bash throws `syntax error near unexpected token '('`. Writing crons that pass this to the terminal tool means they silently fail the lock check, skip the entire Post-Run section, and don't notice. Always use `test -f` at minimum.

## Protocol (trong mỗi cron prompt)

```markdown
#### Lock protocol (shared files)
Before writing to shared files:
1. Check lock: run `test -f vault/.write_lock && echo locked || echo free` in terminal
2. If locked: check age via `stat -c %Y vault/.write_lock` (epoch seconds). Compare with `date +%s`.
   If <30s old → wait 5s, retry. Max 3 attempts.
3. If free or lock stale (>30s): create lock via `echo "$(date)" > vault/.write_lock`
4. Write entries (patch / write_file)
5. Release: `rm -f vault/.write_lock`
```

### Path resolution note

When running from `Warren_OS_Local/` as workdir, use relative path `vault/.write_lock`.
When running from arbitrary workdir, use full MSYS path: `/c/Users/khoans/Documents/Warren_OS_Local/vault/.write_lock`
Using `test -f` works with both MSYS paths (`/c/...`) and relative paths.

## Rules

| Condition | Action |
|-----------|--------|
| Lock không tồn tại | Create + proceed |
| Lock tồn tại, age <30s | Wait 5s, retry (max 3) |
| Lock tồn tại, age >30s | Stale → override (delete + create) |
| Sau 3 retries vẫn locked | Write anyway (force) — tránh cron infinite loop |

## Cron Jobs Cần Lock

Tất cả LLM-driven cron viết vào shared files:
- col-queue-watcher (2m)
- review-queue-watcher (1m)
- daily-ops-brief (09:30)
- stock-broker-fetch + stock-route-pending
- mem0-cleanup (CN)
- audit-automation-weekly (CN)

## V1 Limitation

Lock protocol là **instruction trong prompt**, không phải code atomic. Race condition vẫn có thể xảy ra nếu 2 cron check lock cùng lúc. V1 chấp nhận rủi ro này — collision probability thấp (2 crons same second là rare).
