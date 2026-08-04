# Web Scrape Khi Hết Credit Firecrawl/xAI

## Tình huống
Khi `web_extract` / `web_search` / `x_search` trả lỗi `Payment Required: Insufficient credits` (Firecrawl hoặc xAI hết credit), MỌI URL đều fail — kể cả mirror (vxtwitter, xcancel, wayback) vì cùng 1 proxy.

## Cách B — đọc trực tiếp bằng curl (WORKS)
Dùng `terminal` chạy curl/python3, KHÔNG qua Firecrawl:

```bash
# GitHub raw file
curl -sL --max-time 25 "https://raw.githubusercontent.com/<user>/<repo>/<branch>/<path>" -o /tmp/file.md

# GitHub repo page / API (public)
curl -sL --max-time 25 "https://github.com/<user>/<repo>" -o /tmp/repo.html
curl -sL --max-time 25 "https://api.github.com/users/<user>/<repo>" -o /tmp/repos.json

# Docs site (python.org, etc.) — HTTP 200 OK
curl -sL --max-time 25 "https://docs.python.org/3/library/sqlite3.html" -o /tmp/doc.html
```

Sau đó `python3 -c "import shutil; shutil.copy('/tmp/file.md', r'C:/Users/khoans/Documents/Warren_OS_Local/_tmp_x.md')"` rồi `read_file` (MSYS /tmp map khác, copy sang workspace mới read được).

## Hạn chế
- **Tweet X / bất kỳ trang cần auth**: vẫn kẹt. Bố phải paste text hoặc gửi screenshot → con liteparse.
- Không auto-detect login wall — curl trả HTML login page thay content thì phải nhận biết thủ công.

## Đã verify (2026-07-17)
- Đọc được `coreyhaines31/marketingskills` README + `marketing-loops/SKILL.md` qua curl raw.
- GitHub API public repos list: OK. Docs site: OK.

## Quy tắc
Bố hỏi "đọc được web X không?" → thử cách B trước. Chỉ báo "không được" khi curl cũng fail (hiếm).
