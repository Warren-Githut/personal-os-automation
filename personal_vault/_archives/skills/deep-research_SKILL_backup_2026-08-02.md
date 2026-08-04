---
name: deep-research
description: "Deep research harness cho Warren — biến 1 câu hỏi thành báo cáo có trích dẫn đầy đủ, qua cite-check + phản biện. Port tinh thần hyperresearch (16-step pipeline) sang Hermes + Nemotron free. Dùng khi Warren cần research sâu, báo cáo có nguồn, hoặc nói '/deep-research <câu hỏi>'."
version: 0.1.0
model_note: "Chạy trên model free (nvidia/nemotron-3-nano-30b-a3b:free qua OpenRouter). Bố switch model sang Nemotron free trước khi gõ, hoặc chạy qua cron pin model đó. KHÔNG dùng model trả tiền."
category: research
tags: ['research', 'deep', 'synthesis', 'subagent']
related_skills: ['capture']
---

# /deep-research — Deep Research Harness (Full 16-step, Hermes port)

> Port ý tưởng từ hyperresearch (jordan-gibbs/hyperresearch, MIT) sang Hermes.
> Mục tiêu: 1 câu hỏi → báo cáo có trích dẫn, verified, qua phản biện.
> Chạy trên **Nemotron free** (0₫). Output vào `vault/_inbox/research/<slug>.md`.

## Tại sao skill này tồn tại (Warren rule: mọi file phải có lý do)
Bố muốn research sâu (market, competitor, trend) nhưng: (1) hyperresearch gốc chạy trên
Claude Code trả tiền → không vào được Hermes; (2) Bố xài model free → cần pipeline tối ưu
ít subagent. Skill này lấy TINH THẦN hay nhất của họ (cite-check, independence audit,
source ranking, patch-not-regenerate) và đóng gói lại cho Hermes.

## Khi nào dùng
- Bố hỏi research sâu 1 chủ đề (market F&B, competitor, trend công nghệ...)
- Bố gõ `/deep-research <câu hỏi>`
- KHÔNG dùng cho: lookup nhanh 1 facts (dùng mcp_smart_search trực tiếp), legal/compliance (zone 🔴).

## Convention BẮT BUỘC — token tiến độ
Mỗi bước in đúng 1 dòng để Bố thấy tiến độ (chống "context rot" như bản gốc):
```
🔰 DR-STEP n/16: <tên bước ngắn>
```
Thiếu token = vi phạm (y như thiếu boot token).

## Model pin (đọc kỹ)
- Skill này thiết kế cho **Nemotron free** (`nvidia/nemotron-3-nano-30b-a3b:free`).
- Nemotron yếu hơn Opus/Sonnet của bản gốc RẤT NHIỀU → báo cáo nông hơn benchmark gốc.
  Bù bằng kỷ luật cite-check + 2 critic (SOUL §5), không cậy model khỏe.
- Cách Bố chạy: xem cuối file (mục "Cách Bố dùng").

## Output path
- Báo cáo cuối: `vault/_inbox/research/<slug>.md` (slug = tiếng Anh viết liền, vd `ai-impact-fnb-vn`).
- File trung gian (query.md, draft.md...): cũng trong `vault/_inbox/research/` cùng thư mục run.

## 16-Step Pipeline (tổng quan — chi tiết từng bước ở dưới)
| # | Bước | Tool Hermes | Output |
|---|------|-------------|--------|
| 1 | Decompose | chat | `query.md` |
| 1.5 | Chapter partition | chat (chỉ dissertation) | chapters |
| 2 | Width sweep | mcp_smart_search + mcp_smart_fetch + academic API | raw notes |
| 3 | Contradiction graph | execute_code | `contra.json` |
| 4 | Loci analysis | delegate_task (2 analyst) | loci |
| 5 | Depth investigation | delegate_task (K investigator) | interim notes |
| 6 | Cross-locus reconcile | chat | `comparisons.md` |
| 7 | Source tensions | execute_code | `tensions.json` |
| 8 | Corpus critic | delegate_task | gap-fetch list |
| 9 | Evidence digest | chat | `digest.md` |
| 10 | Triple draft | delegate_task (3 orchestrator) | 3 drafts |
| 11 | Synthesize | delegate_task (synthesizer) | `report.md` |
| 12 | Critics | delegate_task (4 critic song song) | findings JSONs |
| 13 | Gap-fetch | mcp_smart_fetch bổ sung | thêm notes |
| 14 | Patcher | chat (surgical edit, KHÔNG viết lại) | `report v2` |
| 14.5 | Cite-check | `verify-parser-output` skill | cite-report PASS |
| 15 | Polish | chat (filler/hygiene) | `report v3` |
| 16 | Readability audit | delegate_task (recommender) | `final.md` |

## PROCEDURE — Bước 1–8 (Decompose → Corpus critic)

> Mỗi bước: in token `🔰 DR-STEP n/16`, làm, xong mới qua bước sau. Không batch.

### Bước 1 — Decompose
```
🔰 DR-STEP 1/16: Decompose
```
- Đọc câu hỏi Bố. Chốt **canonical query** (nguyên văn, không sửa ý Bố).
- Bẻ thành 3–5 **atomic items** (mục con độc lập).
- Lập **coverage matrix**: mỗi atomic item → cần loại nguồn nào (academic / news / official / blog).
- Tự phân loại tier: `light` (facts đơn giản) / `full` (tranh luận sâu, mặc định) / `dissertation` (chỉ nếu Bố bảo).
- Ghi `vault/_inbox/research/<slug>/query.md` (YAML frontmatter: original_prompt, tier, atomic_items, coverage_matrix).
- **Verified khi:** query.md tồn tại, có đủ 3 phần trên.

### Bước 1.5 — Chapter partition (CHỈ dissertation)
```
🔰 DR-STEP 1.5/16: Chapter partition (skip nếu không phải dissertation)
```
- Nếu Bố không gọi dissertation → **bỏ qua, in "SKIP"**, tới bước 2.
- Nếu có: nhóm atomic items thành 4–10 chapters. Bước 2–10 lặp per chapter.

### Bước 2 — Width sweep
```
🔰 DR-STEP 2/16: Width sweep
```
- Academic trước (API free): Semantic Scholar, arXiv, OpenAlex, PubMed — theo URL trong hyperresearch README.
- Web search đa góc: mỗi atomic item → 1 query, + 1 query **adversarial** ("criticism of X", "limitations of X").
- Dùng `mcp_smart_search` (limit 5–10/query) + `mcp_smart_fetch` cho top URL.
- Lưu raw notes vào `vault/_inbox/research/<slug>/raw/` (mỗi nguồn 1 file .md, ghi URL + date + tier).
- **Independence guard:** nếu 5 kết quả cùng 1 press release → chỉ tính 1 (xem source-ranking.md).
- **Verified khi:** có ≥ (số atomic item × 3) nguồn raw, mỗi file có URL.

### Bước 3 — Contradiction graph
```
🔰 DR-STEP 3/16: Contradiction graph
```
- Dùng `execute_code` (Python stdlib): đọc raw notes, cặp các mâu thuẫn (A nói X, B nói không-X).
- Cluster thành ranked contradictions (`contra.json`: {claim, source_for, source_against, strength}).
- **Verified khi:** contra.json hợp lệ JSON, có ≥1 cặp (nếu không có → ghi "no contradiction found", vẫn OK).

### Bước 4 — Loci analysis
```
🔰 DR-STEP 4/16: Loci analysis
```
- `delegate_task` spawn **2 loci-analyst** (concurrent=2, cùng context: raw + contra.json).
- Mỗi analyst trả về 1–8 **loci** (chủ đề sâu cần điều tra) + rationale + source budget.
- Gộp, dedupe → `loci.json`.
- **Verified khi:** loci.json có 2–8 loci, mỗi loci có rationale.

### Bước 5 — Depth investigation
```
🔰 DR-STEP 5/16: Depth investigation
```
- `delegate_task` spawn **K investigator** (K = số loci, tối đa 3 concurrent/wave).
- Mỗi investigator: đọc sâu loci được giao → 1 interim note có **committed position** (quan điểm rõ).
- Lưu `vault/_inbox/research/<slug>/interim/`.
- **Verified khi:** có K interim notes, mỗi note có committed position (không mơ hồ).

### Bước 6 — Cross-locus reconcile
```
🔰 DR-STEP 6/16: Cross-locus reconcile
```
- Chat (không delegate): đọc K interim notes, đối chiếu các committed positions.
- Viết `comparisons.md`: chỗ đồng thuận / chỗ xung đột giữa các loci.
- **Verified khi:** comparisons.md tồn tại, có 2 mục (agree / conflict).

### Bước 7 — Source tensions
```
🔰 DR-STEP 7/16: Source tensions
```
- `execute_code`: quét interim notes + comparisons → trích expert disagreements.
- Xuất `tensions.json`: {topic, expert_A_pos, expert_B_pos, source_links}.
- **Verified khi:** tensions.json hợp lệ, có danh sách disagreements.

### Bước 8 — Corpus critic
```
🔰 DR-STEP 8/16: Corpus critic
```
- `delegate_task` spawn 1 **corpus-critic**: câu hỏi "Nguồn nào có thể đảo ngược kết luận hiện tại?"
- Trả về gap-fetch list (những lỗ hổng cần fetch thêm).
- **Verified khi:** có gap-fetch list (có thể rỗng nếu corpus đủ).

---

## PROCEDURE — Bước 9–16 (Digest → Readability)

> Tiếp nối Bước 1–8. Vẫn in token mỗi bước.

### Bước 9 — Evidence digest
```
🔰 DR-STEP 9/16: Evidence digest
```
- Chat: đọc interim notes + comparisons + tensions.
- Trích **top claims** + **verbatim quotes** (nguyên văn có dấu ngoặc kép) → `digest.md`.
- Mỗi claim phải gắn ≥1 source link.
- **Verified khi:** digest.md có ≥3 claims, mỗi claim có quote + link.

### Bước 10 — Triple draft
```
🔰 DR-STEP 10/16: Triple draft
```
- `delegate_task` spawn **3 draft-orchestrator** (concurrent=3), mỗi ông 1 góc tiếp cận:
  - Góc A: theo thời gian (timeline)
  - Góc B: theo stakeholder (doanh nghiệp / người tiêu dùng / nhà nước)
  - Góc C: theo pros/cons
- Mỗi ông đọc `digest.md` + curated source list → viết 1 draft.
- Lưu `vault/_inbox/research/<slug>/drafts/{A,B,C}.md`.
- **Verified khi:** 3 file draft tồn tại, mỗi file là 1 bản thảo hoàn chỉnh.

### Bước 11 — Synthesize
```
🔰 DR-STEP 11/16: Synthesize
```
- `delegate_task` spawn **1 synthesizer**: đọc 3 drafts → viết `report.md` (bản tổng hợp, có outline).
- **Verified khi:** report.md tồn tại, có cấu trúc (tóm tắt + thân + kết luận).

### Bước 12 — Critics (4 song song)
```
🔰 DR-STEP 12/16: Critics (4 parallel)
```
- `delegate_task` spawn **4 critic** (concurrent=3/wave, 1 residual sau):
  1. **dialectic-critic**: counter-evidence draft bỏ sót
  2. **depth-critic**: chỗ nông cần đào sâu
  3. **width-critic**: góc độ corpus hỗ trợ nhưng draft bỏ qua
  4. **instruction-critic**: lệch so với atomic items của Bố
- Mỗi ông trả về findings JSON.
- **Verified khi:** 4 findings JSON nhận đủ.

### Bước 13 — Gap-fetch
```
🔰 DR-STEP 13/16: Gap-fetch
```
- Dùng `mcp_smart_fetch` fetch bổ sung các lỗ hổng critic chỉ ra (từ gap-fetch list bước 8 + findings bước 12).
- Thêm notes vào `raw/` + cập nhật digest nếu cần.
- **Verified khi:** các gap critic gọi tên đã được fetch hoặc xác nhận không có nguồn.

### Bước 14 — Patcher (surgical edit)
```
🔰 DR-STEP 14/16: Patcher (surgical edit — KHÔNG viết lại)
```
- Chat: áp dụng critic findings vào `report.md` bằng **surgical Edit hunks** (chỉ sửa từng đoạn).
- **CẤM viết lại toàn bộ** (patch-not-regenerate).
- **Verified khi:** report v2 có dấu vết sửa (diff vs v1), không mất section.

#### 🔍 Structural Integrity Check (sau patch, trước 14.5)
```
🔰 DR-STRUCT: đếm section v1 vs v2...
```
- **BẮT BUỘC** — đếm số heading `##` của `report v1` (trước patch) và `report v2` (sau patch).
- Dùng `execute_code` hoặc đếm thủ công qua `read_file`.
- In token kết quả:
  - Khớp → `✅ DR-STRUCT: N sections intact (v1=N, v2=N).`
  - Lệch → `⚠️ DR-STRUCT: v1=N sections, v2=M sections — chênh (N-M).`
- **Nếu lệch >1 section → DỪNG.** Kiểm tra lại patcher, tìm section bị mất/thêm, sửa trước khi qua 14.5.
- **Nếu lệch 1 section → cảnh báo nhưng vẫn qua** (có thể do merge 2 section ngắn hoặc tách 1 section dài — ghi chú lý do vào chat).

### Bước 14.5 — Cite-check (HARD GATE)
```
🔰 DR-STEP 14.5/16: Cite-check (verify-parser-output)
```
- **PHẢI** load skill `verify-parser-output` (`skill_view(name='verify-parser-output')`).
- Chạy gate: với mỗi `[N]` trong report → so với source link có support không.
- Mọi claim phải có source thật. Hallucinated quote / retracted = **hard block**.
- **Verified khi:** cite-report PASS. **KHÔNG PASS = DỪNG, KHÔNG write vault.**

### Bước 15 — Polish
```
🔰 DR-STEP 15/16: Polish
```
- Chat: filler pass + hygiene (bỏ lặp, sửa từ thừa) → `report v3`.
- **Verified khi:** report v3 sạch, không filler.

### Bước 16 — Readability audit
```
🔰 DR-STEP 16/16: Readability audit
```
- `delegate_task` spawn **1 readability-recommender**: đọc report v3 → JSON suggestions
  (nhịp đoạn, chuyển list/table).
- Chat áp dụng chọn lọc → `final.md`.
- **Verified khi:** final.md tồn tại, là bản hoàn chỉnh cuối.

### Hoàn tất — Write vault
- Move `final.md` → `vault/_inbox/research/<slug>.md` (file Bố đọc).
- Header block: nguyên văn prompt Bố + run metadata (tier, model, thời gian, số nguồn).
- **Verified khi:** file đích tồn tại, Bố mở Obsidian đọc được.

---

## Discipline wiring (KHÔNG bỏ qua)
- **Bước 14.5 (Cite-check):** PHẢI load skill `verify-parser-output` và chạy gate.
  Không PASS = KHÔNG được write vault. (SOUL §5 Verify Gate)
- **Mọi output non-trivial:** PHẢI emit token `🔰 SAFENET:` trước (core/safenet).
- **Patch-not-regenerate (bước 14):** chỉ sửa từng hunk (surgical edit), không viết lại từ đầu.
  Prompt patcher cấm "viết lại toàn bộ" — xem `references/prompts.md` (bước 14 không có template
  viết-lại, chỉ dùng chat surgical edit).
- **Source ranking + independence audit:** xem `references/source-ranking.md`.
- **Cite-check procedure:** xem `references/cite-check.md`.
- **Prompt templates (delegate):** xem `references/prompts.md`.
- **⚠️ VAULT_ROOT trong delegate_task (HARD RULE, học 2026-07-20):** subagent chạy trong
  terminal/context riêng, KHÔNG tự resolve `vault/...` (nó sẽ thành `C:\Users\khoans\vault\...`
  → sai). TRUYỀN ABSOLUTE PATH đầy đủ
  `C:\Users\khoans\Documents\Warren_OS_Local\vault\...` trong context của mọi delegate_task.
  Không dùng relative `vault/...`.

## Rate-limit mitigation (Nemotron free) — CHI TIẾT
- `delegate_task` kế thừa model của bố (parent = Nemotron free). KHÔNG spawn 17 agent cùng lúc.
- **Wave schedule:** mỗi wave tối đa **3 concurrent** (giới hạn hệ thống). Giữa wave: `sleep 5s`.
  - Bước 4: 2 loci-analyst (1 wave)
  - Bước 5: K investigator, chia wave 3/lần
  - Bước 10: 3 draft (1 wave)
  - Bước 11: 1 synthesizer
  - Bước 12: 4 critic → wave 1 (3 ông) + wave 2 (1 ông)
  - Bước 16: 1 recommender
- **Web search throttle:** giữa các `mcp_smart_search` call → `sleep 2s` để tránh ban OpenRouter/free.
- **Auto-fallback (MEDIUM):** nếu gặp lỗi 429 / rate-limit / ban:
  1. In `🔰 DR-FALLBACK: dropping to Medium (10-step)`.
  2. Bỏ bước 1.5/3/4/5/7/8 (các bước cluster/deep mà free yếu) → chỉ chạy 1→2→9→10→11→14→14.5→15→16.
  3. Báo Bố: "bị rate-limit, đã rớt Medium, báo cáo ít sâu hơn nhưng vẫn có cite-check."
  4. KHÔNG cố chạy Full tiếp tới khi hỏng.
- **Không bao giờ:** dùng model trả tiền, spawn >3 concurrent, bịa nguồn để lấp chỗ trống.

## Cách Bố dùng (cho dân non-IT)
1. **Trong chat Hermes:** gõ `/deep-research <câu hỏi của Bố>` rồi Enter.
   VD: `/deep-research tác động của AI tới chuỗi F&B Việt Nam 2026`
2. **Hoặc:** Bố chỉ cần nói "research sâu về X" → Hermes tự nhận diện gọi skill.
3. **Model:** trước khi chạy, đảm bảo đang dùng Nemotron free (Bố set trong Hermes, hoặc
   con chạy qua cron pin model). Nếu đang dùng model trả tiền → con sẽ nhắc Bố chuyển.
4. **Chờ:** ~30-60p (Medium) hoặc ~1h+ (Full 16-step). Bố xem token `🔰 DR-STEP n/16`
   để biết đang ở đâu.
5. **Kết quả:** file `vault/_inbox/research/<slug>.md` — Bố mở Obsidian đọc, có trích dẫn [N]
   link nguồn, qua cite-check.

> Không cần cài pip, không cần Claude Code. Skill nằm trong Hermes của Bố.

---

## Quick Capture (from `capture`, merged 2026-07-22)

> Knowledge capture from web/YouTube/social into `_growth/`. Lightweight single-URL ingest trước khi chạy deep-research.

### Behavior
- Accept link or pasted text.
- Parse source type and suggested tags.
- Create atomic `.md` in `vault/_growth/`.
- Update `_INDEX.md` after capture.
- Ask minimum clarifying questions when metadata is missing.

### Web Extraction (Hound MCP — Default)
- `mcp_smart_fetch` — Fetch any URL, auto anti-bot, PDF → markdown
- `mcp_smart_search` — Keyless web search (10 backends)
- Dùng Hound làm default. Firecrawl/web_extract fallback khi Hound không bypass được site.

### Legacy Fallback (defuddle / Firecrawl)
Khi cả Hound và `web_extract` fail:
```bash
npx -y defuddle parse <url> --md
```
- Dùng cho standard web pages / articles / docs (clean markdown).
- KHÔNG dùng cho `.md` URLs hoặc JS-heavy SPA (fallback to browser tool).
- Save to temp khi large: `npx -y defuddle parse <url> --md -o /tmp/extracted.md`.
