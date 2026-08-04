---
name: hermes-session-backup
type: skill
version: 1.0.0
description: >
  Export, backup, and audit Hermes Agent conversation sessions. Use when Warren
  wants to archive sessions, audit cron-job runs, build a session-backup cron,
  or push sessions to HuggingFace. Covers `hermes sessions export` flags, the
  Windows path quirk, the --redact limitation (Teknium-confirmed), session-volume
  reality, rotation, gitignore, and the E2E-verify gate for the cron.
triggers:
  - "backup hermes sessions"
  - "export sessions"
  - "archive conversations"
  - "audit cron jobs"
  - "push sessions to huggingface"
  - session export / session backup / hermes sessions export
---

# Hermes Session Backup & Export

Hermes auto-saves every conversation (CLI, Telegram, cron, etc.) to a SQLite DB
(`~/.hermes/state.db`). The `hermes sessions export` command turns that into
portable formats. This skill is for Warren's **audit + local backup** use case,
NOT for replacing WARREN_MEMORY.md / mem0 (session history ≠ structured memory).

## When to use
- Warren wants to archive/backup Hermes sessions (insurance against DB loss).
- Warren wants to audit what a cron job actually did (`--source cron`).
- Warren asks about exporting to HuggingFace or fine-tuning a personal model.
  → Recommend LOCAL-ONLY unless he explicitly wants HF; see redact pitfall.

## Prereqs — version matters
New export flags (`--redact`, `--format`, `--newer-than`, `--upload`) require a
recent Hermes. Check first:
```
hermes --version          # needs >= v0.18.2 for full flag set
hermes sessions export --help
```
If flags are missing → `hermes update --check` then `hermes update --yes`
(this is a Zone-🔴-ish core change — confirm with Warren before updating).

## The export command
```
hermes sessions export <output> [flags]
```
| Flag | Effect |
|---|---|
| `--format {jsonl,md,qmd,html,trace}` | jsonl=default (1 JSON obj/line); html=self-contained page; trace=Claude-Code JSONL for HF Agent Trace Viewer |
| `--source cron\|telegram\|cli\|...` | filter by platform — USE THIS for cron audit |
| `--older-than 7d` / `--newer-than 1d` | duration (`5h`/`2d`/`1w`) or ISO timestamp |
| `--redact` | scrub API keys/tokens/credentials (see pitfall) |
| `--model` / `--min-tokens` / `--title` | more filters |
| `--dry-run` | **requires ≥1 filter**; lists matches, writes nothing |
| `--upload` (trace only) | push to private HF `hermes-traces` dataset (needs `HF_TOKEN`) |

## CRITICAL pitfalls
### 1. Windows path quirk (cost me a failed run)
The `hermes` binary runs on **native Windows Python** (`venv/Scripts/hermes.exe`),
even when you invoke it from bash/git-bash. MSYS paths like `/c/Users/...` FAIL:
```
FileNotFoundError: [Errno 2] No such file or directory: '/c/Users/khoans/...'
```
✅ ALWAYS pass **Windows-native paths**: `C:/Users/khoans/...` (forward slashes OK)
or `C:\Users\khoans\...`. Same for the `--output` argument and any `--cwd`.

### 2. `--redact` is API-key-ONLY (Teknium-confirmed)
Teknium (Hermes creator), follow-up to the export announcement:
> "auto-redaction is only good on api key-like text - it will not redact
> plaintext regular passwords, email addresses, addresses, phone numbers, etc
> - so before making anything public be sure to only share what you know is clean."

For Warren's instance this means `--redact` leaves intact:
- email `nguyen.s.khoa@gmail.com`
- vault path `C:/Users/khoans/Documents/Warren_OS_Local/...`
- Google token path `%LOCALAPPDATA%/.../google_token.json`

→ **LOCAL-ONLY by design. NEVER upload to HF/public without a manual grep-then-strip
pass for email/phone/path.** State this in every backup report.

### 3. Session volume is huge — filter or explode
Measured on Warren's machine (2026-07-08):
- Full export (all sources): **4349 sessions / ~559 MB**
- `--source cron --newer-than 1d`: 410 sessions / ~41 MB
- `--source cron --older-than 7d`: 1776 sessions / ~177 MB

→ Always scope with `--source` + a time window. Never blind `export backup.jsonl`
(full DB) on a cron. Add **rotation** (delete >N days) or disk inflates forever.
→ Add the output dir to `.gitignore` (large JSONL must never commit).

### 4. Warren-specific constraints (from WARREN_MEMORY.md)
- **SSOT:** session export is a *log/archive*, NOT a source of truth. Don't let it
  become a 4th memory layer alongside WARREN_MEMORY.md + mem0 + vault.
- **Verify, never trust:** after any export/cron, verify the file on disk (size,
  JSONL validity, redact behavior) before claiming success.
- **Non-IT reports:** when summarizing for Warren, explain in plain Vietnamese,
  conclusion-first, no jargon.

## E2E verify gate (Warren's rule: test before approving any cron)
1. Write the backup script (see `scripts/backup_sessions.py`).
2. Run it manually once → confirm file on disk + size + JSONL parses.
3. `git check-ignore <backup-file>` → confirm .gitignore blocks it.
4. Create cron (`deliver=all` → Telegram, "never silent").
5. `cronjob action=run` → confirm `last_delivery_error: null` AND Warren confirms Telegram message arrived. (Verified live 2026-07-08: job ran, delivered, Warren confirmed receipt.)
6. Only then call it verified.

## Live cron pattern (deployed 2026-07-08)
- Name: `session-backup-weekly` (job_id `a423cfe9598b`)
- Schedule: `0 20 * * 0` (Sun 20:00 — after `audit-automation --all` at 19:00, no overlap)
- `enabled_toolssets: ["terminal","file"]`, `no_agent: false`, `deliver: "all"`
- Prompt: run `python3 <script>`, report stdout (one-line OK/FAIL) to Telegram.
- Script params that worked: `--source cron --older-than 7d --redact`, rotation 28d, OUT_DIR `vault/_archives/sessions/`.
- Result: 1776 sessions / 176.7 MB / run. After 28d rotation ≈ 700 MB local bound.
- ⚠️ If volume too heavy later → narrow `--source` or add a `--min-status` filter.

## Reference
- `references/teknium-session-export.md` — condensed research (tweet, docs, redact quote, volume numbers).
- `scripts/backup_sessions.py` — known-good cron backup script (cron-source, >7d, redact, 28d rotation). Live deployed at `C:/Users/khoans/AppData/Local/hermes/profiles/warren-profile/scripts/backup_sessions.py`.
