# Cross-Profile Brief — replicate memory cleanup on another profile

Handoff used to replicate the personal_profile memory cleanup onto stock-profile (and any other profile).

## A. 2-STORE ARCHITECTURE (read carefully — avoid the bug)
| Store | What | Limit | Who writes | When full |
|-------|------|-------|-----------|-----------|
| (a) Built-in | `memory` tool | 2,200 char HARD cap | Hermes freely prunes + adds (Warren no opinion) | Hermes manages natively |
| (b) mem0 FAISS | `mem0.json` + `mem0_faiss/` | UNLIMITED | ONLY `/compress-memory` (Python) | never |

- SSOT = raw vault file (`_stock_memory_raw.md` etc.), unlimited, append-only → distill → reference file.
- ANTI-LOOP: (a) full → Hermes prunes+adds freely. ONLY banned: loop-delete (a) to stuff (b) into (a).
  (b) pushes via Python, never through the `memory` tool.
- BUG HIT BEFORE: thought `memory` tool = mem0 (SOUL §10 says so). Pushing (b) via `memory` tool
  → rejected at 2,200 → looped delete 4×. Don't repeat.

## B. /compress-memory PROTOCOL
1. Archive reference file → `_archives/memory/<NAME>_YYYY-MM-DD.md`
2. Read raw + current reference
3. Distill → rewrite reference (Preferences / Corrections / Patterns / Lessons Learned)
4. Clean raw (keep frontmatter)
5. Push mem0 (b) via Python (see C)

## C. PUSH MEM0 (b) VIA PYTHON (the only working path)
`memory` tool CANNOT push (b). Use `mem0` lib from hermes-agent venv.
- Script: copy `references/mem0_push_template.py`, edit `profile_dir`, `USER`, `facts`.
- Run with: `C:\Users\khoans\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe scripts/mem0_push_*.py`
- LLM extraction ~30–50s/fact → RUN BACKGROUND + notify_on_complete. Foreground times out 60s.
- VERIFY user_id per profile (personal='warren_personal'; stock likely 'warren_stock').

## D. HARMLESS WARNINGS (ignore)
faiss keyword-search disabled · spaCy not installed · PostHog multiple clients

## E. STOCK TODO
1. Run /compress-memory on STOCK_MEMORY
2. Write push script (copy C, fix USER + facts)
3. Verify user_id
4. Push background, poll /tmp/mem0_push.log for ADDED_IDS
