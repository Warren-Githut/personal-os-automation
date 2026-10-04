# Lightweight Vector Backend Research — 2026-07-08

Condensed verdicts from Warren's "deep research this tweet/repo, có áp dụng cho cron/parser của tôi không" sessions. All were evaluated against his hard constraints: **laptop-only (min RAM), cost=0 (local), runs 24/7**.

## 1. Gbrain (tweet @tonbistudio / Garry Tan)
- **What:** MIT-licensed postgres-backed "brain" for agents (pgvector + semantic recall + MCP).
- **Verdict:** ❌ NOT applicable. It is a memory/retrieval *layer*, not a parser/cron engine. Warren already has mem0 + WARREN_MEMORY.md + built-in memory covering the same ground. Young repo, breaking changes risk. Overlaps existing stack.
- **Lesson:** A "brain" does not help deterministic parser pipelines (luso-parsers, ops-col, liteparse). Don't chase new memory layers when one already fits.

## 2. Hermes Session Export (tweet @Teknium)
- **What:** `hermes sessions export [--redact] [--source cron|cli|telegram] [--newer-than 1w] [--older-than 7d] [--dry-run] [--format jsonl]`
- **Verdict:** ✅ APPLICABLE — for **audit/backup of automation**, not memory. Built a weekly cron (`session-backup-weekly`) exporting cron sessions >7d, redacted, local-only, Telegram-delivered.
- **Teknium redact caveat:** `--redact` only scrubs API-key-like text. Email (`nguyen.s.khoa@gmail.com`), vault paths, token paths are NOT redacted → **local-only, never upload to HF**.
- **Volume reality:** ~410 cron sessions/day → ~177MB/week. Rotate >28d.

## 3. zvec (Alibaba, github.com/alibaba/zvec)
- **What:** In-process vector DB (C++, 14.1k stars, Apache-2.0, Windows OK). Dense + sparse + FTS + hybrid + DiskANN. v0.5.0.
- **Verdict:** ❌ NOT a mem0 replacement. It is a *vector engine* — no memory lifecycle (dedup, facts-by-user, compress). Would require building a custom mem0 layer on top. Young (v0.5.1), API churning.
- **When it WOULD fit:** if Warren wanted to self-build hybrid semantic+keyword search over the vault (zvec has built-in FTS). Not now.

## 4. Tencent Agent Memory (tweet @RoundtableSpace, github.com/TencentCloud/TencentDB-Agent-Memory)
- **What:** Local long-term memory for agents. SQLite + sqlite-vec, L0→L3 layering (conversation→atom→scene→persona), symbolic Mermaid offload. **Has official Hermes adapter** (`hermes-plugin/memory/memory_tencentdb`). 7.3k stars, MIT.
- **Verdict:** ❌ REJECTED for Warren's goal. Reasons:
  1. Runs a **Node.js Gateway sidecar** (port 8420) — replaces Qdrant server with a *different* server.
  2. Needs **LLM API key for L1/L2/L3 extraction** → recurring API cost (Warren uses free local Ollama).
  3. **Breaks** `mem0_*` tools + `mem0-cleanup-warren` / `mem0-30day-review` cron (provider swap to `memory_tencentdb`).
  4. Symlinks into `~/.hermes/hermes-agent/plugins/memory/` — touches Hermes core tree, version-match risk.
- **Irony:** Its L0→L3 philosophy *exactly matches* Warren's vault design (WARREN_MEMORY.md = L3, sessions = L0, cases/wiki = L2). But Warren already does this manually via `/compress-memory` — no need to automate it via a heavy Node sidecar + API cost.

## 5. LanceDB
- **Verdict:** ❌ NOT available in mem0 2.0.10 (Warren's pinned version). `from mem0.vector_stores import LanceDB` → ImportError. Would need mem0 upgrade → risk breaking Hermes. This is what killed the original "swap to LanceDB" plan and pivoted to FAISS.

## Final decision
**FAISS** (in-process, native in mem0 2.0.10, free with Ollama, ~50MB) is the optimal Qdrant replacement for Warren. See SKILL.md "Swap Qdrant → FAISS" for the procedure.
