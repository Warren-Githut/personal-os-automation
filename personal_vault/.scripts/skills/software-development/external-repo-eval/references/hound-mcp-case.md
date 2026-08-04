# Hound (master-fetch) — MCP Server Install Worked Example

> **Date:** 2026-07-21
> **Repo:** `dondai1234/master-fetch` (Hound, PyPI `hound-mcp`)
> **Pattern:** MCP Server → Install + `hermes mcp add`

## Kết quả eval

| Dimension | Verdict |
|-----------|---------|
| Runtime lock? | ❌ None — pure Python MCP server, MIT, Hermes-native |
| Cài được? | ✅ `pip install hound-mcp[all]` |
| Steps | pip → playwright install chromium → `hermes mcp add hound --command hound` |
| Tools | 6: mcp_smart_fetch, mcp_smart_search, mcp_smart_crawl, mcp_screenshot, cache_clear, version |
| Verify | `hound --doctor` (all healthy), `hermes mcp test hound` (connected, 6 tools), `hound -v` (10.4.1) |

## Key lessons

1. **MCP server ≠ runtime lock.** Dù README mention Hermes + Claude Code + OpenCode + Pi + Cursor, MCP protocol là chuẩn mở → Hermes `hermes mcp add` là được. Không cần wrapper skill.
2. **Binary dependency:** playwright install chromium (~300MB) không optional — cần cho anti-bot browser. Đừng bỏ qua.
3. **`hound --doctor`** là health check tốt nhất trước khi add vào Hermes.
4. **Session mới cần thiết:** MCP tools chỉ available sau `/reload-mcp` hoặc session mới.
5. **using-agent-skills constitution:** Dù là cài tool, Bố vẫn muốn chạy đúng quy trình speckit-constitution trước. Không tự ý skip.

## Commands

```bash
pip install hound-mcp[all]
playwright install chromium
hound --doctor                    # verify health
hound -v                          # version
hermes mcp add hound --command hound   # add to Hermes
hermes mcp test hound             # verify connection
hermes mcp list                   # list MCP servers
# Sau đó: /reload-mcp hoặc session mới
```
