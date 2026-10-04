---
name: cross-source-reconcile
description: Discipline for reconciling parser output against a SECOND independent source (Hourly GSheet vs Revenue SSOT, COL vs Master, GrabFood vs SSOT). Prevents false "gap" alarms caused by stale/pre-ingest cached cross-checks. Use whenever a parser emits numbers that must agree with another SSOT/file before being reported or committed.
type: skill
version: 1.0
status: active
applies_to: ["Hermes Desktop"]
---

# cross-source-reconcile — Two-Source Reconciliation Discipline

> **Warren root-cause lesson (2026-07-20):** A false "gap" alarm between two data sources is a trust violation, not a minor error. The agent reported "W29 hourly vs W28 SSOT lệch 6.4% 🔴" when Warren had already ingested SSOT W29 four hours earlier. The parser HAD read the SSOT (W29 block present) but was run BEFORE ingest → cached the stale W29-vs-W28 result. Re-run after ingest → W29 vs W29 = 0.1% net / 0.3% covers (PASS). The gap never existed.

## When this applies
- A parser emits aggregates that must agree with a SECOND source before report/commit:
  - `09_Hourly_Cover_Revenue_Log` (GSheet) vs `01_SSOT_01_Weekly_Revenue_Log` (PowerBI)
  - COL weekly vs `02_MASTER_CPH` / Master
  - GrabFood weekly vs Revenue SSOT
  - Any "X vs Y" where X and Y are independently authored
- NOT for single-source parses (use `verify-parser-output` independent recompute instead).

## Mandatory Rules (the gate)

### R1 — RE-RUN before reporting any gap >5%
The cross-check reads the second source FRESH from disk each run. A cached or pre-ingest result is STALE. Never report a gap derived from a run that predates the second source's update.

### R2 — Compare SAME period, never prior
Checking W29 → compare W29(source A) vs W29(source B). NEVER fall back to "W29 vs W28" unless source B genuinely lacks a W29 block (the DATA GAP state). Mixing periods manufactures a fake gap from organic W/W growth.

### R3 — Distinguish the two states explicitly
Output MUST make the state unmistakable:
- `(a) SSOT W29 MISSING → "DATA GAP, chờ ingest"` — no alarm, no "lag" claim.
- `(b) SSOT W29 PRESENT → "lệch X% 🟢/🔴"` — real reconcile.
Never merge into one ambiguous "gap" message. The parser `cross_check_ssot()` MUST print an explicit status line (e.g. `> ✅ **SSOT tuần W29 CÓ MẶT** — cross-check so CÙNG tuần`).

### R4 — Auto re-poll trigger (agent behavior)
When Warren says "đã ingest / đã nhập / có rồi" + names the SSOT file → the agent MUST re-run the cross-check parser IMMEDIATELY. Hard trigger, not optional. Do not wait for Warren to ask "re-run".

### R5 — Never claim "source missing/lag" without post-ingest re-run
That conclusion requires the post-ingest run to return DATA GAP — not a pre-ingest cached result. If you have not re-run since Warren confirmed ingest, you cannot assert the source is missing.

## Embedding in the parser (baked-in gate)
Follow the `verify-parser-output` "Baking the Gate Into the Parser" pattern, but the cross-check block adds R1–R3:
```python
def cross_check_ssot(week_start, week_end, sys_ac, sys_net):
    # ... read SSOT file FRESH ...
    m = re.search(rf"##\s+\S+\s*\|\s*{start}\s*→\s*{end}.*?(?=\n## |\Z)", rc, re.DOTALL)
    if not m:
        return [f"> ⚠️ **DATA GAP:** SSOT chưa có tuần {start}→{end}. Không thể cross-check."]
    lines.append(f"> ✅ **SSOT tuần {wid} CÓ MẶT** — cross-check so CÙNG tuần.")
    # ... compare same-week numbers, flag >5% ...
```
FAIL (gap >5% AND source present) → still write the entry but the cross-check line carries 🔴 so Warren sees it; the parser itself does not abort (the internal verify_gate already ensured hourly==daily). Abort only on INTERNAL inconsistency, not on cross-source drift (Warren decides on cross-source gaps).

## Battle-test for this gate
Temp `hermes-verify-*.py` under `%TEMP%`:
- **B1:** SSOT W29 present → output contains "CÓ MẶT" + "Khớp", NOT "DATA GAP".
- **B2:** SSOT W99 absent → output contains "DATA GAP", NOT "CÓ MẶT".
- **B3:** re-run reads latest SSOT (no cached state between calls).
- **Verify:** W29 net 683.7M vs SSOT 684.6M = 0.13%; covers 2590 vs 2583 = 0.27% (both <5% → PASS).

## First-Principles root-cause pattern (Elon Musk style)
When a cross-source check surprises you (unexpected gap), before blaming the data:
1. **State the problem without externalizing** — "I reported a gap; was the second source actually read post-update?"
2. **Decompose assumptions** — (a) did I re-run after the source changed? (b) did I compare same period? (c) did I distinguish present-vs-missing?
3. **Find the system flaw** — usually: cached result, wrong comparison period, or ambiguous state message — NOT a data error.
4. **Fix the system, not the symptom** — add re-poll trigger + same-period compare + explicit state line. Embed in `WARREN_MEMORY.md` HARD RULE + `SOUL.md` §5 + parser code.

## Related
- `verify-parser-output` — independent recompute + baked-in gate (single source).
- `WARREN_MEMORY.md` HARD RULE — Cross-Source Reconcile Gate (canonical governance text).
- `SOUL.md` §5 — Cross-Source Re-Poll Trigger.
- Reference: `references/w29-false-alarm-repro.md` — full reproduction recipe (thousands-sep parse fix + subtotal-authority + reconcile).
