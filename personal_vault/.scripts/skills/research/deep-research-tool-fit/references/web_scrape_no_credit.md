# Web Scrape When Firecrawl Credit Exhausted (Cách B)

## Context (2026-07-17)
Hermes chỉ có 1 cổng scrape (Firecrawl) cho `web_extract` / `web_search` / `x_search`.
Khi hết credit → MỌI URL fail: `"Payment Required: Failed to scrape. Insufficient credits"`.
Mirror (vxtwitter/xcancel) và Wayback cũng fail (cùng proxy).

## What still works (no Firecrawl)
| Target | Method | Confidence |
|--------|--------|------------|
| GitHub repo README | `curl -sL "https://raw.githubusercontent.com/<owner>/<repo>/<branch>/README.md"` | [HIGH] |
| GitHub repo page HTML | `curl -sL "https://github.com/<owner>/<repo>"` | [HIGH] |
| GitHub API (public) | `curl -sL "https://api.github.com/repos/<owner>/<repo>"` | [HIGH] |
| GitHub API user repos | `curl -sL "https://api.github.com/users/<owner>/repos?per_page=100"` | [HIGH] |
| Docs site (python.org, etc.) | `curl -sL "<url>"` | [HIGH] |
| **X/Tweet** | curl KHÔNG vào được (auth wall) → nhờ Warren paste text / screenshot | BLOCKED |

## Commands (copy-paste)
```bash
# 1. Verify network egress
curl -sL --max-time 20 "https://docs.python.org/3/library/sqlite3.html" -o /tmp/t.html -w "HTTP %{http_code} size=%{size_download}\n"

# 2. GitHub README (try main, then master)
for b in main master; do
  curl -sL --max-time 20 "https://raw.githubusercontent.com/OWNER/REPO/$b/README.md" -o /tmp/readme.md -w "branch=$b HTTP %{http_code} size=%{size_download}\n"
  if [ -s /tmp/readme.md ] && ! grep -q "404: Not Found" /tmp/readme.md; then break; fi
done

# 3. Copy MSYS /tmp → workspace (read_file can't see /tmp)
python3 -c "import shutil; shutil.copy('/tmp/readme.md', r'C:/Users/khoans/Documents/Warren_OS_Local/_tmp_readme.md')"
# ... read_file the workspace copy, then: rm -f <workspace copy>
```

## MSYS /tmp quirk
- `curl` writes to `/tmp/x.html` but `read_file` returns "File not found" (MSYS temp map differs from Win path).
- FIX: copy to `C:/Users/khoans/Documents/Warren_OS_Local/` via python shutil, read, then delete.

## X/Tweet fallback (Warren-side)
- Warren paste tweet text into chat → read directly [HIGH].
- Or Warren sends screenshot PNG → `liteparse parse` (OCR) → read [MOD].
- NEVER fabricate tweet content when blocked.

## Decision tree
```
web_extract fails "Payment Required"?
  ├─ URL is GitHub / docs → curl fallback (above) ✅
  ├─ URL is X/Tweet → ask Warren paste/screenshot 🔴 blocked
  └─ URL is other → try curl; if 403/401 → report + ask Warren
```
