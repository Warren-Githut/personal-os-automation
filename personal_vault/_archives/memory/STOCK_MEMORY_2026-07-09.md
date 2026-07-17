---
name: "Stock Memory"
type: "memory_reference"
status: "active"
version: "2026-06-28"
created: "2026-06-28"
last_updated: "2026-06-28"
tags: [preferences, corrections, patterns, lessons-learned]
domain: "stock"
---

# MEMORY — Stock Profile Reference Knowledge

> **SSOT — Single Source of Truth duy nhất.** Mọi thứ đều đọc từ file này.
> Raw lessons log ở `personal_vault/_inbox/_stock_profile_memory_raw.md` (append-only, newest đầu).
> Chỉ update sau `/compress-stock-memory` + Warren approve.
>
> **Auto-sync (read-only):** Hermes đọc file này đầu mỗi session → apply rules.
> **Built-in memory** (`memory` tool) auto-saves mặc định — Hermes tự động ghi nhớ facts durable.
>
> **Built-in memory là cache tạm — KHÔNG phải SSOT.** Mất built-in memory không sao,
> mất STOCK_MEMORY.md là mất tất cả. Warren chỉ cần sửa file vault là đủ.
>
> **Language:** Tiếng Việt (có dấu)
>
> **Hard rule:** Không bao giờ tin tuyệt đối vào LLM — luôn phải VERIFY trước khi trust output.

---

## Per-Session Memory Cycle

1. **Đầu session:** Hermes đọc STOCK_MEMORY.md → apply Preferences / Corrections / Patterns / Lessons Learned
2. **Trong session:** Sau mỗi major task, Hermes silent internal check 3 câu:
   - Điều gì worked? → ghi nhớ để propose
   - Điều gì failed? → ghi nhớ để propose
   - Rule nào rút ra? → ghi nhớ để propose
   > Không nói ra. Không propose giữa chừng.
3. **Cuối session — trigger = `git commit`:** Khi Warren commit (bất kỳ repo nào), Hermes check:
   - Có lessons ghi nhớ từ bước 2? → nếu có → propose cho Warren
   - Warren nói "ghi" → append vào `personal_vault/_inbox/_stock_profile_memory_raw.md` ngay
   - Không có lessons → im lặng, không spam
   > Git commit là deterministic trigger duy nhất. 100% session có check, không bỏ sót, không hên xui.

---

## Monthly Cycle (`/compress-stock-memory`)

Warren chạy `/compress-stock-memory` ~1 lần/tháng hoặc sau 3-4 sessions:

1. **Archive** — copy STOCK_MEMORY.md → `_archives/memory/STOCK_MEMORY_YYYY-MM-DD.md`
2. **Read** — đọc `personal_vault/_inbox/_stock_profile_memory_raw.md` + STOCK_MEMORY.md hiện tại
3. **Distill** — gộp raw lessons vào STOCK_MEMORY.md, xóa trùng, sharpen rules
4. **Propose** — show Warren draft STOCK_MEMORY.md mới
5. **Apply** — Warren OK → ghi đè `personal_vault/00_CORE_LOGIC/STOCK_MEMORY.md`
6. **Clean raw** — clear `personal_vault/_inbox/_stock_profile_memory_raw.md`
7. **Push mem0** — hỏi Warren "có push durable facts lên mem0 không?"
8. **Report** — "Đã distill X raw entries → Y rules. Archive tại _archives/memory/."

---

## Nguyên tắc chung

- Never duplicate entries. Rewrite existing rules when you learn something better.
- Archive before every cleanup.
- Mọi data point phải cite source — xem SOUL.md Data quality tags.
- Không bao giờ tin tuyệt đối vào LLM output — luôn VERIFY trước khi trust.

---

## Write Governance

**HARD RULES:**

| # | Rule | Chi tiết |
|---|------|----------|
| 1 | **Memory write protection** | KHÔNG tự động ghi vào STOCK_MEMORY.md, USER.md, mem0 nếu Warren không nói "ghi" hoặc approve. Chỉ append vào `personal_vault/_inbox/_stock_profile_memory_raw.md` khi có lệnh. **Built-in memory** (`memory` tool) auto-saves mặc định. |
| 2 | **Personal domain cấm tuyệt đối** | KHÔNG được read/grep/search vào `30_KNOWLEDGE_BASE/wiki/02_Health/`, `10_PULSE/Daily_Pulse.md`, `10_PULSE/050_Health_Log.md`, `10_PULSE/051_Sleep_Log.md`, `00_CORE_LOGIC/PERSONAL_*`, `_cases/active/`. Đây là domain của personal_profile, stock-profile không đụng tới. |

**HARD RULE:** Hermes không tự động write vào: **STOCK_MEMORY.md, USER.md, hay mem0.**
> **Built-in memory** (`memory` tool) auto-saves mặc định — Hermes tự động ghi nhớ facts durable.

Mọi proposed write phải qua **2 gates**:

| # | Gate | Nếu NO → |
|---|------|----------|
| 1 | **7 ngày nữa thông tin này còn đúng và có giá trị không?** | SKIP |
| 2 | **Đây là durable fact (preference/decision/config/lesson), hay task artifact?** | Nếu artifact → SKIP |

Chỉ WRITE khi:
1. **Direct command** — Warren nói "lưu", "nhớ giùm", "ghi vào memory" → execute ngay
2. **End-of-session proposal** — Hermes proposes → Warren approves → append raw log
3. **`/compress-stock-memory`** — distills raw → propose → Warren approve → WRITE

---

## Vault Structure

- **Vault root:** `C:/Users/khoans/Documents/Personal_OS/personal_vault`
- **VN Equities:** `30_KNOWLEDGE_BASE/wiki/03_Investing/VN_Equities/`
- **Companies:** `030-Companies/{ticker}/` (gồm Thesis.md, Anti-thesis.md, Catalyst-watch.md, BCTC-*.md)
- **Deploy Capital:** `040_Deploy_Capital_Report.md`
- **Watchlist:** `Candidates_Watchlist.md`
- **Holdings:** `Holdings.md`
- **Sector reports:** `020-Sectors/`

---

## Preferences

*Cách Warren muốn mọi thứ vận hành trong stock context. Hermes tuân thủ mặc định.*

- Warren là system-thinker. Kết luận trong 3-5 bullet đầu. Blunt/rude. Dùng terms EN + Tiếng Việt. Long-term all-in + DCA. Confidence tags: HIGH=BCTC, MOD=web, LOW=estimate. DATA_CONTRACT gate.
- Pulse entry: Tiếng Việt có dấu, newest on top, đọc latest + frontmatter trước khi viết.
- Valuation convention: intrinsic = P/E 5Y avg × TTM EPS [HIGH]. MOS >10%. P/B ≤ ROE×0.1. Giá live fetch, fail→báo lỗi.
- HARD RULE path confinement: search_files/grep chỉ trong path chỉ định. TUYỆT ĐỐI ko search lung tung. mặc định path="" (cwd) chỉ dùng khi Warren nói rõ. Terminal grep phải cd đúng target.
- stock-ingest v3.7: 11 Integrity checks. PASS≥7/11. New ticker: fail=stop. Old ticker: flag drop, continue.
- Firecrawl preferred cho automated scraping. Report silent failures explicitly.
- 📌 Liteparse OCR → fallback vision_analyze.
- 📌 **Search Priority Chain:** Index-first — đọc RETRIEVAL_MAP → 00_WIKI_INDEX → 00_PULSE_INDEX trước khi grep vault. Nếu file có trong index → mở thẳng. Vault → session → web (xem SOUL.md §8).

---

## Corrections

*Lỗi đã từng mắc (valuation mistakes, thesis errors, path errors) + bài học rút ra.*

- **2026-06-28 — Vault path sai:** Built-in memory ghi workspace = Warren_OS_Local. Thực tế vault root = Personal_OS/personal_vault. Đã fix. Bài học: verify vault path khi mới dùng profile, ko assume.

---

## Patterns

*Patterns quan sát được từ thị trường hoặc Warren approach. Hermes chủ động apply.*

- stock-deploy-capital: /100 score + valuation → verdict-first. Scan: 4 pulse + wiki/03_Investing/VN_Equities (deploy report, watchlist, holdings, companies). Live giá. Post-run=git commit.
- 023_VNStock_Sector.md = sector broker reports (TCBS, VNDIRECT, HSC, Bonnejed). NOT 021_Macro or 020-Sectors/. Route sector-level docs here first.
- Frameworks.md: Cron A (Sun 14h, no_agent Python 6 indicators) + Mechanism B (event-driven từ BCTC/report). Skill: macro-frameworks.
- fetch_financials.py: warren-profile/skills/stock-ingest/scripts/. CLI: --batch for RSI. Functions: get_price, rsi, integrity_gate.
- Skill architecture: canonical=warren-profile/skills. Stock-profile refs via hard links. Cross-profile guard auto-redirects writes to warren-profile.

---

## Lessons Learned

*Hard-earned lessons — từ BCTC, từ sai lầm phân tích, từ thesis failures.*

- Mem0: Docker Qdrant + Ollama local + mem0ai. Config $PROFILE/mem0.json. Check: "mem0 status".

---

## HARD RULES (tóm tắt)

1. **SSOT = STOCK_MEMORY.md (vault).** Built-in memory là cache tạm — không phải SSOT.
2. **Không auto-write:** STOCK_MEMORY.md, USER.md, mem0 — chỉ ghi khi Warren nói "ghi". **Built-in memory** auto-saves mặc định.
3. **Không auto-sync ngược:** built-in memory không bao giờ tự động ghi vào STOCK_MEMORY.md.
4. **Chỉ propose lessons khi Warren git commit.** Không propose giữa chừng.
5. **Không bao giờ tin LLM — luôn VERIFY.**
6. **Wiki write protection:** KHÔNG ghi bất kỳ file nào vào `30_KNOWLEDGE_BASE/wiki/` nếu không có lệnh hoặc approval trực tiếp từ Warren. Mọi analysis output phải được Warren approve trước khi write vào wiki.
