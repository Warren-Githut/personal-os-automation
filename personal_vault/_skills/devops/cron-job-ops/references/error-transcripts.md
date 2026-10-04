# error-transcripts.md — Raw cron error messages (warren-profile, 2026-07-18)

Captured during the fix of 4 broken no_agent crons (gen-today-daily, review-telegram-sender, fill-promo-tracking, git-auto-backup) + col-queue-watcher-v2 credential error. Use these to diagnose fast.

---

## 1. Script not found (resolver joins into profile/scripts/)

**gen-today-daily** (script field was bare `gen_today_and_send.py`, but file was in vault/.scripts/, not profile/scripts/):

```
Script not found: C:\Users\khoans\AppData\Local\hermes\profiles\warren-profile\scripts\gen_today_and_send.py
```

**review-telegram-sender** (same class — file missing from profile/scripts/):

```
Script not found: C:\Users\khoans\AppData\Local\hermes\profiles\warren-profile\scripts\review_telegram_sender.py
```

Root cause: after 2026-07-15/16 restructure (vault scripts moved to vault/.scripts/), the profile/scripts/ dir was EMPTY. Cron resolver only looks in profile/scripts/, so every no_agent cron died.

---

## 2. Blocked: path outside scripts dir

When we first tried absolute path into vault:

```
Blocked: script path resolves outside the scripts directory (C:\Users\khoans\AppData\Local\hermes\profiles\warren-profile\scripts): 'C:/Users/khoans/Documents/Warren_OS_Local/vault/.scripts/gen_today_and_send.py'
```

When we tried `skills/...` prefix:

```
Script not found: C:\Users\khoans\AppData\Local\hermes\profiles\warren-profile\scripts\skills\ops-daily-brief\.scripts\gen_today_and_send.py
```

-> Confirms: resolver ALWAYS prepends `profile/scripts/` to whatever is in `script` field. Bare name is the only correct form.

---

## 3. gitignore blocks jobs.json

```
The following paths are ignored by one of your .gitignore files:
cron
hint: Use -f if you really want to add them.
```

-> `cron/` is gitignored in profile root. Must `git add -f cron/jobs.json`.

---

## 4. Windows no bash — .sh fails

git-auto-backup source was `.sh` (skills/.git_auto_backup.sh), jobs.json khai `git_auto_backup.py` (wrong name, file missing). After copying .sh as git_auto_backup.sh and running:

```
Script exited with code 1
stderr:
<3>WSL (9 - Relay) ERROR: CreateProcessCommon:818: execvpe(/bin/bash) failed: No such file or directory
```

After converting to .py but using `date` command:

```
File "...\scripts\git_auto_backup.py", line 29, in main
    today = subprocess.run(["date", "+%Y-%m-%d"], ...)
FileNotFoundError: [WinError 2] The system cannot find the file specified
```

Fix: use `datetime.date.today().isoformat()` instead of `date`.

---

## 5. HTTP 402 — out of credits (agent cron)

Stock Broker Fetch (model default Flash, OpenRouter credit exhausted):

```
RuntimeError: HTTP 402: This request requires more credits, or fewer max_tokens. You requested up to 65536 tokens, but can only afford 4047. To increase, visit https://openrouter.ai/workspaces/default/keys/...
```

-> This is a MONEY error, not a code error. Distinct from credential errors below.

---

## 6. No usable credentials — wrong provider name / commented key

col-queue-watcher-v2 (jobs.json: provider=opencode, model=deepseek-v4-flash):

```
RuntimeError: No usable credentials found for provider 'opencode-zen'. Set OPENCODE_ZEN_API_KEY.
```

Root cause: config.yaml has NO `opencode` provider. Correct name is `opencode-go` (seen in stock-profile config: `provider: opencode-go`, base_url `https://opencode.ai/zen/go/v1`). Also `.env` had `# OPENCODE_ZEN_API_KEY=...` COMMENTED OUT -> key not loaded.

-> Diagnosis: "No usable credentials" = name mismatch OR key commented. Check `config.yaml` providers block + `.env` active lines.

---

## 7. Provider drift auto-block

```
RuntimeError: Skipped to prevent unintended spend: global inference config drifted since this job was created (provider 'custom' -> 'kilocode'; model 'deepseek-v4-flash' -> 'tencent/hy3:free'), and this job is unpinned. ... pin it explicitly: cronjob action=update job_id=... provider=<p> model=<m>
```

-> Hermes self-blocks unpinned jobs when global model/provider changes. Re-pin via cronjob update.
