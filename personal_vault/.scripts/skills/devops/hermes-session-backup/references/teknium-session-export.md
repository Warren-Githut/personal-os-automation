# Teknium Session Export — Condensed Research

Source date: 2026-07-07/08. Authoritative: hermes-agent.nousresearch.com/docs/user-guide/sessions#export-sessions

## Tweet (Teknium @Teknium, 2026-07-07)
"Hermes Agent can now export your agent sessions, or sets of sessions, into a
variety of formats and places. Get full conversations out in HTML, Markdown,
JSON and more, or upload entire datasets of your sessions to private
@huggingface repos with ease. You also get all the filters ... by model, date
ranges, conversation source (i.e. cronjob or telegram) ... `hermes update` and
you'll have full control over your data to export, inspect, share, and store."

## REDACT LIMITATION (Teknium follow-up, 50m later — VERBATIM)
"auto-redaction is only good on api key-like text - it will not redact
plaintext regular passwords, email addresses, addresses, phone numbers, etc -
so before making anything public be sure to only share what you know is clean."

→ For Warren: `--redact` leaves email / vault-path / token-path intact.
  LOCAL-ONLY unless a manual grep-strip pass is added before upload.

## Formats (docs)
| Format | Output | Use |
|---|---|---|
| jsonl (default) | 1 JSON obj/session | backups, machine round-trip |
| md / qmd | 1 file/session + manifest | readable archives |
| html | self-contained page | sharing, browsing |
| trace | Claude Code JSONL → HF Agent Trace Viewer | `--upload` to private `hermes-traces` |

## Key filters
`--source` (cron/telegram/cli/...), `--older-than`/`--newer-than` (5h/2d/1w/ISO),
`--model`, `--min-tokens`, `--title`, `--redact`, `--dry-run` (needs ≥1 filter),
`--upload` (trace only, needs HF_TOKEN; `--public` for public dataset).

## Warren's measured volume (2026-07-08, v0.18.2)
- Full DB: 4349 sessions / ~559 MB
- `--source cron --newer-than 1d`: 410 sessions / ~41 MB
- `--source cron --older-than 7d`: 1776 sessions / ~177 MB
- Rotation needed: 4 weekly backups ≈ 700 MB local.

## Windows path quirk
hermes binary = native Windows Python. MSYS `/c/Users/...` → FileNotFoundError.
Use `C:/Users/khoans/...`.
