---
name: windows-gitbash-msys-path
description: MSYS path conversion pitfalls when running native Windows Python from git-bash on this Hermes Desktop host. Covers the AppData path to vault-relative workaround AND the search_files empty-result false-negative on Windows MSYS.
status: active
created: 2026-07-16
version: 1.1
triggers:
  - temp script not found
  - python3 cant open file
  - MSYS path conversion
  - C c Users in terminal error
  - windows gitbash python path fail
  - search_files returns empty on Windows
  - rg IO error file specified
---

# Windows git-bash MSYS Path Conversion

## Problem

On this host (Windows 10, git-bash/MSYS terminal), native Windows Python 3.14 receives paths through MSYS2 automatic POSIX-to-Windows path conversion. Two failure modes:

1. **Backslash escaping:** `python3 C:\Users\khoans\AppData\Local\Temp\script.py` — bash interprets backslashes as escape sequences, path mangled.
2. **MSYS drive-letter doubling:** `python3 /c/Users/khoans/AppData/Local/Temp/script.py` — MSYS2 converts `/c/` to `C:\c\` (both drive-letter `/c/` and `C:` kept), yielding `C:\\c\\Users\\...`, cant open file.

## Workaround (proven 2026-07-16)

Write the temp script to the CWD (vault/ under Warren_OS_Local) instead of AppData\Local\Temp\:

```
write_file(path=r'C:\Users\khoans\Documents\Warren_OS_Local\vault\hermes-verify-<name>.py',
           content='''...''')

terminal('python3 vault/hermes-verify-<name>.py',
         workdir=r'C:\Users\khoans\Documents\Warren_OS_Local')

terminal('rm vault/hermes-verify-<name>.py',
         workdir=r'C:\Users\khoans\Documents\Warren_OS_Local')
```

Why it works: `vault/` is a POSIX-relative path — bash passes it literally to python3, which resolves it relative to CWD. No drive letter, no backslashes, no MSYS conversion.

## `search_files` returns EMPTY / IO error on Windows MSYS (false-negative, 2026-07-17/18)

The `search_files` tool (ripgrep-backed) SILENTLY returns 0 results or `rg: IO error ... The system cannot find the file specified` on this Windows/MSYS host — EVEN WHEN the target file/folder EXISTS and is readable.

**This is a FALSE NEGATIVE. Do NOT trust "no results = does not exist."**

Observed failure: searching for `SOUL.md` / `STOCK_MEMORY.md` under `C:/Users/khoans` returned 0 results, but `find` via terminal found them immediately at `C:/Users/khoans/Documents/Stock_OS/stock_vault/...`.

### Fix (always verify with terminal)
When `search_files` returns empty and you EXPECT a file to exist:
```bash
terminal('find /c/Users/khoans -iname "SOUL.md" 2>/dev/null | head')
# or
terminal('ls -la "/c/Users/khoans/Documents/Stock_OS/stock_vault/00_CORE_LOGIC/"')
```
The `find`/`ls` route is reliable on this host. Only trust `search_files` when it RETURNS results; treat empty as "unknown", not "absent".

### Pitfall
- Con lost time (and nearly mis-edited the wrong folder) because it trusted `search_files` empty = "file not there". Warren caught it. Always cross-check with `terminal find/ls` before acting on a negative search result.

## Git push to GitHub fails under MSYS (no tty / credential helper can't spawn gh.exe)
`git push` to GitHub HTTPS from this git-bash host fails EVEN when `gh auth status` shows logged-in:
```
error: cannot spawn /mingw64/bin/git-askpass.exe: No such file or directory
bash: line 1: /dev/tty: No such device or address
fatal: could not read Username for 'https://github.com': No such file or directory
```
Root cause: `git config credential.https://github.com.helper` points at `gh auth git-credential`, but MSYS mangles the `C:/Program Files/GitHub CLI/gh.exe` path (space + drive letter) and there is no `/dev/tty`, so the helper can't prompt for the token.

### Fix (ephemeral token-in-URL; do NOT store creds in .git/config)
```bash
cd "<vault_repo>"
TOKEN=$(gh auth token 2>/dev/null)   # 40-char gh token, printed to stdout
git -c "credential.helper=" push "https://x-access-token:${TOKEN}@github.com/<OWNER>/<REPO>.git" <branch>
```
- `<OWNER>/<REPO>` MUST match `git remote -v` exactly. If push says `Repository not found`, verify the real name with `gh repo list` — do NOT guess. (Session 2026-07-20: typo `Warren-Githut` vs real `Warren-Github` cost a round-trip; `gh repo list` showed the truth instantly.)
- `x-access-token:` is the GitHub convention for PAT/gh-token over HTTPS. The token is passed only on the CLI for this one push; nothing is written to `.git/config`.
- `gh auth setup-git` writes the helper into global config but it STILL breaks under MSYS path mangling — the token-URL override is the reliable path.
- The `gh` CLI binary lives at `C:/Program Files/GitHub CLI/gh` (not on PATH as bare `gh` in every shell); `command -v gh` confirms.
- **Verify the repo name before pushing** — a `Repository not found` means the `OWNER/REPO` in the URL is wrong, NOT auth. Run `gh repo list` to get the exact name (session 2026-07-20: typo `Warren-Githut` vs real `Warren-Github` cost a round-trip; `gh repo list` showed the truth instantly). Do NOT guess the owner/spelling.

## File "exists" in `ls`/`find` but UNREADABLE from every tool — Obsidian/MSYS lock (2026-07-26)

SYMPTOM: `ls -li` / `find` thấy file (size bình thường, inode có), NHƯNG `read_file` / `cat` / `python open()` / `git show` / `git checkout-index` ĐỀU fail "No such file or directory". `git ls-files` track file, nhưng `git show HEAD:<path>` báo "does not exist in HEAD" (chưa commit).

ROOT CAUSE: **Obsidian đang mở file → Windows file lock** → MSYS fuse lazy-lookup cache directory listing (nên `ls`/`find` thấy) nhưng `open()` syscall fail. Native Windows Python và git đều fail.

FIX (theo thứ tự):
1. **Đóng Obsidian** (hoặc close pane file đó) → retry `read_file` / `patch`. Đây là cách sạch nhất.
2. Nếu cần patch gấp mà Obsidian lock: **BỐT dán nội dung thủ công** (agent đưa text sẵn, Bố paste vào file). KHÔNG `write_file` mù lên file đang lock → risk corrupt.
3. **Verify readable** bằng `terminal cat <file>` trước khi patch — nếu `cat` cũng fail → file đang lock, dừng.
4. Không dùng `git checkout-index` / `git show` để "recover" — file chưa commit vào HEAD nên không recover được từ git; chỉ restore được nếu đã staged (index) hoặc committed.

Áp dụng: mọi edit vault file `.md` khi Obsidian đang mở cùng file đó.

## Related
- ops-col pitfalls: MSYS path conversion on AppData temp scripts
- ops-col references/verification-script-pattern.md: Recipe section MSYS note
- ops-col Step 0 (Update heartbeat): MSYS caveat note
