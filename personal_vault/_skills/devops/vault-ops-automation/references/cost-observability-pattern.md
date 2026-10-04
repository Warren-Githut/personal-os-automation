# Cost Observability Pattern — COST_LOG.md

Every LLM-driven cron job logs token usage + estimated cost to `vault/00_CORE_LOGIC/COST_LOG.md` after each run.

## File Structure

```
---
name: Automation Cost Log — Token & Cost Tracking
type: operation_log
rate_input: "$0.15/1M tokens (DeepSeek V4 Flash)"
rate_output: "$0.60/1M tokens (DeepSeek V4 Flash)"
---

<!-- TEMPLATE: Cost Entry -->
# Automation Cost — Token & Cost Tracking

## Total Accumulator
| Period | Input Tokens | Output Tokens | Total Tokens | Est. Cost |
|--------|-------------|--------------|-------------|-----------|
| YYYY-MM-DD | N | N | N | $X.XX |

---
## cron-name @ HH:MM DD/MM
- Tokens: input=X output=Y total=Z
- Cost: $0.00XX (input×$0.15/M + output×$0.60/M)
- Run notes: no-op / full triage / partial action
```

## Entry Format (prepend, newest on top)

```markdown
## col-queue-watcher @ 16:45 30/06
- Tokens: input=22,000 output=800 total=22,800
- Cost: $0.0038
- Run notes: no-op — queue empty
```

## Token Estimation

LLM tự estimate: 4 chars ≈ 1 token. Accuracy ±20% là chấp nhận cho V1.

- Input: prompt length + skill content + tool outputs
- Output: response length

## Cost Rates (DeepSeek V4 Flash)
- Input: $0.15/1M tokens
- Output: $0.60/1M tokens

## Accumulator Table

Insert/update row mỗi lần chạy: append dòng dưới header cho period tracking.
Update các dòng Daily/WTD/All-time khi thêm entry mới.

## Cron Prompt Injection

Thêm step vào cuối mỗi LLM-driven cron prompt:

```markdown
### Step N: Post-Run Critique + Cost Log (ALWAYS — even if no data)
Estimate your token usage (4 chars ≈ 1 token). Prepend TWO entries:

1. To vault/00_CORE_LOGIC/AUTOMATION_HEALTH.md with field "Toks: input=X output=Y total=Z"
2. To vault/00_CORE_LOGIC/COST_LOG.md with cost calculation
```

## Boundaries
- **Always:** Log token count sau mỗi lần chạy. Prepend entry. Tính US$.
- **Never:** Log deterministic scripts (no_agent), edit entry cũ.
