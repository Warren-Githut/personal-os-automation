# Performance Review Checklist

Use when the change touches data volume, loops, I/O, or UI rendering. For deep profiling see `performance-optimization`.

## Query & Data Access
- [ ] No N+1 query pattern (batch fetches instead of per-row round-trips)
- [ ] No unbounded `SELECT *` / full-table scans without filter
- [ ] Pagination on list/collection endpoints

## Loops & Hot Paths
- [ ] No unbounded loops or unconstrained data fetching (cap or stream)
- [ ] No large object/materialization created inside hot loops
- [ ] Repeated computation hoisted out of loops (cache invariant results)

## Concurrency & Async
- [ ] Synchronous blocking calls that should be async identified (I/O-bound work)
- [ ] No race conditions on shared state (locks / atomic ops where needed)
- [ ] Cron / scheduled jobs don't recursively schedule more jobs

## UI / Rendering
- [ ] No unnecessary re-renders (memoize, stable keys)
- [ ] Large lists virtualized or windowed
- [ ] Chart/dashboard data fetched once, not per-frame

## Parsers / Batch Jobs (L'Usine context)
- [ ] File scan bounded (excluded dirs: `__pycache__`, `.trash`, `.git`)
- [ ] Cross-source assertions use independent inputs (no self-comparison no-op gate)
- [ ] Idempotent re-runs don't multiply cost (cache rebuild is O(n), not O(n²))

## Thresholds (from battle-test coverage)
- Script parse success ≥ 95% · Execution time < 180s · Overall score ≥ 90%

## Severity
- Performance finding causing >2× regression or unbounded growth → **Major** (non-blocking, notify).
- Micro-optimization without measurable impact → **Nit** (optional).
