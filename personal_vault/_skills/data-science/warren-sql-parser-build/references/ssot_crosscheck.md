# Independent SSOT Cross-Check (A9 + 2% threshold)

> Dùng trong mọi Warren vault parser cần cross-check vs `01_SSOT_01_Weekly_Revenue_Log.md`
> (hoặc SSOT khác). Source: `hourly_cover_sql_parser.py` v6.0 (2026-07-26).

## Rule
- Cross-check PHẢI độc lập (ANCHORS A9): parse SSOT từ text riêng, KHÔNG dùng output của parser.
- Threshold hourly = **2%** (handoff D6). Weekly pipeline internal verify giữ 0.3%/0.5%.
- Phân biệt 2 trạng thái:
  - **DATA GAP**: SSOT CHƯA CÓ section tuần đó → báo "thiếu", KHÔNG báo 🔴 mismatch.
  - **MISMATCH 🔴**: SSOT CÓ nhưng lệch >2% → báo 🔴, yêu cầu check query/SSOT trước ghi.

## SSOT section format (đích)
```
## 2026-W30 | 2026-07-20 → 2026-07-26   [84% calendar] 🟢

### Full Week
|  | ALL | LU3 | LU5 | LU7 |
|--|-----|-----|-----|-----|
| Net Revenue | 684,550,556 | 243,010,500 | 197,834,856 | 243,705,200 |
| Covers | 2,583 | 926 | 735 | 922 |
```

## Code (copy + adapt)
```python
CROSS_THRESHOLD_PCT = 2.0

def parse_ssot_week(ssot_text, ws, we):
    start_s, end_s = ws.strftime("%Y-%m-%d"), we.strftime("%Y-%m-%d")
    m = re.search(rf"^##\s+\S+\s*\|\s*{re.escape(start_s)}\s*→\s*{re.escape(end_s)}\b.*?(?=^## |\Z)",
                  ssot_text, re.MULTILINE | re.DOTALL)
    if not m:
        return None                      # → DATA GAP
    blk = m.group(0)
    fw = re.search(r"### Full Week\s*(.*?)(?=\n### |\Z)", blk, re.DOTALL)
    table = fw.group(1) if fw else blk
    cov = net = None
    for line in table.splitlines():
        if not line.strip().startswith("|"):
            continue
        cells = [c.strip().replace(",", "").replace(".", "").replace(" ", "")
                 for c in line.strip().strip("|").split("|")]
        if len(cells) < 2:
            continue
        # EXACT label match — tránh 'Covers W/W%' false match
        if cells[0] == "NetRevenue" and net is None:
            net = int(re.sub(r"\D", "", cells[1])) or None
        elif cells[0] == "Covers" and cov is None:
            cov = int(re.sub(r"\D", "", cells[1])) or None
    return {"covers": cov, "net": net} if cov and net else None

def cross_check_ssot(ws, we, sys_ac, sys_net, ssot_text=None):
    lines = ["### 🔍 Cross-check vs 01_SSOT_01_Weekly_Revenue_Log", ""]
    if ssot_text is None:
        ssot_text = REVENUE_LOG_FILE.read_text(encoding="utf-8")
    res = parse_ssot_week(ssot_text, ws, we)
    wid = make_week_id(ws)
    if res is None:
        lines.append(f"> ⚠️ **DATA GAP:** SSOT chưa có tuần {wid} ...")  # không 🔴
        return lines
    rcc, rrn = res["covers"], res["net"]
    pc = abs(sys_ac - rcc) / rcc * 100
    pn = abs(sys_net - rrn) / rrn * 100
    flg_c = "🔴" if pc > CROSS_THRESHOLD_PCT else "🟢"
    flg_n = "🔴" if pn > CROSS_THRESHOLD_PCT else "🟢"
    lines.append(f"> Covers: Hourly={sys_ac:,} vs SSOT={rcc:,} ({pc:.1f}%) — {flg_c}")
    lines.append(f"> Net Rev: Hourly={int(sys_net):,} vs SSOT={int(rrn):,} ({pn:.1f}%) — {flg_n}")
    return lines
```

## Verify (A6)
E2E W29 thực tế (2026-07-26): Hourly SQL covers=2,590 vs SSOT=2,583 (+0.3%) 🟢 ·
Net=683,671,620 vs 684,550,556 (+0.1%) 🟢. RESULT: PASS (independent parse, no circular).
