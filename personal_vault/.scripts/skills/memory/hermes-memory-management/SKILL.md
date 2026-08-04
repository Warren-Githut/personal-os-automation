---
name: "hermes-memory-management"
type: "skill"
status: "active"
version: "2026-07-09"
created: "2026-07-09"
description: "Manage Hermes's two distinct memory stores across profiles — built-in `memory` tool (2200-char cache) vs separate mem0 FAISS (unlimited, Python-pushed). Covers the /compress-memory protocol, the raw SSOT file pattern, the corrected anti-loop rule, and the exact Python technique to push durable facts into mem0 FAISS. Use whenever a session ends, after a major task, or when Warren says 'compress-memory' / 'ghi nhớ' / 'mem0'."
triggers:
  - "Warren says 'compress-memory' or '/compress-personal-memory' / '/compress-memory'"
  - "Warren says 'ghi nhớ' / 'lưu' / 'mem0' / 'push mem0'"
  - "End of session / after major task — distill lessons"
  - "memory tool rejects with 'over the limit' / 2,200 chars"
---

# Hermes Memory Management — 2 Stores, 1 SSOT

## The core model (memorize this)

Hermes has **TWO SEPARATE memory stores**. Conflating them is the #1 failure mode — the docs
themselves blur them (SOUL.md §10 sometimes says "`memory` tool = mem0 FAISS", which is WRONG in practice).

| | (a) Built-in memory | (b) mem0 FAISS local |
|---|---|---|
| Access | `memory` tool | Python `mem0` lib (separate) |
| Limit | **HARD 2,200-char WRITE CAP** | **UNLIMITED** |
| Who writes | **Hermes freely** — prune stale + add new when full. Warren has NO opinion (native management). | **ONLY `/compress-memory`** (distills raw → mem0). Never written directly mid-session. |
| Backed by | Hermes agent runtime | `mem0.json` config + `mem0_faiss/` vector store in the profile dir |
| Fills up? | Yes (hit 4× in one session) | Never |

**SSOT (single source of truth):** the vault raw file — `_personal_memory_raw.md`,
`_stock_memory_raw.md`, or `WARREN_MEMORY` raw log. **UNLIMITED, append-only.** Distilled
into the reference file (`PERSONAL_MEMORY.md`, `STOCK_MEMORY.md`, `WARREN_MEMORY.md`) by `/compress-memory`.

> ⚠️ The `memory` tool IS store (a) — NOT mem0. Pushing (b) facts via the `memory` tool fails
> with "over the limit 2200" because you're hitting (a)'s cap, not (b)'s. (b) is pushed via Python.

## CORRECTED ANTI-LOOP RULE (user-corrected — do NOT over-correct)

**Wrong (over-corrected once):** "when (a) nears cap → STOP, don't delete entries."
**Right:** Hermes may freely prune stale + add new to (a) when (a) is full — that's native management,
Warren explicitly said he has no opinion on (a).

The ONLY loop that is banned: **looping delete of (a) entries to stuff (b) content into (a).**
(b) belongs in mem0 FAISS, pushed via the Python script — never squeezed through the 2,200-char `memory` tool.

If `memory` tool returns "2,163/2,200 — over the limit": that is store (a). Do NOT loop-delete to fit.
Write the lesson to the raw SSOT file instead. (b) gets pushed separately via Python during `/compress-memory`.

## /compress-memory PROTOCOL (run on demand)

1. **Archive** the current reference file → `_archives/memory/<NAME>_YYYY-MM-DD.md`
2. **Read** the raw SSOT log + current reference file
3. **Distill** → rewrite reference file, grouped: Preferences / Corrections / Patterns / Lessons Learned. Dedupe, sharpen.
4. **Clean raw** — empty the SSOT log (keep frontmatter + header comment)
5. **Push mem0 (b)** — see below. Ask Warren first; if OK, run the Python push.
6. **Report** — "Distilled X raw → Y rules. Archive at _archives/memory/. Pushed N facts to mem0."

## Pushing mem0 (b) via PYTHON (the only working path)

The `memory` tool cannot write (b). Use the `mem0` Python lib (ships in hermes-agent venv).

**Script template** → `references/mem0_push_template.py` (copy + edit `USER` and `facts`).

Key facts:
- **Venv with mem0 lib:** `C:\Users\khoans\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe`
  (add `.../hermes-agent/venv/Lib/site-packages` to `sys.path`).
- **Config:** read `mem0.json` from the profile dir (`personal_profile` / `stock-profile` / `warren-profile`).
- **user_id:** VARIES per profile. personal = `'warren_personal'`. VERIFY stock/warren before pushing
  (check `scripts/mem0_scan_*.py` or existing memories — likely `'warren_stock'` / `'warren'`).
- **LLM extraction is SLOW (~30–50s/fact)** because `m.add()` calls the LLM. **ALWAYS run in background**
  with `notify_on_complete=true`. Foreground times out at 60s.
- Harmless warnings to ignore: *faiss does not support keyword search*, *spaCy not installed*, *PostHog multiple clients*.

Run:
```
cd <profile_dir>
C:\Users\khoans\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe scripts/mem0_push_compress_YYYY-MM-DD.py
```
Then poll the log for `ADDED_IDS=[...]` per fact.

## PITFALLS
- **Conflating stores** — SOUL.md §10 wording misled the agent into thinking `memory` tool = mem0. It's (a). (b) = separate FAISS.
- **Loop-delete-to-fit** — never delete (a) entries to make room for (b) content. Write (b) via Python.
- **Foreground push** — times out at 60s; `m.add` takes 30–50s each. Use background.
- **Wrong user_id** — verify per profile before pushing or facts land under the wrong namespace.
- **Trusting preview over file** — `read_file`/preview sometimes drops Vietnamese diacritics; trust the actual file. (Also a general rule.)

## REFERENCES
- `references/mem0_push_template.py` — ready-to-copy push script (edit USER + facts).
- `references/cross-profile-brief.md` — the handoff brief used to replicate the cleanup across personal → stock profile.
