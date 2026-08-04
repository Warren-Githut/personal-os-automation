# GSheet: 09_Hourly_Cover_Revenue_Log — Column Layout

> File này mô tả column layout của tab `09_Hourly_Cover_Revenue_Log` trong GSheet `LU_COL_ENGINE_V4` (sheet_id: `1ZtIocc_Ic1z-tO1JGd4ZLnRB_7ZHHkvpJ5emaWJyeEE`, gid: `1841157748`).
>
> Layout này **không uniform** do merged cells trong GSheet header.

## Column Mapping (0-indexed)

| Day | Guests col | Revenue col | Notes |
|-----|:----------:|:-----------:|-------|
| Mon | 3 | 5 | Col 4 = empty (merged cell artifact) |
| Tue | 6 | 7 | **Không có empty col giữa guests và rev** |
| Wed | 8 | 10 | Col 9 = empty |
| Thu | 11 | 12 | **Không có empty col** |
| Fri | 13 | 14 | **Không có empty col** |
| Sat | 15 | 16 | **Không có empty col** |
| Sun | 17 | 18 | **Không có empty col** |
| Week total | 19 | 20 | Guests + Revenue |

**KHÔNG dùng** công thức `guests = 3 + day_idx * 3` — sai vì Tue/Thu/Fri/Sat chỉ có 2 columns (guests + rev, ko có empty).

## Row Types

| Row | Type | hour_str | Khi nào có |
|-----|------|----------|------------|
| `["LU3-LTT-Q1", "7", "Dine in", ...]` | Order type | `"7"`, `"8"`... | Mỗi order type (Dine in, GrabFood, Split Order, Take away) |
| `["LU3-LTT-Q1", "08 Total", ...]` | Hour total | `"08 Total"`, `"09 Total"`... | **Nên parse row này** — đã aggregated sẵn |
| `["LU3-LTT-Q1 Total", "", ...]` | Store total | `""` | Tổng store cho cả tuần. Cột 19 = guests, 20 = rev |
| `["Grand Total", "", ...]` | System total | `""` | Dòng cuối cùng |

## Parsing Rules

1. **Parse "XX Total" rows** (regex: `r'^(\d+)\s*Total$'`) — đã aggregated sẵn, tránh double-count
2. **Ngoại lệ hour 7** (LU3): ko có "07 Total" row → sum từ order-type rows
3. **actual_covers = gross_covers - split_orders**: Tổng từ "XX Total" rows là **gross** (cả Split Orders). Để có actual, phải subtract các Split Order rows
4. **Store total row**: Dòng "LU3-LTT-Q1 Total" là source of truth cho store totals

## Python Parsing Example

```python
D = {'mon':(3,5),'tue':(6,7),'wed':(8,10),'thu':(11,12),'fri':(13,14),'sat':(15,16),'sun':(17,18)}
DAYS = ['mon','tue','wed','thu','fri','sat','sun']

def parse_hourly_total_rows(rows, store_start, store_end):
    """Parse all 'XX Total' rows for one store"""
    hourly = {}
    for i in range(store_start, store_end + 1):
        row = rows[i]
        hour_str = str(row[1]) if len(row) > 1 else ''
        m = re.match(r'^(\d+)\s*Total$', hour_str)
        if m:
            hr = int(m.group(1))
            day_data = {}
            for di, day in enumerate(DAYS):
                gc, rc = D[day]
                g = clean_num(row[gc]) if gc < len(row) else 0
                rv = clean_num(row[rc]) if rc < len(row) else 0
                day_data[day] = (g, rv)
            hourly[hr] = day_data
    return hourly

def compute_actual_covers(rows, store_start, store_end, gross_covers):
    """Subtract split orders from gross to get actual covers"""
    split_total = 0
    for i in range(store_start, store_end + 1):
        row = rows[i]
        otype = str(row[2]) if len(row) > 2 else ''
        if 'Split Order' in otype:
            for day in DAYS:
                gc, _ = D[day]
                split_total += clean_num(row[gc]) if gc < len(row) else 0
    return gross_covers - split_total
```
