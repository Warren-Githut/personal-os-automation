# Cron HOME-path pitfall (Windows) — reproduction + fix

## Symptom (what the cron output shows)

```
[WARN] GSheet read failed: [Errno 2] No such file or directory: '~\AppData\Local\hermes\google_token.json'
[WARN] Google Calendar read failed: [Errno 2] No such file or directory: '~\AppData\Local\hermes\google_token.json'
```
or
```
FileNotFoundError: [Errno 2] No such file or directory: '~\Documents\Warren_OS_Local\vault\00_CORE_LOGIC\TODAY.md'
```
or a no_agent script that exits 0 but produces an empty/silent result (e.g. `OPEN CASES — Không có case active` when the index clearly has active cases).

## Root cause

In the Hermes **cron** environment, the `HOME` environment variable is **not set**. So:

```python
home = os.environ.get("HOME", "~")   # → "~"  (literal tilde string)
path = Path(home) / "AppData/Local/..."   # → "~AppData\Local\..."  (nonexistent)
```

On **Windows**, `Path("~")` does **NOT** expand the tilde to the user profile (unlike POSIX shells). `Path.home()` is what actually resolves the profile dir on Windows — and it reads `USERPROFILE` / `LOCALAPPDATA`, which ARE present in the cron environment.

So any vault script that resolves paths via `os.environ.get("HOME", "~")` works fine when run from an interactive terminal (where `HOME` is set to `/c/Users/khoans` by the shell) but **fails silently in cron** — exactly the "works on my machine, dies in cron" class.

## Affected patterns (grep for these)

```
os.environ.get("HOME"
Path(...) / "Documents/Warren_OS_Local"
Path(...) / "AppData/Local/hermes
```

Seen 2026-07-08: `gen_today.py` (VAULT + token path), `cases_parser.py` (VAULT + token path). All fixed by switching to `Path.home()`.

## Fix

Replace every `Path(os.environ.get("HOME", "~")) / "..."` with `Path.home() / "..."`.

```python
# BEFORE
VAULT = Path(os.environ.get("HOME", "~")) / "Documents/Warren_OS_Local/vault"
token_path = Path(os.environ.get("HOME", "~")) / "AppData/Local/hermes/profiles/warren-profile/google_token.json"

# AFTER
VAULT = Path.home() / "Documents/Warren_OS_Local/vault"
token_path = Path.home() / "AppData/Local/hermes/profiles/warren-profile/google_token.json"
```

`Path.home()` is correct on Windows in every context (interactive and cron). Prefer it unconditionally for Warren's vault scripts.

## Verification — reproduce the cron environment

Strip `HOME` and run the script exactly as cron would:

```bash
cd /c/Users/khoans/Documents/Warren_OS_Local
env -u HOME python3 vault/scripts/<script>.py
```

- If the script uses `Path.home()` → runs correctly (exit 0, real output).
- If it still uses `os.environ.get("HOME","~")` → fails with the `~AppData` / `~Documents` path error, reproducing the cron bug locally.

Use this as the **standard pre-commit verification** for any `no_agent` vault cron script. Pair with the ad-hoc temp-script pattern (`write_file` a `hermes-verify-*.py` to `%TEMP%`, run, `rm`) since `execute_code` and `python3 -c` are blocked in cron mode.

## Silent-failure variant (case index)

If `CASES_INDEX = VAULT / "_cases/00_CASES_INDEX.md"` resolves to `~Documents/...` (nonexistent), `get_active_cases_metadata()` returns `[]` → `format_open_cases_section` prints "✅ Không có case active." even though the real index has 6 active cases. Same `Path.home()` fix resolves it. Verify with:

```bash
env -u HOME python3 -c "import sys; sys.path.insert(0,'vault/scripts'); import cases_parser as cp; o,d,t=cp.get_all_active_cases_with_tasks(); print(len(o)+len(d)+len(t))"
# expect 6 (not 0) once Path.home() is applied
```
