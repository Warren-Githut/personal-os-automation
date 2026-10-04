# Loop Ready Score — Automation Health Dashboard

Score 0–100 đánh giá automation health của warren-profile. Chạy cùng `audit-automation` mỗi CN 19:00.

## File

`vault/00_CORE_LOGIC/LOOP_READY_SCORE.md`

## 5 Dimensions

| Dimension | Max | Calculation |
|-----------|-----|-------------|
| Cron Health | 30 | 30 − (cron_errors_last_7d × 5), min 0 |
| State Freshness | 25 | 25 − (stale_files × 8), min 0. Check: AUTOMATION_HEALTH.md, COST_LOG.md, CONTEXT.md, TODAY.md |
| Critique Coverage | 20 | (unique_crons_with_critique / 7) × 20 |
| Cost Tracking | 15 | COST_LOG has entry last 7d? Accumulator updated? → 15/7/0 |
| Delegation Zone | 10 | 10 − (zone_drifts × 2), min 0 |

### How to calculate each

1. **Cron Health** — scan cron jobs. Count `last_status = error` trong 7 ngày
2. **State Freshness** — đọc frontmatter `last_updated` của 4 files. >7 ngày = stale
3. **Critique Coverage** — scan AUTOMATION_HEALTH.md entries 7 ngày. Count unique cron names
4. **Cost Tracking** — COST_LOG.md có entry 7 ngày? Accumulator có số >0?
5. **Delegation Zone** — từ audit Step 3 zone_drift count

## Entry Format (prepend)

```markdown
## 2026-06-30 — Score: 85/100 🟢

| Dimension | Pts | Detail |
|-----------|-----|--------|
| Cron Health (30) | 30 | 0 errors last 7d |
| State Freshness (25) | 25 | all fresh |
| Critique Coverage (20) | 15 | 5/7 crons covered |
| Cost Tracking (15) | 7 | has entry, no accumulator |
| Delegation Zone (10) | 8 | 1 zone drift |

**Trend:** △+5 vs last week
**Action:** Add critique for stock-route-pending
```

## Score History Table

Append row dưới header mỗi lần chạy:

```markdown
| Date | Total | Cron | State | Critique | Cost | Zone | Trend |
|------|-------|------|-------|----------|------|------|-------|
| 2026-06-30 | 85 | 30 | 25 | 15 | 7 | 8 | Baseline |
```

## Ranges
- ≥90 🟢
- 70–89 🟡
- <70 🔴

## Integration

Added as **Step 5** in `audit-automation` skill. Runs automatically on Sunday 19:00 cron.
