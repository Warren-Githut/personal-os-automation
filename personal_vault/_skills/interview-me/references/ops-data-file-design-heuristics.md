# Ops Data File Design Heuristics

> Design principles cho operational data files trong Warren's vault — 60% machine-optimized (Hermes parse) + 40% human-actionable (Warren decisions).
> Được tổng hợp từ session redesign Item Sales Star Horse Tracker (2026-07-06).

## Core Principle: 60/40 Split

Mọi ops data file trong vault phải có 2 lớp rõ ràng:

| Layer | % | Audience | Format | Mục đích |
|-------|---|----------|--------|----------|
| **Machine** | 60% | Hermes | JSON block + grep-able structure | Parse nhanh, 1 lần đọc, 0 token waste |
| **Human** | 40% | Warren | Markdown summary, flags, recommendations | Ra quyết định trong 5 giây |

**Rule of thumb:** Nếu 1 dòng dữ liệu Hermes ko cần parse và Warren ko cần đọc → xoá nó.

## 9 Reusable Heuristics

### H1: Embedded JSON Block
```markdown
### 📦 JSON
```json
{
  "week": "W27",
  "metric": "value"
}
````
- JSON block nằm TRONG file markdown, ko phải file riêng
- Hermes grep 1 phát: `grep -A 50 '### 📦 JSON' file.md`
- Warren skip JSON, đọc markdown bên trên
- **Token saving:** ~40% vs format markdown thuần

### H2: Top 80% Groups
- Chỉ giữ groups chiếm top 80% volume (~8-10 groups)
- Skip groups <1% volume
- **Token saving:** ~40% vs full group list (thường 20-25 groups)
- **Business justification:** FBM chỉ care top sellers; bottom 20 groups = noise

### H3: Store-Level + System-Level Item Tracking
- **Mỗi store:** top 10 food + top 10 bev (~20 items/store × 3 stores = 60 items)
- **System:** top 10 food + top 10 bev (tổng hợp)
- **Fallback:** Hermes tra accumulation JSON nếu cần item cụ thể ngoài top 10

### H4: Accumulation JSON as Hermes Fallback
```
_accumulation/{domain}.json
```
- Chứa ALL items ALL weeks — Hermes query khi cần deep-dive
- Parser append mỗi tuần
- File markdown chỉ chứa summary + top items
- **Pattern:** `weekly report = summary` + `accumulation = full history`

### H5: Dashboard Auto-Rebuild After Parser
```
Parser chạy (cron)
  ├── Ghi markdown format
  └── Update accumulation JSON
Script dashboard builder (cron +5 phút)
  └── Read accumulation JSON + rebuild self-contained HTML
```
- HTML self-contained (data embedded, Chart.js CDN) — ko cần server
- File:// open là chạy
- Link absolute ghi vào weekly report: `file:///C:/path/to/dashboard.html`

### H6: Scorecard Format (1-Line Per Store)
```
| Store | Qty | Rev | Price | ΔQty | ΔRev | ΔPrice | Top Group |
```
- 1 dòng/store + 1 dòng System = 4 dòng total
- Thay thế 3 blocks riêng biệt mỗi store (~60 dòng)
- **Token saving:** ~90% vs per-store block format

### H7: Executive Summary 3-Bullet
```
### 🎯 Executive Summary
- **System**: [qty] items | [rev]M rev (±X% vs W-N)
- **🔴 Flag**: [vấn đề cần xử lý ngay]
- **✅ Star**: [item] — [qty] qty | [rev] rev
- **💡 RECOMMEND**: [hành động cụ thể, 1 câu]
```
- FBM needs 5 giây: "what changed, what's wrong, what to do"
- Bullet 1 = system health
- Bullet 2 = critical exception
- Bullet 3 = top performer
- Bullet 4 = actionable recommendation

### H8: Flags Section — Exceptions Only
```
### 🔴🔵 Flags & Actions
- 🔴 Price below target: [items, giá thực tế, target]
- ✅ BCG Stars: [items]
- 📊 BCG Summary: Food Star X, PH Y, Dog Z, ? W | Drink...
- ℹ️ Cost=0 items: [list]
```
- KHÔNG đưa data bình thường vào flags section
- Chỉ exceptions: price alerts, cost=0, new items, disappearing items
- **Token saving:** ~60% vs full item list

### H9: BCG Quadrant Summary (Compressed)
```
- 📊 BCG Food: Star 21, PH 16, Dog 21, ? 16 | Drink: Star 16, PH 19, Dog 15, ? 19
```
- 1 dòng thay vì 8 dòng (2 blocks × 4 lines)
- Hermes parse counts cho trend, Warren thấy cân bằng portfolio
- **Token saving:** ~87% vs expanded format

## When to Apply

Apply these heuristics khi redesign hoặc tạo mới:

| File Type | Apply H# | Notes |
|-----------|----------|-------|
| Item Sales Log | H1-H9 | Full stack |
| GrabFood Weekly Log | H1, H5, H6, H7, H8 | Channel mix focus |
| Revenue Log | H1, H6, H7 | Store comparison primary |
| COL Weekly Log | H1, H6, H7, H8 | Labor cost flags |
| COGS Monthly Log | H1, H8 | Exception-driven |
| LTO Weekly Log | H1, H2, H7, H8 | LTO performance |

## Token Budget Reference

| Heuristic Applied | Token Saving (est) |
|-------------------|-------------------|
| No heuristics (full markdown) | 0% (baseline) |
| Embedded JSON only | ~20% |
| + Top 80% groups | ~40% |
| + Scorecard format | ~55% |
| + Flags only exceptions | ~65% |
| + BCG compressed | ~70% |
| Full stack (H1-H9) | ~50-60% |

> Target range: 50-60% token reduction vs legacy format while INCREASING decision speed for Warren.
