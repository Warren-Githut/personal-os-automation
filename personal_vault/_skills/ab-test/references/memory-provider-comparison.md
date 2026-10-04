# Memory Provider A/B Test: Mem0 (Vector) vs Built-in (FTS5)

## Test Date
2026-06-24 — Warren's L'Usine ops environment

## Setup
- **Facts stored:** 5 facts (cafe den, LU3 location, OIL 325M, Warren role, Telegram report)
- **Mem0 config:** DeepSeek v4 Flash LLM + Ollama nomic-embed-text (768d) + Qdrant local
- **Built-in:** Hermes SQLite FTS5 (keyword exact match)

## Test A: Exact Keyword
Both systems found all 5 facts when query matched stored keywords exactly.
- Mem0: 5/5, avg 259ms
- Built-in: 5/5, avg ~0ms

## Test B: Semantic (different wording)
Queries used completely different words than stored facts (e.g. "do uong yeu thich" for "cafe den").
- Mem0: **5/5** (100%) — vector search found semantically similar content
- Built-in: **0/5** (0%) — FTS5 requires exact keyword match

## Winner: MEM0
- 100% semantic recall vs 0% for built-in
- 259ms avg latency (acceptable for conversation flow)
- Additional advantage: auto LLM fact extraction from conversation

## Windows Qdrant Lock Issue
Qdrant local on Windows uses `portalocker` with `msvcrt.locking()`. Creating multiple `Memory()` instances in the same Python process causes:
```
RuntimeError: Storage folder C:\Users\khoans\.mem0\migrations_qdrant is
already accessed by another instance of Qdrant client.
```
**Workaround:** Use `subprocess.run([sys.executable, "-c", code])` per test. Each process starts fresh, no lock conflict. This matches real usage (each Hermes profile runs in its own process).
