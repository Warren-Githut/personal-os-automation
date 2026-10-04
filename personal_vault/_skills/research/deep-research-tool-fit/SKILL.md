---
name: deep-research-tool-fit
description: Evaluate whether an external tool/repo (GitHub/X link) fits the user's existing workflow — non-IT explanation, honest pushback, concrete comparison table, 3 options + recommended. Use when Warren sends a repo/tweet and asks "deep research, có áp dụng cho workflow của tôi không, giải thích non-it, use case."
type: skill
---

# Deep Research — Tool Fit Evaluation

## When to use
User sends a GitHub repo or X/Twitter link and asks (any phrasing) to:
- "deep research cái này"
- "xem có áp dụng được cho workflow cron/parser của tôi không"
- "có ổn hơn mem0 không" / compare to current stack
- "giải thích cho dân non-it, use case"

This is a RECURRING Warren pattern (done for Gbrain, zvec, Tencent Agent Memory, mem0 in one session).

## Process
1. **Pull the source** — `mcp_smart_fetch` the repo URL (GitHub README + any X thread). If truncated, `read_file` the cached markdown at offset to get README body.
   - **🚨 FALLBACK WHEN FETCH IS BLOCKED:** Con có thể dùng `web_extract` (Firecrawl, nếu có credit) hoặc curl fallback. Khi hết credit:
     - **(A) GitHub / docs site (trang tĩnh public):** Dùng `terminal` chạy `curl -sL --max-time 25 <url>` → lưu file → `read_file`. Hoặc `curl -sL "https://raw.githubusercontent.com/<owner>/<repo>/<branch>/README.md"`. GitHub API: `curl -sL "https://api.github.com/repos/<owner>/<repo>"` (public, no auth). **Đây là cách B — miễn phí, hoạt động [HIGH].** Xem `references/web_scrape_no_credit.md`.
     - **(B) X/Tweet:** curl không vào được (cần auth). BẮT BUỘC nhờ Warren paste text hoặc gửi screenshot → con `liteparse` OCR. KHÔNG tự scrape được.
     - **(C) Không báo "không đọc được" rồi đoán.** Báo trung thực + đề xuất (A)/(B).
   - **Verify curl thoát mạng:** test `curl -sL --max-time 20 "https://docs.python.org/3/library/sqlite3.html" -w "HTTP %{http_code}"` → 200 = OK. 404 = URL sai (không phải lỗi mạng).
   - **MSYS /tmp quirk:** `curl` ghi `/tmp/x.html` nhưng `read_file` không thấy (path map khác). Copy về workspace trước: `python3 -c "import shutil; shutil.copy('/tmp/x.html', r'C:/Users/khoans/Documents/Warren_OS_Local/_tmp_x.html')"` rồi read. Xóa sau khi xong.
2. **Identify what it ACTUALLY is** vs what the user might think. State plainly: "X is a <category>, not a <category>." (e.g. "zvec is a vector engine, not a memory layer"; "Gbrain is a brain/retrieval layer, not a parser executor").
3. **Compare against current stack** — read WARREN_MEMORY.md / SOUL / relevant skills to know what's already in place. Don't propose a 3rd copy of something that already exists.
4. **Non-IT explanation** — one metaphor paragraph. No jargon.
5. **Honest pushback with evidence** — if it does NOT fit, say so directly with reasons (overlap, wrong layer, young/breaking, overkill for scale). Warren expects disagreement backed by proof, not sycophancy.
6. **Concrete comparison table** — columns: Server?, Windows?, In-process?, Fits cron/parser?, Risk. Cite sources.
7. **3 options + recommended** — A (recommended) / B (alternative) / C (reject), with effort + risk each.

## Lens 0 — Install target / runtime compatibility (RUN BEFORE fit verdict)

A hot GitHub repo (high stars/forks) is NOT automatically usable by Warren. Before recommending adoption, check the **install command and target runtime**:

- Read the repo's install docs / `npx skills add ... --agent <X>` or equivalent. If the only supported agents are **Codex / Cursor / Claude Code** (or another coding agent) and there is **NO `--agent hermes` / Hermes path**, the tool **cannot load or run on Warren's Hermes Desktop** as a native skill — but **check if it's an MCP server** first.
- **MCP protocol override:** Hermes supports MCP natively via `hermes mcp add <name> --command <cmd>`. If the tool speaks the Model Context Protocol (mcp package, MCP server entrypoint), it CAN run on Hermes even without `--agent hermes` support. Vd: `dondai1234/master-fetch` (Hound) — pip install → `hermes mcp add hound --command hound` → 6 tools (smart_fetch, smart_search, smart_crawl, screenshot...) available natively.
- **How to detect MCP:** grep README/pyproject.toml for `mcp`, `modelcontextprotocol`, `MCP server`. If the repo has `mcp` in dependencies or an entry point named `<name>` that starts an MCP server → it's MCP-compatible.
- Distinguish: **installable skill** (needs a host agent like Codex/Cursor — dead on Hermes if no --agent hermes) vs **MCP server** (standard protocol — works on any MCP client including Hermes) vs **standalone service/app** (runs itself).
- If the tool is domain-mismatched AND runtime-mismatched (not MCP, not pip-installable), the verdict is a fast **reject** — do not over-explain.

**Example (2026-07-19, loopy):** `Forward-Future/loopy` ⭐2.8k — install is `npx skills add Forward-Future/loopy --agent codex|cursor|claude-code`. No Hermes target. Verdict: do NOT install; borrow 2 concepts (Run Receipt format, Loop Doctor audit) instead. The repo being popular did not change the runtime blocker.

Add a column to the comparison table: **Runs on Hermes?** (Yes / No / Partial). Cite the install command as evidence.

## Core insight (durable)
Warren's cron/parsers (`luso-parsers`, `ops-col`, `liteparse`, `gen_today`) are **deterministic data pipelines** (regex/CSV/GSheet). Vector DBs / memory layers / "brain" tools (Qdrant, mem0, Gbrain, zvec, Tencent Agent Memory) are **retrieval/memory layers** — they do NOT make parsers faster or replace them. Don't confuse the two layers.
- If the tool is a memory/vector layer → evaluate against mem0/Qdrant, not against cron.
- If the user wants to REMOVE a heavy component (e.g. Qdrant) → distinguish "swap backend" (keep layer, change engine) from "remove layer" (rebuild). See `references/mem0-backends.md`.

## Verification
- Cite repo README/stars/license as sources.
- State confidence on fit verdict.
- Don't fabricate benchmarks — quote the repo's claimed numbers and label them as vendor claims.

## Pitfalls
- Don't assume "new + popular = better for Warren." His stack is purpose-built; young repos (v0.5) have breaking API churn.
- Don't recommend adding a 3rd memory layer when mem0 + WARREN_MEMORY.md already cover it (SSOT rule).
- Distinguish engine vs layer: zvec/LanceDB = engines (need a memory layer on top); mem0/Tencent = layers.
- See `references/mem0-backends.md` for the swap-vs-remove decision, mem0's Qdrant+Ollama deps, and backend comparison table.
- **🚨 Hound (mcp_smart_fetch) now primary — Firecrawl/web_extract là fallback khi Hound block.**
- **Skill BUNDLES (local SKILL.md packs) need a different audit than repos/MCP tools:** enumerate + read EVERY file (references/tests/scripts, not just SKILL.md), actually RUN the bundled validator + unittest, and apply the lens "claims a discipline ≠ implements one" — prompt-only 'verification'/'safety'/'source ledger' features have zero machinery; bundle tests validate the markdown, not runtime behavior. Also check overlap vs already-installed warren-profile skills before recommending adoption. Full method + borrowable patterns: `references/skill-bundle-audit-method.md` (Hermes Field Kit case, 2026-07-26).
- **SaaS/tech repos ≠ F&B directly applicable.** When evaluating a SaaS marketing/dev repo for L'Usine, flag the bias explicitly (e.g. CRO/SEO/signup skills are web-only, low fit for offline F&B). Adapt framework, don't install wholesale. See `references/marketingskills-deep-dive.md` (coreyhaines31/marketingskills case).

## Concrete Execution Protocol (Hermes Field Kit case, 2026-07-26)

When the repo is a **multi-file skill bundle** (>=20 files) and Warren says "explore + deep research, read EVERY file": do NOT read file-by-file in main context (blows context). Use this deterministic sequence:

1. **Clone locally** — `git clone --depth 1 <url> <local>` to get real files (not fetch-truncated markdown). Verify with `find . -type f` count.
2. **Read README + catalog + roadmap FIRST** — get the admission rule, skill list, version claims.
3. **Dispatch parallel subagents** — `delegate_task(tasks=[...])` splitting by directory groups (e.g. 3 doctor skills / 4 audit skills / repo-infra). Each subagent reads EVERY file in its slice + RUNS the bundled validator (`python scripts/validate.py`, `python -m unittest discover`) + reports evidence (file:line). Cap 3 concurrent (max_concurrent_children).
4. **Spot-check yourself** — independently verify 2-3 key SKILL.md + RUN the repo's own validator in terminal (real evidence: "Validation passed: 13 skills"). Subagent self-reports are suggestions, not ground truth.
5. **Cross-check middle of truncated summaries** — if a subagent output is truncated, `read_file` the saved `subagent-summary-*.txt` (full path given) to recover detail before reporting to Warren.
6. **Report** — conclusion-first: what it IS, fit verdict, which to adopt, red flags (verify claims on disk, not from README).

**Why this matters:** deep-research on a 65-file repo without subagents = context overflow. With subagents + local clone + real validator run = thorough AND verifiable. The "claims a discipline ≠ implements one" lens is mandatory: prompt-only skills (read-only checklists) have zero diagnostic code — quality = model diligence.
