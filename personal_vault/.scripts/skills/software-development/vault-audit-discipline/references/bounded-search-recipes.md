# Bounded Search Recipes (Warren home tree, <60s)

The home tree `C:\Users\khoans` is too large for unbounded `find` (node_modules,
AppData depth -> 60s timeout). Use these BOUNDED recipes instead.

## Recipe 1 — Find a script by name (bounded)
```bash
cd /c/Users/khoans/AppData/Local/hermes/profiles/warren-profile/scripts
find . -name "telegram_bot.py" 2>/dev/null
```
Or vault scripts:
```bash
cd /c/Users/khoans/Documents/Warren_OS_Local/vault
find .scripts -name "*.py" 2>/dev/null | grep -i "review"
```

## Recipe 2 — Grep for a symbol in a bounded dir (fast, ripgrep-backed)
Use the `search_files` tool with explicit `path` + `file_glob`:
- pattern: `review_response_handler|_append_to_gsheet`
- path: `C:/Users/khoans/AppData/Local/hermes/profiles/warren-profile/scripts`
- file_glob: `*.py`

Or terminal:
```bash
cd /c/Users/khoans/AppData/Local/hermes/profiles/warren-profile/scripts
grep -rl "review_response_handler" . 2>/dev/null
```

## Recipe 3 — Find an approved build plan before building
```bash
cd /c/Users/khoans/AppData/Local/hermes/profiles/warren-profile/skills
grep -rln "Build X Plan\|APPROVED by Warren" ops/ 2>/dev/null
# then read the matching references/*-build-*.md
```

## Recipe 4 — Locate a cron script referenced by a job
Cron `script` field is relative to `~/.hermes/scripts/`. Check both:
```bash
ls ~/.hermes/scripts/            # global scripts dir (cron script field resolves here)
ls profiles/warren-profile/scripts/   # profile scripts dir
```

## Anti-recipe (NEVER do this)
```bash
find /c/Users/khoans -name "*.py"          # -> 60s timeout, inconclusive
search_files(path='/', pattern='x')        # -> IO error / timeout
```
A timeout/IO-error from these is NOT "file not found". Re-scope to a bounded dir.
