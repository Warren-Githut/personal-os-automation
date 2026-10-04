---
name: cron-job-ops
description: "Configure, troubleshoot, and repair Hermes cron jobs on the Windows host. Covers script-path resolution (profile/scripts/ only), jobs.json gitignore, Windows no-bash constraint, model/credit error diagnosis (HTTP 402 / missing credentials), no_agent vs agent cost, free-model + high-frequency rate-limit pitfalls, AND cross-profile cron discovery (cronjob list is profile-scoped). Class-level — applies to ANY Hermes profile on this Windows host (warren-profile / personal_profile / stock-profile)."
status: active
created: 2026-07-18
version: 1.0
triggers:
  - cron báo error / Script not found
  - sửa cron job / jobs.json
  - cron không chạy / silent fail
  - cron hết tiền / HTTP 402 / credential error
  - thêm script vào cron
  - "tại sao cron vỡ"
  - tìm cron ở profile khác / user hỏi cron mà cronjob list không thấy
  - audit tất cả cron qua nhiều profile / "cron nào đang chạy"
---

# cron-job-ops — Hermes Cron Operations (Windows host)

Skill này ghi lại behavior THỰC TẾ của Hermes cron resolver trên Windows host warren-profile (phát hiện 2026-07-18 khi fix 4 cron no_agent vỡ). Đọc trước khi sửa/bạn cron.

---

## 1. Cron resolver behavior (HARD FACT — không đoán)

Khi cron `no_agent: true` chạy, field `script` được resolver xử lý NHƯ SAU:

1. **Resolver LUÔN join `script` field vào `profile/scripts/`** (tức `~/.hermes/profiles/warren-profile/scripts/`).
   - Bare name `gen_today_and_send.py` → tìm `profile/scripts/gen_today_and_send.py` ✅
   - `skills/promo-eval/scripts/x.py` → tìm `profile/scripts/skills/promo-eval/scripts/x.py` ❌ (sai)
   - Absolute `C:/.../vault/.scripts/x.py` → ❌ bị guard chặn (xem #2)
2. **Guard CHẶN mọi path ngoài `profile/scripts/`.** Lỗi: `Script not found: ...\scripts\...` hoặc `Blocked: script path resolves outside the scripts directory (.../scripts): '...'`.
3. **`workdir` field KHÔNG ảnh hưởng chỗ resolver tìm script.** Nó chỉ set CWD cho script khi chạy.

→ **Quy tắc vàng:** Mọi no_agent script PHẢI nằm thẳng trong `profile/scripts/` + `script` field = **bare name**. Vault `vault/.scripts/` là SSOT gốc (git-tracked Warren repo), `profile/scripts/` = runtime copy (gitignored, force-add).

## 1.5 SSOT path = `vault/.scripts/` (dotfolder) — STALE-`vault/scripts/` TRAP

**HARD FACT (2026-07-23 COL cron rebuild):** Tất cả vault parser/cron scripts (`ops_col.py`, `col_*.py`, `col_queue_handler.py`…) sống ở **`vault/.scripts/`** (dotfolder — ẩn với Obsidian + `search_files` trên Windows MSYS). Thư mục `vault/scripts/` (KHÔNG dot) **KHÔNG TỒN TẠI** và là stale-path trap.

- ⚠️ **Trap symptom:** một script gọi `subprocess([..., "vault/scripts/ops_col.py", ...])` (thiếu dot) → FileNotFoundError tại runtime → append/bước cuối **BỊ CHẶN THẦM** (Warren "ok" không append được gì). Đây là BUG1 trong COL rebuild — đã fix thành `vault/.scripts/ops_col.py`.
- **Quy tắc:**
  1. SSOT = `vault/.scripts/`. KHÔNG BAO GIỜ viết `vault/scripts/` (không có dot).
  2. `search_files`/`read_file` **KHÔNG thấy** dotfolder trên MSYS → dùng `terminal` `ls`/`grep` để inspect. Đừng kết luận "file missing" từ `search_files` rỗng.
  3. Cron resolver chỉ đọc `profile/scripts/` → sau edit SSOT PHẢI re-copy vào `profile/scripts/` (md5 match).
     - **🚨 Post-edit sync check (2026-07-24):** SAU mỗi lần edit script trong `vault/.scripts/`, BẮT BUỘC copy updated file vào `profile/scripts/` và verify. Thiếu bước này = cron chạy STALE code cũ → bug production. Check: `diff vault/.scripts/<name>.py profile/scripts/<name>.py` → nếu khác → copy ngay.
  4. Hardcode `VAULT_ROOT` trong no_agent script (CWD = `profile/scripts/`, `parents[N]` resolve sai). **Submodule copy:** nếu script import 1 submodule (vd item_sales parser import `sqlclient` từ `VAULT_ROOT/.scripts/sqlserver_client`), PHẢI copy CẢ thư mục submodule đó vào `profile/scripts/` — resolver chỉ join bare script name, KHÔNG theo dõi subdir. Quên → `ModuleNotFoundError: No module named 'sqlclient'` tại runtime (bắt 2026-07-27 item-sales cron build).
- **Verify sau mọi đổi path SSOT:** `test -f vault/.scripts/ops_col.py && echo OK` + `test -f vault/scripts/ops_col.py && echo BUG || echo good`.
- → Xem `references/vault-scripts-ssot-path.md` cho full recipe + verify commands.

### 1.6 Subagent dotfolder-blind false negatives (2026-07-24)

**Pitfall:** Khi dùng `delegate_task` subagent review vault code, subagent dùng `search_files` để tìm file → không thấy dotfolder (`.scripts/`, `.parsers/`) → kết luận SAI "file không tồn tại" → báo CRITICAL giả.

**Real case:** Code-review subagent search `_send_telegram.py`, `gen_revenue_dashboard.py`, `revweek_test_fixture.json` — tất cả tồn tại trong `vault/.scripts/` và `vault/10_OPERATION_DATA/.parsers/`. `search_files` → 0 kết quả → subagent báo "pipeline cannot run, zero dependencies exist on disk." Thực tế cả 3 file đều có.

**Prevention:**
1. Khi dispatch subagent review vault → truyền explicit file paths trong `context` field (để subagent dùng `read_file`, không `search_files`)
2. Sau khi nhận subagent report → **verify mọi claim "file missing" bằng `terminal ls`** trước khi hành động
3. Subagent output = suggestion, không phải ground truth (SOUL §5 "Verify Gate")

## 2. Windows no-bash constraint

Host này chạy Windows, **KHÔNG có bash/WSL** trong cron context.
- `no_agent` cron chạy `.py` qua Python interpreter. Script `.sh` → lỗi `execvpe(/bin/bash) failed: No such file or directory`.
- Convert mọi `.sh` thành `.py` tương đương. Dùng `datetime.date.today()` thay `date +%Y-%m-%d` (lệnh `date` không có trên Windows).

## 3. jobs.json bị gitignore

`cron/jobs.json` nằm trong `.gitignore` của profile root → mặc định `git add` báo "ignored by one of your .gitignore files".
- Sửa cron config → **PHẢI `git add -f cron/jobs.json`** để track (tránh mất config nếu xóa profile).
- `profile/scripts/` cũng bị `.gitignore` line 70 → force-add các script runtime copy (`git add -f scripts/x.py`).

## 4. no_agent vs agent — model cost

| Loại cron | Dùng model? | Tiền |
|-----------|-------------|------|
| `no_agent: true` (script) | KHÔNG | Miễn phí (chạy Python) |
| `no_agent: false` (agent) | CÓ — mặc định **DeepSeek V4 Flash** (hoặc khai rõ `model`/`provider`) | Tốn credit theo model |

→ Muốn cron "free" → đảm bảo `no_agent: true`. Chỉ cron agent (vd `col-queue-watcher-v2`, Stock Broker) mới tốn model.

## 4.5 Debug thực tế — đọc error chi tiết

Khi cron báo `last_status: "error"`, field `last_error` trong `cronjob(action='list')` thường NGẮN (chỉ tóm tắt). **Raw error đầy đủ nằm trong file output:**
```
profile/cron/output/<job_id>/<YYYY-MM-DD_HH-MM-SS>.md
```
Mở file đó để thấy message thật (vd `Script not found: C:\...\scripts\gen_today_and_send.py`). Đừng chỉ đọc `last_error` — nó có thể thiếu context. Luôn kết hợp: (1) đọc file output, (2) `cronjob(action='run')` để tái hiện + xem `execution_success`/`execution_error` inline.

## 5. Symptom → Root Cause (error transcripts)

Xem `references/error-transcripts.md` cho raw text. Tóm tắt:

| Lỗi cron trả về | Nguyên nhân | Fix |
|-----------------|-------------|-----|
| `Script not found: ...\scripts\<name>.py` | File không có trong `profile/scripts/` (resolver đúng chỗ nhưng thiếu file) | Copy script vào `profile/scripts/` |
| `Blocked: script path resolves outside the scripts directory` | `script` field là absolute path hoặc `skills/...` prefix | Đổi về bare name, file đã ở `profile/scripts/` |
| `HTTP 402: ...requires more credits...` | Hết credit model | Đổi model free / nạp credit / đổi provider |
| `RuntimeError: No usable credentials found for provider 'opencode-zen'` | Sai tên provider (khai `opencode` nhưng config không có; đúng là `opencode-go`) + key bị comment trong `.env` | Sửa `provider` khớp config + bỏ comment key |
| `execvpe(/bin/bash) failed` | Cron chạy `.sh` trên Windows | Convert sang `.py` |
| `--heartbeat-check never fires` | **Dual-mode script trap** — 2 cron jobs share 1 script, mode-switch via CLI flag, but `no_agent` cron CANNOT pass CLI args → both jobs run same default mode | Tách script riêng cho mỗi mode, hoặc detect mode từ schedule (giờ/day), hoặc dùng env var |

### 5.1 Dual-mode script trap — one script, two cron jobs, broken mode-switch

**Pattern:** Bạn có 1 script `.py` với `--mode-a` / `--mode-b` flag (qua `argparse`). Tạo 2 cron `no_agent` jobs trỏ cùng script, job A định chạy mode A, job B chạy mode B. **Cả 2 sẽ chạy cùng default mode** vì Hermes `no_agent` cron **KHÔNG hỗ trợ CLI args** — script được gọi bare (`python3 script.py`), không có flag nào được truyền.

**Real case (revweek pipeline, 2026-07-24):**
- `revweek_telegram_intake.py` có `--heartbeat-check` flag (line 149)
- `revweek-telegram-intake` cron: poll mode (default) ✅
- `revweek-heartbeat` cron: lẽ ra chạy heartbeat mode với `--heartbeat-check` ❌
- **Kết quả:** heartbeat cron cũng vào poll mode → đọc offset → gọi getUpdates → empty → exit silent → **Warren KHÔNG BAO GIỜ nhận reminder**
- Không có lỗi, không crash — chỉ đơn giản là code path KHÔNG BAO GIỜ được gọi

**Các fix options (từ dễ nhất):**
1. **Tách script riêng** — `revweek_heartbeat.py` chỉ làm heartbeat logic (recommended, cleanest)
2. **Detect từ schedule** — dùng `datetime.now()` check giờ/day để tự switch mode (fragile, dễ sai khi test thủ công)
3. **Env var** — nếu Hermes hỗ trợ `env` field trong cron config, set `HEARTBEAT_CHECK=1` rồi script đọc `os.environ` (check docs)
4. **Đổi sang agent cron** — dùng prompt thay vì script, prompt mô tả mode (tốn token, vi phạm rule "all cron free")

1. `cronjob(action='list')` → tìm job_id + đọc `script` field.
2. Tìm source script thực tế: `find profile/skills + vault/.scripts` (dùng `terminal`+`find`, KHÔNG `search_files` — lỗi Windows MSYS).
3. Copy vào `profile/scripts/` (bare name). Nếu source là `.sh` → viết lại `.py`.
4. Sửa `script` field → bare name (qua `cronjob action='update'` hoặc patch `jobs.json`).
5. `cronjob(action='run', job_id=...)` → confirm `execution_success: true`.
6. `git add -f cron/jobs.json scripts/<name>` + commit + push.

## 7. Model/credit diagnosis cho agent cron

- Lỗi **HTTP 402** = hết credit (KHÔNG phải lỗi code). Kiểm tra provider có tiền không.
- Lỗi **"No usable credentials"** = TÊN PROVIDER SAI hoặc KEY BỊ COMMENT. Check `config.yaml` `providers:` block xem tên provider đúng (vd `opencode-go`, `deepseek`, `xai`), rồi đối chiếu `.env`.
- **Provider drift guard:** Hermes có thể auto-block job nếu global inference config drifted (provider/model đổi) → lỗi `Skipped to prevent unintended spend`. Pin lại: `cronjob action=update job_id=... provider=<p> model=<m>`.
- **no_agent=False + script misconfiguration:** Nếu job có `no_agent=False` (LLM-driven) VÀ có `script` field, đây là hybrid misconfiguration. Hermes cố chạy LLM agent + execute script cùng lúc → thường trigger provider drift guard. **Fix:** set `no_agent=True` nếu script là toàn bộ logic (đúng cho vault-scan/deterministic tasks — zero LLM cost), hoặc bỏ script field + chuyển logic vào prompt nếu cần LLM reasoning. Trường hợp field `no_agent` missing (implicit false) + `script` set → tương tự, thêm `no_agent: true` rõ ràng.
- **LITERAL pin call (agent cron):** `model` field NHẬN **OBJECT**, KHÔNG phải 2 string param rời. Đúng:
  ```python
  cronjob(action='update', job_id='<id>',
          model={'model': 'nvidia/nemotron-3-nano-30b-a3b:free',
                 'provider': 'openrouter'})
  ```
  Sai (sẽ báo lỗi param): `cronjob(action='update', job_id='<id>', model='nvidia/...', provider='openrouter')`.
- **HTTP 402 = unpinned PAID model, NOT broken script.** Reflex sai: đi sửa code/script. Đúng: pin nemotron-free → hết lỗi. Cùng 1 OpenRouter key NHƯNG `col-queue-watcher-v2` (pin free) vẫn `✅ ok` chứng minh key sống — chỉ là quota cạn do cron khác dùng paid global default. → Luôn check job đó pin free chưa trước khi đổ lỗi script.
- **Leftover cron ≠ auto-delete (Zone 🟠).** Cron "lạ"/leftover (vd 3 `Stock Broker *` route vào stock vault `10_PULSE/`, nghi từ stock-profile) → BÁO BỐ + đưa options (pin-free giữ / tắt), **KHÔNG tự tắt**. Warren 2026-07-18 chọn pin-free giữ.

## 7.5 Gán provider MỚI cho cron — discover + TEST trước khi assign (2026-07-26)

Khi Bố yêu cầu đổi cron sang 1 provider CHƯA từng dùng (vd Qwen Cloud), làm đúng quy trình để cron KHÔNG chết silent mỗi tick:

**B1 — Tìm tên provider ĐÚNG** (không đoán):
- Providers được cache ở `provider_models_cache.json` (profile root). Đọc bằng `read_file` hoặc `python3` (KHÔNG `search_files` — MSYS quirk, xem §10/§14).
  - ⚠️ **SHAPE caution (2026-07-27):** cache JSON top-level có thể KHÔNG phải flat `{provider: {models:[...]}}`. Naive `for k,v in d.items(): v['models']` → `'str' object has no attribute 'get'`. Trước iterate: `print(type(d), (list(d)[:3] if isinstance(d,dict) else d[:3]))` để biết shape. HOẶC đơn giản hơn: đọc thẳng `config.yaml` `providers.<name>.base_url` confirm endpoint (vd `deepseek` → `https://api.deepseek.com`). Không cần cache JSON để confirm provider chính hãng.
- Key cấp 1 = tên provider Hermes dùng (vd `alibaba`, `alibaba-coding-plan`, `openrouter`, `deepseek`). Model nằm trong `models:` list của key đó.
- Ví dụ thực tế (2026-07-26): Qwen Cloud = provider key **`alibaba`** (dùng `DASHSCOPE_API_KEY` đã có trong `.env`), model IDs `qwen3.7-max` (mạnh nhất) + `qwen3.7-plus` (nhẹ). KHÔNG phải `qwen`/`qwen-oauth` (OAuth variant KHÔNG nằm trong cache model list — chỉ hiện trong `.env` comment).

**B2 — Kiểm tra key/env tồn tại**: grep `.env` cho `DASHSCOPE_API_KEY` (set) + `HERMES_QWEN_BASE_URL` (set). Nếu key bị comment → bỏ comment trước.

**B3 — TEST kết nối TRƯỚC khi gán vào cron** (bắt buộc — tránh cron chết mỗi tick):
```bash
hermes chat -q "Reply with exactly: QWEN_OK" --provider alibaba -m qwen3.7-max > /tmp/test.log 2>&1
cat /tmp/test.log   # tìm "QWEN_OK" trong block ╭─ ⚕ Hermes ─╮
```
- Thấy reply đúng → provider sống → an toàn gán.
- Lỗi (auth/404) → sửa provider/key TRƯỚC, KHÔNG gán (cron sẽ fail liên tục).

**🔴 GC event UPDATE KHÔNG TỒN TẠI — dùng delete+create (2026-07-27 google-review fallback):**
`google_api.py calendar` CHỈ hỗ trợ `{list, create, delete}` — **KHÔNG có `update`**. Khi cần sửa 1 event đã có (vd đổi description):
1. `calendar list` → grep event id cũ. NẾU không thấy (grep rỗng) → event đã mất/sai id → bỏ qua update.
2. KHÔNG thể `update` → flow đúng = `calendar delete <old_id>` (nếu tồn tại) + `calendar create` event mới với description đầy đủ.
3. Create recurrence: `--recurrence "FREQ=WEEKLY;BYDAY=TU"` (TU=Thứ 3; MO=Thứ 2). Start/end ISO `+07:00`.
4. **Verify persisted (§7.5):** `calendar list` tuần NÀY (assert start đúng giờ) + tuần SAU (assert lặp lại = RRULE lưu). `list` JSON KHÔNG show field `recurrence` → phải assert bằng sự lặp lại.
5. Ghi event id MỚI vào handoff/CONTEXT (event cũ vứt).
- ⚠️ BỐ rule: GC = dùng `google_api.py` trực tiếp, KHÔNG re-auth/custom script. Token PRODUCTION persist → không hết hạn.
- Real case: google-review fallback event `i12smj859vt88ilapfocvtpn4c` không có trong `list` + script không có `update` → con tạo mới `bpjmsmr4g39cg80udoh552qcgg` (T2 11:00).
- **🔴 DeepSeek reasoning model — empty content trên HTTP 200 (2026-07-27 GrabFood cron):** Khi test `deepseek-v4-flash` (hoặc bất kỳ reasoning model) bằng 1 chat completion call, NẾU `max_tokens` quá nhỏ (vd 20) → response STATUS vẫn 200 NHƯNG `choices[0].message.content` = `''` (rỗng) vì model tiêu `reasoning_tokens` (vd 23) trước khi sinh content. **Fix test:** set `max_tokens` >= 50 + `temperature` bình thường, assert `content` không rỗng + `finish_reason=='stop'`. Đừng kết luận 'key lỗi' từ content rỗng — check `usage.completion_tokens_details.reasoning_tokens` trước. Recipe: `references/google-calendar-event-pitfalls.md` §DeepSeek.
- **🔴 DeepSeek key INVALID signal — "Authentication Fails (governor)" (2026-07-27 weekly-revenue-sql):** Khi test key chính hãng `https://api.deepseek.com` trả về `Authentication Fails (governor)` (HTTP 401) → key KHÔNG valid. ĐỪNG switch `base_url` sang official DeepSeek (Bố rule: "nếu key valid → chạy được: approved" → key lỗi = chưa approved). Giữ provider cũ (vd openrouter) cho tới khi 1 key MỚI trả `GET /v1/models` → 200. Đây là signal确定性 — không retry key cũ, báo Bố cấp key mới. (Khác với empty-content-on-200: đó là max_tokens nhỏ, key VẪN sống; "Authentication Fails" = key CHẾT.)
- **🔴 GC fallback event — recurrence/start drift (2026-07-27 GrabFood cron):** Tạo GC recurring qua `google_api.py calendar create --recurrence "FREQ=WEEKLY;BYDAY=MO"` → `calendar list` JSON **KHÔNG show field `recurrence`** (ngay cả khi đã lưu). Và start time có thể drift (truyền 07:00 nhưng ghi 11:00). **Verify bắt buộc:** (1) list tuần NÀY → assert `start` đúng giờ; (2) list tuần SAU → assert event xuất hiện lại (chứng tỏ RRULE lưu). Nếu sai → `calendar delete <id>` + create lại. Recipe đầy đủ: `references/google-calendar-event-pitfalls.md`. (Note: `google-workspace` là bundled skill — KHÔNG sửa nó; capture pitfall ở đây.)

**B4 — Gán qua cronjob tool** (per-job override KHÔNG cần sửa config.yaml):
```python
cronjob(action='update', job_id='<id>',
        model={'model': 'qwen3.7-max', 'provider': 'alibaba'})
```
- Per-job `model`+`provider` override HOẠT ĐỘNG ĐỘC LẬP với `config.yaml` `providers:` block. Bạn KHÔNG cần thêm provider vào config.yaml để gán cho 1 cron cụ thể (chỉ cần key tương ứng có trong `.env`). → Tránh sửa config.yaml (bị write-guard, xem §8.2).
- `no_agent=True` cron (script) → bỏ qua model hoàn toàn. Đổi model trên nó = vô nghĩa. Chỉ agent-cron (`no_agent:false`) mới dùng model.

**B5 — Verify:** `cronjob(action='list')` → job đó `model`/`provider` hiển thị đúng. Run 1 lần để confirm không lỗi 402/auth là tốt.

## 8. Free-model + high-frequency = rate limit

Model free (OpenRouter `:free`, `tencent/hy3:free`) có giới hạn request RẤT THẤP.
- Cron chạy mỗi 2 phút (30 lần/giờ) + free 550B model → **vài phút là dính rate limit, cron lỗi liên tục**.
- Khi dùng free model cho cron agent → **giảm frequency** (vd 2p → 15p) để không spam rate limit.
- Hoặc dùng model nhẹ free đã có sẵn (`tencent/hy3:free` = default profile) thay vì free 550B.

## 8.1 Warren hard rule: ALL crons MUST be free

Warren (2026-07-18) quy định: **mọi scheduled cron PHẢI chạy free model, KHÔNG dùng API trả tiền.**
- Chỉ sửa cron agent cần LLM → OpenRouter `:free` models. Không động cron no_agent (đã free) hay cron `hy3:free` (đã free).
- Free Nemotron nhẹ khuyên dùng: `nvidia/nemotron-3-nano-30b-a3b:free` (30B MoE, agentic tốt, rate limit thoải mái hơn 550B). 550B = `nvidia/nemotron-3-ultra-550b-a55b:free` (dễ bị ban hơn).
- Khi chuyển sang free + giảm frequency → dùng combo (15p + nano free) để ổn định nhất.

## 8.2 Enable OpenRouter provider (config.yaml WRITE-PROTECTED)

**config.yaml BỊ AGENT WRITE-GUARD CHẶN** — `patch`/`write_file` trực tiếp trả lỗi:
`Refusing to write to Hermes config file ... Agent cannot modify security-sensitive configuration.`
→ PHẢI dùng `hermes config set` (dot-path), KHÔNG sửa tay file.

Steps enable OpenRouter cho cron agent:
1. Check key có sẵn: `grep -i OPENROUTER .env` (warren-profile `.env` đã có `OPENROUTER_API_KEY` active, không bị comment).
2. Thêm provider block qua CLI:
   ```
   hermes config set "providers.openrouter.api_key_env" "OPENROUTER_API_KEY"
   hermes config set "providers.openrouter.base_url" "https://openrouter.ai/api/v1"
   ```
3. Verify: `python3 -c "import yaml; d=yaml.safe_load(open('config.yaml')); print(d['providers'])"` → phải có `'openrouter'`.
4. Sửa cron job: `provider: openrouter` + `model: nvidia/nemotron-3-nano-30b-a3b:free` + schedule 2m→15m.
5. `cronjob(action='run')` → assert `execution_success: true`.
6. `git add -f cron/jobs.json config.yaml` + commit + push (config.yaml chưa bị gitignore → add thường; jobs.json vẫn -f).

⚠️ Config.yaml KHÔNG nằm trong `.gitignore` → `git add config.yaml` (không cần `-f`). Chỉ `cron/jobs.json` + `profile/scripts/` cần `-f`.

## 9. E2E verify gate (trước báo Bố xong)

- no_agent: `cronjob(action='run')` → assert `execution_success: true`.
- agent: chạy 1 lần → assert không lỗi 402/credential.
- Telegram send: chạy LEAF sender script trực tiếp (`python3 send_today_brief.py`), KHÔNG trigger orchestrator cron (có state-gate chỉ gửi 10:00/đầu ngày → off-schedule = silent skip). Xem `telegram-py-checklist` §3e.
- Commit + push cả profile repo (`warren-profile-root`) lẫn vault repo (`Warren_OS_Local`).

---

## 10. Cross-profile cron discovery (HARD FACT — 2026-07-18 session)

`cronjob(action='list')` ONLY returns jobs for the **active** profile (profile session hiện tại). Nếu Warren hỏi về 1 cron mà `cronjob list` KHÔNG hiện → cron đó nằm ở **profile khác**.

**Profiles trên host này:** `warren-profile` (chính, nhiều cron nhất), `personal_profile`, `stock-profile`.

**Audit TẤT CẢ cron xuyên profile:** `cronjob` tool không thấy cross-profile → phải đọc trực tiếp `jobs.json` của từng profile:
```bash
for p in warren-profile personal_profile stock-profile; do
  echo "=== $p ===";
  grep -o -i -E "telegram|sender|review|fetch" "/c/Users/khoans/AppData/Local/hermes/profiles/$p/cron/jobs.json" | sort | uniq -c;
done
```
Hoặc `read_file(".../profiles/<profile>/cron/jobs.json")` để đọc full.
> ⚠️ Dùng `terminal` `grep`/`ls`, **KHÔNG dùng `search_files`** — lỗi false-negative trên Windows MSYS (search_files trả rỗng dù file tồn tại). Đã ghi STOCK_MEMORY lesson 2026-07-17.

**jobs.json schema (mỗi profile):**
- Top: `{ "jobs": [ {job}, ... ] }`
- Mỗi job: `id`, `name`, `schedule`, `script`/`prompt`, `no_agent`, `enabled`, `state`, `next_run_at`, `last_run_at`, `last_status`, `last_error`, `completed` (số lần chạy), `deliver`.
- ⚠️ **Key là `id`, KHÔNG phải `job_id`.** Output `cronjob list` dùng `job_id`, nhưng JSON file dùng `id`. Đọc bằng python: `j['id']` (dùng `j['job_id']` → `KeyError`). Đã bắt lỗi 2026-07-23 khi patch prompt watcher.
- **`schedule` — 2 dạng:**
  - `kind: "cron"` → `{ "expr": "0 9 * * *", "display": "0 9 * * *" }` (cron expr)
  - `kind: "interval"` → `{ "minutes": 1, "display": "every 1m" }` (chạy MỖI N phút — hay dùng cho cặp watcher/sender)
  - → `"every 1m"` = interval `minutes:1`, **KHÔNG phải cron expr**. Đừng đọc nhầm thành hàng giờ/ngày.

**Chẩn đoán không cần chạy:** `last_status` (ok/error), `last_error` (ngắn — raw đầy đủ ở `cron/output/<job_id>/<ts>.md`), `completed` count, `next_run_at` đều có sẵn trong jobs.json / `cronjob list`.

**Pattern — watcher + sender pair:** Cron interval tần số cao thường đi cặp: `*_queue-watcher` (LLM tiền xử lý → ghi queue) + `*_telegram-sender` (no_agent, poll queue mỗi 1m, gửi). Cả 2 đều interval 1m. Giảm frequency của sender an toàn nếu watcher vẫn feed kịp.

⚠️ **DOC-VS-RUNTIME DRIFT TRAP (2026-07-23, review pipeline):** A skill's "Fix applied on DATE" note proves NOTHING. `ops-review` SKILL.md Step 8 says sender "MUST check BOTH arrays (pending[] + history[])" and this skill's old pitfall said "Fix applied 2026-07-02" — but the ACTUAL runtime script `profile/scripts/review_telegram_sender.py` (line 65) STILL only scanned `data.get("history", [])`. The fix was NEVER written to disk. Result: if the watcher (LLM) leaves an entry in `pending[]` after writing `approval_message`, the sender SKIPS it → review dies silent, Warren never sees it to approve. **Real fix (Warren approved 2026-07-23, 1 line, zero risk):** line 65 → `all_entries = data.get("pending", []) + data.get("history", [])`, loop over `all_entries`. After any cron fix: re-copy to `profile/scripts/`, run `cronjob(action='run', job_id='97c05046989a')` to E2E verify Telegram delivery.

**RULE — VERIFY DISK > TRUST DOC:** When auditing/fixing ANY cron, ALWAYS read the actual runtime script on disk (`profile/scripts/` or `vault/.scripts/`) and CONFIRM the fix is present. Do NOT trust a skill's "Fix applied on DATE" line — it may be docs-only. A "fix applied" claim is only valid when you see the code.

**Batch audit sequence Warren duyệt (2026-07-18):** (1) đổi schedule dày → 30m TRƯỚC, (2) SAU ĐÓ investigate error → đọc raw `cron/output/<id>/<ts>.md` → báo nguyên nhân, (3) chờ Bố quyết sửa/tắt → mới `run`-test. KHÔNG investigate rồi tự sửa luôn (vượt Zone 🟢). Cụ thể: Warren lệnh đổi 3 sender/watcher → 30m (làm ngay), rồi mới bảo "để con check kỹ từng cái error trước rồi báo Bố".

→ Xem `references/cross-profile-discovery.md` cho schema đầy đủ + recipe.

## 11. Silent-cron false-dead pitfall (2026-07-18 frameworks-weekly)

Warren nhìn `last_updated` trong frontmatter Frameworks.md = 2026-07-05 → tưởng cron `frameworks-weekly` "dừng từ 5/7". Thực tế cron VẪN CHẠY (last run 07-12, status ok) — script chỉ append entry, QUÊN sửa frontmatter, VÀ silent exit khi không có trigger → không gửi Telegram → Bố tưởng chết.

**3 gotcha khi Bố hỏi "cron còn chạy không":**
1. **Frontmatter lag** — script ghi data nhưng không bump `last_updated` → ngày trong frontmatter LỖI THỜI. Luôn check (a) entry mới nhất trong body file, (b) `cron/output/<job_id>/` run logs, (c) `cronjob list` `last_run_at`.
2. **Silent no-change exit** — no_agent script `return` sớm khi không có trigger → stdout rỗng → không gửi Telegram. Bố thấy im lặng = tưởng cron chết.
3. **User says "đã xóa X từ lâu" → verify FS trước** — Bố từng bảo "đã xóa mem0 lâu rồi" nhưng `mem0.json` + `mem0_faiss/` + 4 scripts VẪN CÒN. Trước khi xóa "lại" hoặc kết luận, luôn `ls`/`find` xác nhận thực tế (search_files false-negative trên MSYS → dùng terminal).

**Fix pattern (áp dụng khi vá no_agent script):** mọi lần chạy (kể cả silent) PHẢI: (a) ghi 1 dòng vào `<script>.log`, (b) bump frontmatter `last_updated`, (c) `print()` 1 dòng `[ALIVE]` để cron bắn Telegram tóm tắt ngay cả khi không có trigger. Đã vá `frameworks_cron.py` (§8.1 pin nemotron + pattern này).

**Verify "cron alive" không cần chạy:** `cronjob list` → `last_run_at` + `last_status`; mở `cron/output/<job_id>/*.md` xem có file run gần nhất không.

## 11.6 Cron chỉ chạy KHI Hermes Desktop app SỐNG (2026-07-18 vault-consistency session)

**HARD FACT — verify trên disk, không đoán:** Hermes cron scheduler sống BÊN TRONG process `Hermes.exe` (Desktop app). Nó **KHÔNG** phải Windows Service, **KHÔNG** có Windows Scheduled Task, **KHÔNG** auto-start khi bật máy (không có registry Run key).

→ **Hệ quả (durable pitfall, không phải env-error):**
- Bố **tắt máy / tắt app** = process chết = mọi cron (`no_agent` lẫn agent) **bị SKIP hoàn toàn** trong khoảng đó.
- Cron **KHÔNG bù lại** (missed run không được replay). Nó chỉ chạy lại từ schedule tiếp theo (vd `0 10 * * *` → đợi 10:00 đêm NÀY / sáng NÀY).
- Máy **sleep/hibernate** (không tắt hẳn) → timer thường pause → cũng có thể lỡ.
- Không có data hỏng, không crash vault — chỉ là **1 đêm không quét / không báo cáo**.

**Quy tắc scheduling cho warren-profile:**
1. **Đặt giờ cron vào khung BỐ ĐÃ MỞ MÁY** (vd 09:00–22:00), tránh giờ Bố thường tắt máy (đêm sâu). Vault-consistency原本 `0 2 * * *` → Bố đổi sang `0 10 * * *` vì 02:00 dễ bị tắt máy miss.
2. **Luôn có FALLBACK thủ công** nếu cron miss:
   - Tạo **Google Calendar recurring event** nhắc Bố chạy tay, description ghi sẵn copy-paste command. **CLI `google_api.py calendar create` ĐÃ hỗ trợ `--recurrence` (proven 2026-07-27 item-sales fallback — event T2 13:00 tạo + list verify được RRULE lưu):** chạy `python google_api.py calendar create --summary "..." --start "2026-07-27T13:00:00+07:00" --end "2026-07-27T14:00:00+07:00" --recurrence "RRULE:FREQ=WEEKLY;BYDAY=MO;BYHOUR=13;BYMINUTE=0" --description "$(cat _gc_desc.txt)"`. Timezone Asia/Ho_Chi_Minh. MSYS: raw `C:/Users/...` không qua `/c/`. Template description chuẩn: `references/gc_cron_fallback_template.md`.
   - **Vẫn MUST verify recurrence persisted (§7.5):** `calendar list` tuần NÀY (assert `start` đúng giờ) + tuần SAU (assert event lặp lại = RRULE thực sự lưu). Chỉ list tuần này là CHƯA đủ — `calendar list` JSON KHÔNG show field `recurrence` nên phải assert bằng sự lặp lại.
   - Hoặc Bố bảo Hermes "chạy <tên cron>" → con chạy script tay.
3. **Không dựa vào cron cho việc BẮT BUỘC phải có mỗi ngày** nếu Bố hay tắt máy — kết hợp cron + GC nhắc + Telegram báo cáo.

**Verify "cron có chạy đúng giờ không":** `cronjob list` → `next_run_at` + `last_run_at`. Nếu `last_run_at` cũ hơn 24h mà schedule là daily → máy đã tắt qua giờ đó.

## 11.5 No-agent vault-scan script pattern (2026-07-18 consistency cron)

Khi viết no_agent script quét vault (orphan / SSOT-conflict / gap scanner), áp dụng pattern này để an toàn + đúng triết lý Warren:

1. **`--dry-run` flag MẶC ĐỊNH an toàn.** Script luôn hỗ trợ `--dry-run` (print kết quả, KHÔNG gửi Telegram, KHÔNG commit). Dùng để verify thủ công không spam Bố. Production cron gọi KHÔNG có flag → gửi thật.
2. **Telegram = best-effort, NEVER crash.** Wrap `send_telegram()` trong try/except → trả `{"ok":False}` nếu fail (token/hết hạn). Log vẫn ghi đầy đủ dù TG fail. Import qua `sys.path.insert(0, PROFILE_SCRIPTS); from _send_telegram import send_telegram`.
3. **Quét orphan PHẢI exclude folder hệ thống.** `VAULT_ROOT.rglob("*")` sẽ bắt cả `.scripts/`, `.archives/`, `_archives/`, `.accumulation/`, `_assets/`, `__pycache__`, `.git`. Whitelist `EXCLUDE_DIRS` + skip `rel.parts[0].startswith(".")` → chỉ báo orphan ở **user-facing vault data** (10_OPERATION_DATA, wiki, _cases...). Nếu không exclude → false-positive ồn ào.
4. **VAULT_ROOT từ env, fallback hardcode.** `VAULT_ROOT = Path(os.environ.get("VAULT_ROOT", r"C:/Users/khoans/Documents/Warren_OS_Local/vault"))`. KHÔNG hardcode sâu trong logic (tránh drift trap 07-15).
5. **0 token, 0 external dep.** Chỉ stdlib (`re`, `json`, `pathlib`, `subprocess`, `datetime`). Không gọi LLM, không GSheet live (dùng cache local `vault/.accumulation/*.json` cho pair CPH).
6. **Log newest-on-top + machine state.** Ghi `CONSISTENCY_LOG.md` (prepend block, mỗi entry có `id:` + `status: open`). State file ẩn `vault/.scripts/.consistency_state.json` lưu `resolved_ids` để không báo lại entry Bố đã ignore. Script KHÔNG bao giờ tự sửa vault (zone 🔴) — chỉ phát hiện + ghi log.
7. **Heartbeat MỖI lần chạy (KHÔNG silent-when-clean).** Warren rule: *mọi cron tuyệt đối ko silent*. Đổi `if not findings.has(): print("OK: no issues"); return` → gửi 1 Telegram plain-text heartbeat: clean = `✅ sạch (0 findings)`, có findings = grouped 🔴🟡🟢 bullets. Dùng `send_telegram_plain()` (NO `parse_mode`) — vault filenames có `_` → Markdown parse 400 (xem `telegram-py-checklist` Pitfall 2). Cron `deliver` set `local` (KHÔNG `all`) để tránh double-send (script tự gửi + scheduler push stdout = 2 tin). Kết quả = đúng 1 tin/ngày, never silent.

→ Xem `references/no-agent-scan-pattern.md` cho skeleton script đầy đủ (copy-paste base cho mọi scan cron tương lai).

## 11.8 Silent-failure code anti-pattern — swallow-then-default (2026-07-25)

**HARD RULE cho mọi no_agent script viết/chữa trong `vault/.scripts/`:**

1. **Exception nuốt → return default/empty = BUG.** Pattern SAI:
   ```python
   except Exception:
       return []   # hoặc return None, return 0, pass
   ```
   → caller coi như "không có data" → silent no-op hoặc báo sai. Con từng mắc: `col_telegram_intake.py` `_get_updates()` nuốt → `return []` → `main()` silent no-op vĩnh viễn khi token hết hạn/mạng chết (job 16d81e801a39).
   → ĐÚNG: `except Exception as e: print(...); sys.exit(1)` (fail cứng) HOẶC trả sentinel phân biệt được: `None` = thất bại (fail), `[]` = thật sự rỗng (no-op OK). Caller PHẢI `if x is None: sys.exit(1)`.

2. **State corrupt → KHÔNG auto-reset im lặng.** Pattern SAI:
   ```python
   except (json.JSONDecodeError, OSError):
       state = DEFAULT.copy(); save_state(state); return state  # reset 0, exit 0
   ```
   → report in "0%" sai sự thật, không alert. Con từng mắc: `quota.py` `load_state()` (job d235537ac561 Model Router Daily Report) → daily report báo "0% Pro" sai.
   → ĐÚNG: `except ... as e: print(ERROR); sys.exit(1)` — để cron báo failed, sửa thủ công.

3. **Phân biệt rõ 3 trạng thái:** `None` = thất bại (fail signal) · `[]` = không có mới (no-op hợp lệ) · `0` = giá trị hợp lệ (KHÔNG auto-doán từ corrupt). Mixing chúng = silent bug.

→ 2 real cases + fix pattern: `references/cron-verifier-gate-audit.md` (grep recipe + transcripts).

## 11.9 Audit procedure — TÌM silent-failure bugs (2026-07-25, reusable; extended 2026-07-29)

Khi Bố yêu cầu "audit cron thiếu verifier / silent-failure", đừng chỉ đọc source tự kết luận. Áp dụng quy trình này (đóng được 2 bugs thực: quota.py job d235537ac561, col_telegram_intake.py job 16d81e801a39):

**B0 — Function-reference cross-check (2026-07-29):** Catch `NameError` bugs where a function is called but never defined in the same file — the function exists in a sibling script (copy source) but was dropped during copy-paste. Run BEFORE other checks (cheap, catches entire-class failures):

```bash
# Scan mọi no_agent script: compare call vs def count cho mỗi hàm
for f in vault/.scripts/*.py; do
  for fn in _token _get_updates _allowed_users _send_telegram _today_already_logged; do
    calls=$(grep -cP "[^a-z_]$fn\(" "$f" 2>/dev/null || echo 0)
    defs=$(grep -cP "^def $fn\(" "$f" 2>/dev/null || echo 0)
    [ "$calls" -gt "$defs" ] && echo "🔴 $f: $fn called $calls but defined $defs times"
  done
done
```

**Real bug (2026-07-29):** `col_telegram_intake.py:102` calls `_token()` but `def _token()` is in `hourly_regen_commit_watcher.py` + `revweek_commit_watcher.py` — NOT in `col_telegram_intake.py`. Copy-paste dropped the function block. Result: `NameError` every 30 min → cron `last_status=error` from file creation date (28/07). Grep `except: pass` (B1) wouldn't catch this — only B0 does.

**Prevention:** After creating/modifying any no_agent script, run `grep -cP '^def _(token|get_updates|send_telegram|today_already_logged|allowed_users)' <file>` — assert ≥1 match if those calls exist.

**B1 — Grep swallow patterns toàn bộ no_agent scripts:**
```bash
cd vault/.scripts && grep -rnE "except.*:\s*(return \[\]|return None|return 0|pass)" *.py
cd profile/scripts && grep -rnE "except.*:\s*(return \[\]|return None|return 0|pass)" *.py
```
Mọi hit = candidate silent-failure. Đọc từng cái: caller có phân biệt fail vs empty không? (§1.6: truyền path trực tiếp cho subagent, KHÔNG để nó search_files dotfolder.)

**B2 — Phân biệt 3 trạng thái tại caller (§11.8.3):** `None`=fail, `[]`=rỗng hợp lệ, `0`=giá trị. Nếu caller làm `if not updates: return` mà `updates` có thể là `None` (fail) → BUG (fail bị coi là no-op).

**B3 — Spawn reviewer-node ĐỘC LẬP (BẮT BUỘC, A10):**
- Self-audit LUÔN bỏ sót blind spot cùng class với author. Session này self-audit gắn "assume ok" cho `col-telegram-intake` → critic bắt được: (a) `ok:false` HTTP 200 bị nuốt thành `[]` (y hệt bug cũ), (b) `quota.py` thiếu-key JSON vẫn nuốt câm → nổ ở chỗ khác (KeyError).
- Dispatch `delegate_task` (role leaf) với context = file paths + grep evidence, yêu cầu: verify exit-code behavior, tìm blind spot (None-vs-[]混淆, ok:false, schema-missing), check circular/tautological. Critic PHẢI đọc file trên disk (truyền path, không để nó search_files — §1.6).

**B4 — Empirical exit-code test (KHÔNG claim done khi chưa chạy):**
- Corrupt input → assert `exit 1` (vd `echo "{bad" > state.json && python script.py; echo $?` phải =1)
- Normal → assert `exit 0`
- Missing-key JSON → assert `exit 1` (schema validate, không nuốt câm)
- Recovery path (vd `reset` action) → assert chạy được ngay cả trên file corrupt (bypass load_state)

**B5 — Patch + re-verify + critic vòng 2:** Sau sửa, chạy B4 lại. Nếu critic vòng 1 bắt blind spot → sửa tiếp → critic vòng 2 confirm. Rồi mới archive (`_archives/skills/`, §SOUL 5.2) + commit + push.

→ Quy trình này: self-audit 1 mình = insufficient cho silent-failure class. 2 vòng critic là chi phí bắt buộc, không phải over-engineering.

## 11.7 "No Telegram received" ≠ "cron missed" — first-principle diagnosis + never-silent fix

**HARD FACT (2026-07-19 vault-consistency session):** Khi Bố báo "không nhận TG từ cron X lúc Y" → đừng vội kết luận máy tắt/hibernate. Chạy `cronjob list`, check job đó:
- `last_run_at` = đúng giờ đó? `last_status` = `ok`? → **cron ĐÃ chạy**, máy KHÔNG tắt.
- Nguyên nhân "không nhận TG" thường là (1) script chỉ gửi KHI có finding (`if not findings: return` → silent) + (2) `deliver: local` (không đẩy Telegram kênh Bố).

**Warren rule vi phạm:** *"mọi cron deliver=all, tuyệt đối ko silent"* (WARREN_MEMORY §Preferences). Silent-when-clean + deliver:local = Bố thấy im lặng = tưởng miss.

**FIX pattern (áp dụng vá no_agent cron):**
1. Script tự gửi **heartbeat Telegram MỖI lần chạy** (clean = `✅ sạch`, findings = `🔴/🟡`). Dùng `send_telegram_plain()` (plain text, NO `parse_mode`) — xem `telegram-py-checklist` Pitfall 2 (vault filenames có `_` → Markdown 400).
2. Set cron `deliver: local` (KHÔNG `all`) để tránh **DOUBLE send**: scheduler cũng push stdout → 2 tin trùng vào finding days.
3. Kết quả = đúng **1 tin/ngày**, never silent, không bao giờ tưởng miss.

**Chống chỉ định:** ĐỪNG combo `deliver: all` + script tự gửi (nhân đôi tin). Nếu muốn `deliver: all`, script PHẢI silent-when-clean (nhưng vậy vi phạm "never silent" → Bố vẫn tưởng miss). → Luôn chọn pattern (1)+(2).

### 11.7b Agent-cron `[SILENT]` + double-send traps (2026-07-27 GrabFood cron)

Khi build **AGENT cron** (`no_agent:false`), scheduler tự inject 2 rule vào prompt mà agent phải override — nếu không sẽ hỏng im lặng:

**Trap A — System-injected `[SILENT]` suppresses your ONLY message.**
Mọi agent-cron prompt bị prepend:
> "SILENT: If there is genuinely nothing new to report, respond with exactly '[SILENT]' (nothing else) to suppress delivery."

Nếu final response = `[SILENT]` → scheduler suppress stdout delivery. Trên SKIP/clean run mà bạn return `[SILENT]` → tin nhắn tự-gửi (heartbeat) là tin DUY NHẤT → bị suppress → Bố KHÔNG thấy GÌ (vi phạm "never silent" §11.7).
- **FIX:** trong prompt ghi rõ: *"KHÔNG bao giờ trả lời `[SILENT]` — luôn in text bình thường làm final response (vì ta tự gửi Telegram / cần heartbeat)."*

**Trap B — `deliver:all` + self-send = DOUBLE Telegram.**
`deliver:all` fan stdout ra mọi home channel (Telegram + chat). Nếu agent CŨNG gọi `_send_telegram.py` → Bố nhận CÙNG nội dung 2 lần (1 từ self-send, 1 từ scheduler push).
- **FIX (chọn 1 đường delivery):**
  1. **`deliver:all` + print-only (recommended):** agent in report (XANH/ĐỎ/SKIP) làm final response; scheduler tự deliver Telegram + chat. KHÔNG self-send. Thoả "CẢ HAI Telegram + vault file", zero double.
  2. **`deliver:local` + self-send:** agent self-send qua `_send_telegram.py` (kiểm soát conditional/heartbeat); scheduler KHÔNG push stdout (`local`). Tránh double NHƯNG mất chat/vault-file copy trừ khi tự ghi.
- **Rule of thumb:** never both self-send AND `deliver:all`.
- **Verify:** sau tạo, `cronjob(action='run')` 1 lần → check Telegram Bố = ĐÚNG 1 tin/run, không 2.

**Real incident (2026-07-27):** `grabfood-weekly` cron build với `deliver:all` + prompt gọi `_send_telegram.py` → double-send + risk `[SILENT]` suppress trên skip. Caught in E2E review; fix = giữ `deliver:all`, bỏ self-send, in report + override `[SILENT]`.

**Verify trước báo xong:** chạy script tay 1 lần (clean branch E2E + findings branch E2E) → assert cả 2 gửi `TG_RESULT:OK`. Debug 400 bằng `telegram-py-checklist` repro.

→ Xem `telegram-py-checklist` references/telegram-markdown-400.md. `vault-ops-automation` (pinned) overlap cron Telegram routing.

## 11.10 No-agent git-pushing watcher — repo-corruption HARD rule (2026-07-27)

**CRITICAL LESSON (hourly-regen-commit-watcher session):** A no_agent watcher
that commits+pushes vault files MUST NOT run any git command that moves HEAD
(`git pull --rebase`, `git checkout`, `git reset --hard`, `git stash pop` that
re-applies across a HEAD move).

**What went wrong:** `git pull --rebase --autostash origin HEAD` inside the
watcher checked out an OLDER remote commit (remote had commits Bố pushed from
another machine). Result: ENTIRE working tree became untracked (`?? vault/`),
rebase conflict opened, `.git/index.lock` orphaned → repo broken, manual
`rebase --abort` + `reset --hard <known-good-SHA>` required to recover.

**Rule (NEVER auto-sync in a watcher):**
1. Watcher does `git add <scoped files>` + `git commit` + `git push origin HEAD` ONLY.
2. If push is REJECTED (non-fast-forward) → send 🔴 TG, `sys.exit(1)`, STOP.
   DO NOT auto-`pull`/`rebase`. Bố resolves manually (pull on his machine).
3. NEVER `git reset --hard` / `git checkout` / `git stash` in watcher logic.
4. Guard: commit at most ONCE per ISO week (state file `last_committed_week`).
   Subsequent 30-min polls SKIP entirely → no repeated push attempts, no 409 spam.

**Why:** watcher runs unattended; any HEAD move on a repo with uncommitted
Bố-work destroys that work or untracks everything. Cost of a rejected push
(Bố pulls manually) << cost of a corrupted repo.

See `references/no-agent-git-watcher-pitfalls.md` for the full watcher anatomy
(unique trigger, red/green/ack pattern, commit-once guard, E2E test-harness safety).

## 12. Telegram getUpdates 409 Conflict — intake vs main bot (2026-07-24)

**Symptom:** `no_agent` intake script polls Telegram `getUpdates` and gets `HTTP Error 409: Conflict`. Retry không hết.

**Root cause:** Một process KHÁC đang long-poll cùng bot token (thường là main bot `LUsineWorkBot/launch_bot.py` hoặc aiogram-based bot). Telegram API chỉ cho phép **1** `getUpdates` connection per bot token tại 1 thời điểm.

**Real case (2026-07-24, revweek intake):**
- Main bot (`LUsineWorkBot/launch_bot.py`, PID 1388, `pythonw.exe`) long-polling 24/7
- Intake cron (`revweek_telegram_intake.py`) gọi `getUpdates?timeout=20` → 409 vì main bot đang giữ connection
- **Hệ quả kép:** Không chỉ conflict — main bot đã "nuốt" hết updates trước đó (getUpdates đánh dấu delivered), intake không bao giờ thấy ảnh Bố gửi

**Fix options (từ cleanest):**
1. **Dedicated bot token cho intake** — tạo bot Telegram riêng (`@lusine_revenue_bot`) chỉ nhận ảnh revenue. Intake dùng token riêng → không conflict với main bot. Bố gửi ảnh vào bot revenue thay vì bot chính.
2. **Tích hợp intake vào main bot** — sửa `launch_bot.py` để khi nhận caption `01_weekly_revenue` → tự download ảnh + gọi orchestrator (thay vì cron riêng). Ưu: 1 process, không conflict. Nhược: sửa code main bot (risk cao hơn).
3. **Tắt main bot tạm khi test** — kill main bot (PID), chạy intake tay, restart main bot. Chỉ dùng cho test thủ công, không phải solution production.
4. **Webhook thay polling** — 1 trong 2 process dùng webhook. Nhưng webhook cần public URL (ngrok/server) → phức tạp hơn polling.

**Current status (2026-07-24):** Option 3 (kill + re-send + restart) cho test. Chưa chọn solution production. **Recommend: Option 1** (dedicated bot) — đơn giản nhất, không đụng main bot, không cần public URL.

### 12.4 Option D — Queue-file pattern (RECOMMENDED, 2026-07-27 hourly-regen-commit-watcher)

**Bối cảnh:** Bố KHÔNG muốn tạo bot mới, cũng không muốn tắt main bot mỗi T2. → Cần cách giải 409 mà KHÔNG đụng connection TG.

**Pattern (không poll TG, không conflict):**
1. Main bot `LUsineWorkBot/telegram_bot.py` giữ connection (long-poll 24/7) — KHÔNG đổi.
2. Thêm **1 handler nhỏ** trong `handle_text()`: bắt trigger riêng (vd `"ok 09"`) → ghi vào **queue file** `.hourly_approval_queue.json` (không gọi getUpdates, chỉ `json.dump` append).
3. Watcher `no_agent` (`hourly_regen_commit_watcher.py`) chạy schedule `*/30 7-17 * * 1` → **ĐỌC queue file** (KHÔNG `getUpdates`) → nếu có trigger → commit+push 2 file → xóa entry đã xử lý.
4. Watcher vẫn gửi Telegram OUTBOUND (báo đỏ/xanh) qua `send_telegram_plain()` — outgoing OK, chỉ incoming poll mới conflict.

**Ưu điểm vs Option 1 (dedicated bot):**
- Không cần bot token mới, không cần Bố đổi thói quen (gõ "ok 09" vào bot chính).
- Zero 409 (watcher không bao giờ poll TG).
- Tách biệt: bot chỉ ghi file, watcher đọc file → debug dễ.

**So sánh 4 options:**
| Option | Tạo bot mới? | Tắt main bot? | 409? | Risk |
|--------|-------------|---------------|------|------|
| A tắt main bot T2 | Không | Có (tạm)) | Hết lúc tắt | Quên bật lại → bot chết |
| B bot riêng | Có | Không | Hết | Bố phải gõ đúng bot |
| C tích hợp vào bot | Không | Không | Hết | Gộp logic vào bot live |
| **D queue-file** | **Không** | **Không** | **Hết (watcher không poll)** | **Thấp — chỉ thêm handler, không đổi logic cũ** |

**Implementation note (bot handler):**
```python
# in telegram_bot.py, FIRST in handle_text() (before other handlers):
if _append_hourly_approval(message.from_user.id, text):
    await message.answer("✅ Nhận được 'OK 09' — đã ghi queue. Watcher sẽ commit+push.")
    return
# _append_hourly_approval(): if clean(text)=="ok 09" -> json.dump append to QUEUE_FILE
```

**Watcher read (no getUpdates):**
```python
def main():
    queue = json.loads(QUEUE_FILE.read_text()) if QUEUE_FILE.exists() else []
    pending = [e for e in queue if is_commit_trigger(e.get("text",""))]
    if not pending:
        return  # no-op, silent OK (no 409)
    # ... commit + push ...
    QUEUE_FILE.write_text("[]")  # consume
```

→ Xem `references/telegram-409-queue-file-pattern.md` cho full bot-handler + watcher skeleton (đã áp dụng thực tế 2026-07-27, E2E pass).

### 12.5 Xây watcher getUpdates MỚI — conflict tức thì + date-range động

**HARD lesson (2026-07-27, hourly-regen-commit-watcher):** Khi build 1 watcher `getUpdates` MỚI và chạy lần đầu → **409 Conflict NGAY LẬP TỨC** nếu main bot `LUsineWorkBot/launch_bot.py` đang long-poll cùng token (aiogram giữ connection 24/7). Cron B vừa tạo xong chạy thử là dính ngay → confirm §12 bằng evidence thực tế.

**Quy tắc build watcher mới:**
1. **Check conflict TRƯỚC deploy:** grep process nào đang poll token (launch_bot.py / telegram_bot.py). Nếu có → watcher MỚI SẼ 409.
2. **Resolution (production):** Dùng **dedicated bot token riêng** (Option 1 §12) — watcher poll token riêng, không đụng main bot. Test-only: kill main bot tạm rồi restart (Option 3).
3. **PRIVATE offset file:** Mỗi watcher PHẢI có offset file RIÊNG (vd `.hourly_regen_commit_offset.json`), KHÔNG share `.col_telegram_offset.json` của col_telegram_intake → tránh race nếu Bố chạy tay đè giờ. Schedule khống chế (col intake 9-11h, hourly watcher 12-17h T2 → không đụng giờ, NHƯNG offset riêng = safe tuyệt đối).
4. **Mojibake gate + never-silent + fail-cứng** (§3b, §11.8): no_agent script → ASCII print, heartbeat mỗi run, `getUpdates` fail → `sys.exit(1)` (KHÔNG nuốt thành []).

**🔴 HARDCODED DATE-RANGE TRAP (áp dụng MỌI scheduled regen script):**
Script regen mà **hardcode** `WEEKS = [W26, W27, W28, W29]` (hoặc bất kỳ week label cố định) → khi chạy bởi cron mỗi tuần → **regen y nguyên tuần cũ mãi, không bao giờ lấy W mới** → automation vô nghĩa (bắt đúng bug này 2026-07-27: `_regen_all_hourly.py` hardcode W26-W29, HANDOFF ghi "script KHÔNG đổi" nhưng M1 chỉ bảo duplicate constant, không bảo hardcode week → phải sửa thành dynamic).
→ **FIX:** Tính range ĐỘNG từ ngày chạy:
```python
import datetime
def compute_last_4_weeks(reference=None):
    if reference is None: reference = datetime.date.today()
    days_since_sun = (reference.weekday() + 1) % 7
    end = reference - datetime.timedelta(days=days_since_sun)  # last Sunday <= ref
    weeks = []
    for _ in range(4):
        start = end - datetime.timedelta(days=6)
        y, w, _ = start.isocalendar()
        weeks.append((f"{y}-W{w:02d}", start.isoformat(), end.isoformat()))
        end = start - datetime.timedelta(days=1)
    return weeks  # newest-first
```
ISO week ends Sunday; Monday reference → tuần vừa đóng = tuần trước. Label = `isocalendar()` (khớp `01_SSOT`/WARREN_MEMORY: week-label lệch hệ đã resolve W29=13/07).
→ E2E test pattern: `references/watcher-commit-e2e-test.md`.

**🔴 W30 INCIDENT CHECKLIST (2026-07-28, từ `_regen_all_hourly.py` overwrite W30):** Khi build/sửa MỌI cron regen/script ghi file log → BẮT BUỘC 3 bước:
- **C-A — Test trên COPY trước khi chạy thật.** Script ghi file qua `os.replace`/`open('w')` sẽ GHI ĐÈ TOÀN BỘ file → mất data tuần khác (W30 bị xóa vì list hardcode W26-W29). Luôn `cp` log thật → `/tmp` copy, redirect `LOG` path trong test copy, chạy, assert số block `## Wxx` không đổi trước khi đụng log thật.
- **C-B — Dynamic window (KHÔNG hardcode).** Thay vì `WEEKS=[W26,W27,W28,W29]`, đọc các `## 2026-Wxx` header ĐÃ CÓ từ log → regen hết (newest-first). Tuần mới (W31...) tự vào, không bao giờ bị xóa. Regex parse PHẢI có flag `re.M` (không có → `^` chỉ khớp đầu file → rớt vào fallback sai).
- **C-C — Verify sau force-run.** Đếm `grep -c '^## 2026-W' log.md` TRƯỚC và SAU chạy → assert không mất/thêm block. Incident này phát hiện precisely vì W30 count 1→0 sau cron chạy.

### 12.6 Pitfalls thực tế bắt thêm (2026-07-27 E2E watcher)

**P1 — Git push non-fast-forward reject (🔴 NEVER auto-rebase — repo-corruption trap).** Watcher `git commit` + `git push origin HEAD` → `! [rejected] HEAD -> master (non-fast-forward)` nếu Bố push từ máy khác hoặc session trước push.

> **🔴 CẤM TUYỆT ĐỐI `git pull --rebase` / `git stash` / `git checkout` / `git reset --hard` TRONG WATCHER.** Session 2026-07-27: watcher chạy `git pull --rebase --autostash origin HEAD` → checkout commit REMOTE CŨ HƠN local → **TOÀN BỘ working tree thành untracked (`?? vault/`)**, mở rebase conflict, orphan `.git/index.lock` → repo hỏng, phải `rebase --abort` + `reset --hard <known-good-SHA>` thủ công để recover. Chi phí recover >> chi phí 1 lần push bị reject.

→ **FIX (reject-safe):** watcher chỉ `add` + `commit` + `push`. Nếu push reject → gửi 🔴 TG "PUSH REJECTED" + `sys.exit(1)` + DỪNG. BỐ tự `git pull` trên máy rồi push. Pattern:
```python
def do_commit_push():
    _run_git(["add"] + COMMIT_FILES)
    if not _run_git(["diff", "--cached", "--name-only"]):
        return None
    _run_git(["commit", "-m", "weekly: hourly regen (auto via ok 09)"])
    try:
        _run_git(["push", "origin", "HEAD"])
    except RuntimeError as e:
        _tg_red(f"PUSH REJECTED: {str(e)[:120]}. Bo pull thu cong hoac push tay.")
        raise
    return _run_git(["rev-parse", "--short", "HEAD"])
```
→ Xem `references/no-agent-git-watcher-pitfalls.md` cho full corruption transcript + recovery + reject-safe skeleton.

**P2 — no_agent watcher import heavy parser module FAIL trong cron-mode.** Watcher import `compute_last_4_weeks` từ `_regen_all_hourly.py` → file đó `importlib` load `H` (hourly_cover_sql_parser, cần sqlclient/VPN) → exec dừng giữa chừng → `module has no attribute 'compute_last_4_weeks'`. → **FIX:** tính week label bằng **hàm local** (5 dòng, không import regen script):
```python
def compute_current_week_label():
    import datetime as _dt
    ref = _dt.date.today()
    days_since_sun = (ref.weekday() + 1) % 7
    last_sun = ref - _dt.timedelta(days=days_since_sun)
    y, w, _ = last_sun.isocalendar()
    return f"{y}-W{w:02d}"
```
(Giữ 1 bản copy local, duplicate 5 dòng chấp nhận được — tránh dependency nặng trong cron-mode.)

**P3 — Week-guard giảm 409 + tránh double-commit.** Watcher chạy `*/30 7-17 * * 1` = 20 lần/T2. Nếu main bot chiếm token → 20 lần 409. → **FIX:** state file `.hourly_regen_commit_state.json` lưu `last_committed_week`; mỗi lần chạy: nếu `last_committed_week == current_week` → **SKIP entire** (không poll, không 409); chỉ khi tuần CHƯA commit mới poll + sau commit lưu state → các lần lặp sau skip. Kết quả: tối đa 1-2 lần poll/T2 sau khi commit xong.

### 12.7 Monday-cron "just-closed week" = prev ISO week (W29≠W30 trap)

**HARD lesson (2026-07-27 item-sales cron):** Cron `0 9 * * 1` (T2 09:00) xử lý tuần VỪA ĐÓNG. Nhầm tưởng "tuần trước = W29" là SAI.

- `date(2026,7,27)` là **Thứ 2 = W31** (ISO: 07-27..08-02 = W31).
- `monday = ref - weekday()` = 07-27 (W31). `prev_monday = monday - 7d` = 07-20 = **W30** (20-26/07, tuần vừa đóng).
- W29 = 13-19/07 → đã đóng TỪ TRƯỚC, KHÔNG phải tuần cron xử lý.

→ Công thức đúng: `prev_monday = (ref - weekday_days) - 7 days`, rồi `isocalendar()`. Parser mặc định (`monday_of(today) - 7d`) cũng ra W30 — KHÔNG dùng `ref - 14` hay hardcode.
→ **TDD bắt kịp:** test viết sai `assert wk == "2026-W29"` → RED fail → sửa thành W30. Luôn test compute_run_week với ngày Thứ 2 cụ thể trước khi chạy thật.

### 12.8 Handoff design có thể STALE vs ANCHORS/WARREN_MEMORY (override rule)

**HARD lesson (2026-07-27 item-sales cron):** Handoff viết TRƯỚC (27/07 sáng) design "cron tự `git commit+push`". NHƯNG WARREN_MEMORY §Preferences + §15 (BỐ duyệt 27/07, SAU handoff) quy định **mọi cron KHÔNG tự push — BỐ gõ trigger mới commit**.

→ Khi build từ 1 handoff/plan cũ: LUÔN re-check ANCHORS + WARREN_MEMORY hiện tại cho rule MỚI hơn. Nếu conflict → áp dụng rule MỚI (override), KHÔNG theo handoff cũ mù quáng. Thiết kế đúng: cron chạy parser+verify → báo xanh/đỏ Telegram → in "🔔 gõ 'ok 11' để GG commit push" → BỐ gõ trigger → GG push.

## 13. Circuit Breaker Pattern (steal from auto-company)

> **Mục đích:** Ngăn cron "đốt token vô ích" khi upstream API chết. Pattern từ `auto-loop.sh` — error counter + cooldown + tự phục hồi.

### Pattern

```python
import json, time, os

CIRCUIT_FILE = os.path.join(os.path.dirname(__file__), ".circuit_breaker.json")
MAX_ERRORS = 5          # số lỗi liên tiếp → ngắt cầu dao
COOLDOWN_MINUTES = 30   # thời gian chờ trước khi thử lại

def check_circuit():
    """Return True if circuit is OPEN (skip this run)."""
    if not os.path.exists(CIRCUIT_FILE):
        return False
    with open(CIRCUIT_FILE) as f:
        state = json.load(f)
    if state["status"] == "open":
        if time.time() - state["opened_at"] < COOLDOWN_MINUTES * 60:
            return True  # still cooling down
        else:
            state["status"] = "half-open"  # try again
            with open(CIRCUIT_FILE, "w") as f:
                json.dump(state, f)
    return False

def record_success():
    if os.path.exists(CIRCUIT_FILE):
        os.remove(CIRCUIT_FILE)  # reset on success

def record_failure():
    state = {"errors": 0, "status": "closed", "opened_at": 0}
    if os.path.exists(CIRCUIT_FILE):
        with open(CIRCUIT_FILE) as f:
            state = json.load(f)
    state["errors"] += 1
    if state["errors"] >= MAX_ERRORS:
        state["status"] = "open"
        state["opened_at"] = time.time()
    with open(CIRCUIT_FILE, "w") as f:
        json.dump(state, f)
```

### Usage trong script no_agent

```python
if __name__ == "__main__":
    if check_circuit():
        print("[CIRCUIT BREAKER] Skipping — too many errors, cooling down.")
        sys.exit(0)
    try:
        main()
        record_success()
    except Exception as e:
        record_failure()
        raise
```

### Tích hợp với Telegram alert
Khi circuit mở → gửi 1 Telegram alert: "Cron [name] bị ngắt cầu dao sau [N] lỗi. Cooling down [M] phút. Check thủ công."
Khi circuit tự phục hồi (half-open → success) → gửi: "Cron [name] đã tự phục hồi."

### Áp dụng cho stock-profile cron
| Cron | Risk khi API chết |
|------|-------------------|
| `stock-price-daily` | Entrade API down → 5 ngày fail liên tiếp → circuit break + Telegram alert |
| `frameworks-weekly` | Web fetch fail → retry vô ích → circuit break |
| `vault-health-monthly` | Agent cron — nếu fail → circuit break không chạy tiếp |

## 15. Warren cron comms rules — 9 규정 (2026-07-27 GrabFood cron)
Khi Bố giao build cron cho warren-profile, áp dụng NGHIÊM NGAY (Bố tự đưa, class-level):
1. **Failed → Telegram ĐỎ, ngắn gọn, KHÔNG im lặng.** Template `🔴 [FAIL] <job> — <lý do ngắn>`.
2. **Success → Telegram XANH + phân tích ngắn gọn.** Template `🟢 [OK] <job> (<week>) • <3 bullets>`.
3. **Schedule + guard chống spam:** Bố duyệt `*/30 7-17 * * 1` (20 lần/T2) + **guard: chỉ chạy lúc đầu (07:00) LUÔN + các lượt sau SKIP nếu tuần hiện tại ĐÃ CÓ log** (check `week_id in log_file`). → tránh spam 20 lần.
4. **Fallback GC kép:** tạo Google Calendar recurring event (T2 07:00) có description (a) nhắc Bố tự paste data GSheet + (b) chứa sẵn lệnh copy-paste vào chat cho GG chạy manual. Tạo qua `google_api.py` (OAuth PRODUCTION persist).
5. **Model = DeepSeek CHÍNH HÃNG:** provider `https://api.deepseek.com`, model `deepseek-v4-flash`. KHÔNG qua OpenRouter/proxy. **API key test BẮT BUỘC:** `urllib GET /v1/models` với `Bearer sk-...` → 200 OK mới ghi "approved"; 401 = key lỗi → ghi "pending", fallback model mặc định. Key ghi vào `profiles/warren-profile/.env` (ngoài vault git → an toàn, KHÔNG echo ra chat).
6. **Commit-push GATE (cứng):** GG KHÔNG tự commit/push. Sau build/xong → HỎI Bố qua Telegram/chat "Có muốn commit push không?". Chỉ Bố "ok/approved" mới `git commit`+`push`. **LUẬT BÁO CÁO:** mọi phản hồi Bố (approve/decline) → GG PHẢI trả "nhận được"/"failed", KHÔNG im lặng.
7. **Guard chống spam** — xem #3.
8. **Reply format tránh trùng T2:** T2 có nhiều cron → Bố reply `ok [số thứ tự] được ko?` (vd `ok 3 được ko?`). GG parse "ok [n]" → thực thi mục n. Không số → hỏi lại.
9. **api_key chính hãng** — xem #5.
- **🔴 TG tự soạn KHÔNG bịa convention (2026-07-28):** Khi GG gửi tin Telegram thủ công (KHÔNG qua cron prompt), TUYỆT ĐỐI không tự viết instruction approve bịa (vd "Reply OK hourly để GG commit/push"). Dùng ĐÚNG convention thật: `[review]`/`[col]` = gửi mới, `'ok review'`/`'ok col'`/`'ok hourly'` = approve. Warren bắt lỗi ngay tin có câu sai convention. Không chắc keyword → HỎI Bố, đừng đoán. (Cron `834e6e519420` hourly dùng `'ok hourly'` = approve commit/push 2 file log+dashboard.)

**Hard rules từ set này:**
- Mọi cron `deliver: all` (Telegram + vault file).
- Cron KHÔNG tự update file manual analysis (vd `GF_Channel_PL.md`) — chỉ parser+dashboard; P&L update thủ công (cần FBD judgement).
- Key auth test là bắt buộc trước ghi "approved" — không đoán.

**🔵 DeepSeek-chính-hãng pin = COMPLIANT với §8.1 (all-crons-free):** Bố's `deepseek` provider trong `config.yaml` trỏ `base_url: https://api.deepseek.com` — là key **free-tier chính hãng**, KHÔNG phải paid API. → `model=deepseek/deepseek-v4-flash` trên 1 cron KHÔNG vi phạm §8.1. **Khi cron cần LLM judgement (vd GrabFood report FBD), PREFER agent-cron + pin `deepseek/deepseek-v4-flash`** thay vì hand-roll `no_agent` script gọi DeepSeek API qua `urllib` (thêm code, dễ lỗi JSON parse, không lợi ích). Đã áp dụng build GrabFood cron 2026-07-27.

## 16.5 `cronjob(action='update')` — TRUYỀN ĐỦ field (2026-07-27 GrabFood)

**PITFALL (thực tế gặp):** `cronjob(action='update')` với `deliver` / `model` / `provider` để **TRỐNG** (rỗng) → resolver ghi `null` lên `jobs.json`, **XÓA giá trị cũ**.
- Ví dụ: update prompt mà không truyền `deliver`/`model`/`provider` → sau update, job mất `deliver:all` + `model` bị null → cron chạy sai hoặc lỗi.
- **FIX (an toàn):** Mỗi lần `update`, TRUYỀN ĐỦ mọi field đang có (id, name, prompt, schedule, model OBJECT, provider, deliver, enabled). Hoặc edit `jobs.json` trực tiếp bằng `python3` (read-modify-write) rồi `git add -f` — ít rủi ro hơn update partial.
- **Verify:** sau update → `cronjob(action='list')` → check `deliver`/`model`/`provider` vẫn đúng (KHÔNG null) trước báo Bố xong.

## 16. Agent-cron build checklist (2026-07-27 — từ GrabFood cron build)

Khi build agent cron (`no_agent:false`) theo flow incremental-implementation + writing-great-skills + TDD:

1. **Slice 0 — verify infra trước code:** test model key alive (`urllib GET /v1/models` → 200), confirm provider `base_url` chính hãng (đọc `config.yaml`, KHÔNG chỉ tin cache JSON), check parser/dashboard/telegram files tồn tại (dùng `ls`, KHÔNG `search_files` dotfolder).
2. **TDD guard logic:** viết pure-function guard (vd spam-guard `should_run_pipeline`) + unit test RED→GREEN trước khi viết skill/cron. Anchor regex `^## <week_id>` (KHÔNG substring — tránh template false-match).
3. **Skill chứa SOP:** prompt chuẩn + guard + report template + fallback GC + hard guardrail (giữ ANCHORS/SOUL). Đặt vào `skills/ops-<domain>-cron/`.
4. **Cron create:** `model={'model':...,'provider':...}` (OBJECT, không 2 string), `deliver:all`, schedule cron-expr.
5. **E2E run:** `cronjob(action='run')` → assert `execution_success:true`, đọc `cron/output/<id>/<ts>.md` confirm behavior (guard SKIP / parser RUN), check Telegram Bố = ĐÚNG 1 tin (Trap B §11.7b).
6. **Prompt MUST override `[SILENT]`** (Trap A §11.7b) + KHÔNG self-send (Trap B).
7. **Fallback GC:** `google_api.py calendar create` với recurrence (OAuth PRODUCTION persist, `--check` trước). Theo `google-workspace` Rule 1: SHOW nội dung event cho Bố approve TRƯỚC khi tạo.
8. **Commit-push GATE:** agent KHÔNG tự push; in "🔔 CÓ MUỐN COMMIT PUSH?" + chờ Bố reply, trả "nhận được"/"failed".

## 16.6 Tạo skill đi kèm cron — Description Budget (HARD tool constraint)

Khi build cron xong mà Bố muốn 1 skill SOP kèm theo (`skill_manage(action='create')`):

- **Description BẮT BUỘC ≤57 ký tự** (budget hệ thống: 1 câu, trigger-first, kết thúc dấu chấm). Dài hơn → lỗi `"must fit the 60-char system-prompt budget"` → tạo fail.
- **Build description TRƯỚC body**, ngắn: `<trigger> + <1 câu làm gì>.` Vd: `"Item Sales weekly cron runner. T2 09:00, no auto-push."` (57 char OK).
- Detail (flow, gates, pitfalls) → đẩy vào SKILL.md body, KHÔNG nhồi vào description.
- Real friction 2026-07-27: description 164 → 100 → 57 char (3 lần mới qua). Luôn viết description <57 char từ đầu.
- Skill mới cho warren-profile → archive backup ngay (`vault/_archives/skills/<name>_SKILL_backup_YYYY-MM-DD.md`) theo SOUL §5 Skill Archive Gate.

## 14. MSYS terminal nuốt stdout — write-to-file fallback (2026-07-26)

**Pitfall:** Trên Windows MSYS terminal, một số lệnh `python3 -c "..."` / `print()` TRẢ KẾT QUẢ NHƯNG tool result hiển thị rỗng (hoặc `wc`/`echo` đi kèm báo "failed" giả). Đặc biệt khi chuỗi có unicode escape (`\u1ebf`...) hoặc output dài. → Đừng kết luận "lệnh fail / file rỗng" từ terminal output rỗng.

**Workaround đã dùng thành công:**
1. Trong python script: ghi kết quả ra file thay vì print → `open('scripts/_dump.txt','w',encoding='utf-8').write(result)` (dùng `profile/scripts/` để path đơn giản, tránh MSYS path issue).
2. `read_file('.../scripts/_dump.txt')` để đọc kết quả (read_file hiển thị đáng tin cậy, KHÔNG bị nuốt).
3. Cleanup: `rm -f scripts/_dump.txt` sau khi xong.
- File lớn (vd jobs.json 31KB): `cp` sang `/tmp/` rồi `read_file('/tmp/...')` để tránh MSYS path issue khi read_file trực tiếp path AppData.
- KHÔNG dùng `execute_code` cho task đọc file config — bị cron-guard chặn trong profile này (`BLOCKED: execute_code runs arbitrary local Python... approvals.cron_mode`).

## 17. No-Agent Parser Cron — verify-gate + path pitfalls (2026-07-27 item-sales build)

Real bugs caught bởi reviewer-node khi build `item-sales-weekly` cron (no_agent runner + verify gate + Telegram, **NO auto-push** per rule 15). Encode để không lặp lại ở mọi cron parser tương lai.

### 17.1 Verify gate inspects WRONG file (dead gate)
Runner `BUILT_HTML = item_sales_trend.html` (file BỐ mở) NHƯNG parser `--emit-html` ghi đè **TEMPLATE** (`item_sales_trend.template.html`) → verify đọc file pipeline KHÔNG produce → gate luôn PASS rỗng (dead, không bắt đc bug trắng chart).
- **FIX pattern:** template = INPUT (read-only source có `__PAYLOADS__`); built = OUTPUT. Parser: `out = tpl.with_name(tpl.name.replace(".template.html", ".html"))`. Runner verify ĐÚNG `BUILT_HTML`.
- **Verifier false-FAIL trap tương tự:** scan ĐÚNG artifact pipeline viết, không phải template/source (xem §10 verifier-scan-wrong-region).

### 17.2 Parser clobbers own template (silent no-op tuần 2)
Parser ghi đè template → tuần sau `__PAYLOADS__` mất → parser ERR + `return` (exit 0) → runner thấy success → 🟢 WHILE dashboard KHÔNG regen.
- **FIX:** parser ghi vào built file, **GIỮ NGUYÊN template** (tái sử dụng được tuần tới).

### 17.3 Week-id format drift (ISO year vs calendar year)
Runner `compute_run_week` dùng `prev_monday.isocalendar()` (ISO year) nhưng parser `make_week_id` (`_utils.py`) dùng `week_start.year` (calendar year) → year-boundary mismatch (~1 tuần/năm): runner verify `2025-W01` nhưng parser viết `2024-W01` → spurious red `thiếu block`.
- **FIX:** runner DÙNG calendar year để khớp parser: `f"{prev_monday.year}-W{prev_monday.isocalendar()[1]:02d}"`.
- **Rule:** mọi module tính week-id PHẢI gọi CÙNG hàm (`make_week_id`) — đừng reimplement.

### 17.4 `HERE = Path(__file__).parent` thiếu `.resolve()`
no_agent script chạy từ `profile/scripts/` (copy của `vault/.scripts/`) → `HERE` relative path fragility khi cwd ≠ script dir → subprocess/PARSER resolve sai.
- **FIX:** `HERE = Path(__file__).resolve().parent`. Compute PARSER/verify target qua absolute `VAULT_ROOT` (env override), KHÔNG qua HERE.

### 17.5 Critic cũng có thể sai — verify disk
reviewer-node báo "không có file item_sales_trend*.html" trong khi THỰT TẾ CẢ 2 file tồn tại (693KB). Con check `ls` → critic false-claim. → **Luôn verify critic claim trên disk** (A9/A10), đừng tin blind kể cả independent reviewer.

→ Full working pattern (runner skeleton + verify gate + no-push + `ok NN` trigger) + bug post-mortem: `references/no-agent-parser-cron-pattern.md`.

### 17.6 Wrapper reuses vault-SSOT orchestrator via absolute subprocess path (SKIP copy step)

**Pattern (LTO cron build, 2026-07-28):** Khi 1 no_agent cron CẦN logic đã có sẵn trong `vault/.scripts/<orchestrator>.py` (đã verify, SSOT) → **KHÔNG copy orchestrator vào `profile/scripts/`**. Thay vào đó: wrapper (nằm `profile/scripts/`, bare name do resolver gọi) **`subprocess.run([sys.executable, VAULT_ROOT/.scripts/<orchestrator>.py, ...])`** trỏ đường dẫn TUYỆT ĐỐI vault.

- **Tại sao hợp lệ:** resolver chỉ giới hạn file `script` của cron (phải bare name trong `profile/scripts/`). NHƯNG wrapper chạy xong → tự spawn subprocess Python riêng → subprocess gọi orchestrator qua absolute path KHÔNG bị resolver chặn. → Orchestrator SSOT duy nhất, không duplicate file, không drift (M1: Stability > Perfection).
- **Refines §1.5:** §1.5 nói "sau edit SSOT PHẢI re-copy vào profile/scripts". Quy tắc đó áp dụng KHI cron script TỰ import module SSOT (resolver không theo dấu subdir → ModuleNotFoundError). Nhưng với mô hình **wrapper → subprocess absolute-path**, không cần copy. Chỉ copy KHI import inline (không subprocess).
- **VAULT_ROOT hardcode an toàn** ở đây: wrapper CWD = `profile/scripts/`, `parents[N]` resolve sai → hardcode `VAULT_ROOT = Path(r"C:\Users\khoans\Documents\Warren_OS_Local\vault")` (như §1.5 #4 khuyên). Hoặc env-override `os.environ.get("VAULT_ROOT", ...)`.
- **Retry SQL:** orchestrator đã có retry trong parser; wrapper bọc thêm retry 3 lần quanh `subprocess.run` (VPN flaky, §17/P6) → fail 3/3 → exit 1 + TG 🔴 (§15 #1).
- **Compute tuần:** cron chạy T2 → tuần vừa đóng = ISO Monday của (hôm qua). Dùng `yesterday - timedelta(days=yesterday.weekday())` (không `isocalendar()` year-drift, xem §12.7 / §17.3). Test BẮT BUỘC với ngày T2 cụ thể.
- **9-điểm compliance (§15) embed vào wrapper:** fail→🔴 TG, ok→🟢 TG tóm tắt, guard-skip nếu tuần đã log, no_agent (không LLM), không tự commit (§15 #6).
- **TDD pattern:** viết `tests/test_<wrapper>.py` TRƯỚC (RED, import wrapper → ModuleNotFoundError), mock `run_orchestrator` + `_get_bot_token` + file IO, GREEN sau. pytest thường CHƯA cài trong venv → chạy `python tests/test_x.py` (unittest native). Xem `references/no-agent-wrapper-cron-pattern.md` cho skeleton đầy đủ (RED test + GREEN wrapper LTO).

- `references/no-agent-wrapper-cron-pattern.md`

## 18.8 Duplicate cron on create — DEDUPE trước khi báo xong (2026-07-28 LTO cron)

**HARD lesson:** `cronjob(action='create')` KHÔNG reject trùng tên. Nếu đã có 1 cron cùng `name` + `schedule` → tạo mới sẽ sinh **2 job trùng** → chạy 2 lần mỗi tick (double-run, double TG, double ghi log).

**Real case (2026-07-28):** GG tạo `lto-weekly` (`*/30 7-17 * * 1`) → phát hiện ĐÃ CÓ `lto-weekly` cũ (`c81421f72858`, thiếu `workdir`, prompt khác) → `cronjob list` show 2 job cùng tên. Catch trước T2 chạy, xóa cái cũ theo Bố duyệt.

**Quy trình BẮT BUỘC sau mọi `cronjob create`:**
1. `cronjob(action='list')` → grep tên cron vừa tạo.
2. Nếu >1 kết quả cùng `name` (hoặc cùng `script`+`schedule`) → **DUPLICATE**.
3. **KHÔNG tự xóa.** Dùng `clarify` đưa Bố chọn: (a) xóa cũ giữ mới, (b) xóa mới giữ cũ, (c) giữ cả 2, (d) chờ Bố check. Ghi rõ job_id + sự khác biệt (workdir, prompt, next_run).
4. Sau xóa → `cronjob list` verify chỉ còn 1.

**Pitfall — verify bằng list, KHÔNG bằng file search:** cron store KHÔNG ở `cron/*.json` (chỉ có lock/output), cũng không grep dễ dàng (MSYS). `cronjob list` là nguồn truth duy nhất. Đừng `search_files` tìm cron — sẽ rỗng.

**Pitfall — cron store location:** `cronjob create` trả success + job_id + `next_run_at` = đã đăng ký (trust API response). Store nằm trong runtime DB/app state, không phải file text editable trực tiếp.

## 18. Redundant-run Guard Pattern (daily cron, 2026-07-28 COL cron)
Khi Bố yêu cầu cron daily chạy khung rộng (vd `*/30 6-12` = 06:00–12:30 mỗi 30p) NHƯNG chỉ muốn xử lý THỰC SỰ 1 lần/ngày → dùng guard "skip nếu hôm nay đã log":
1. **Đầu khung LUÔN chạy:** chỉ slot đầu (`(now.hour,now.minute)==(6,0)`) chạy không điều kiện → bắt queue/intake.
2. **Các slot sau SKIP** nếu state hôm nay đã "done": scan queue/state file tìm entry `received_at` bắt đầu bằng ngày hôm nay (`datetime.now().strftime('%Y%m%d')`) VÀ `status=='done'`.
3. **Đang chờ duyệt KHÔNG skip:** entry `pending_approval` (chờ Bố "ok") → KHÔNG tính là done → cron vẫn chạy để append. (Tránh bẻ gãy flow duyệt của Bố.)
4. **Heartbeat vẫn update** mọi lần chạy (kể cả skip) — tránh false-alert (xem §11.7 never-silent).

**Snippet (no_agent script):**
```python
def _today_already_logged() -> bool:
    today = datetime.now().strftime('%Y%m%d')
    queue = _load_queue()  # hoặc đọc state file
    for e in queue.get('pending', []) + queue.get('history', []):
        rec = (e.get('received_at') or '')[:10].replace('-', '')
        if rec == today and e.get('status') == 'done':
            return True
    return False
# trong main():
now = datetime.now()
if (now.hour, now.minute) != (6, 0) and _today_already_logged():
    print("[guard] today already logged -> skip", file=sys.stderr); return
```
**Verify:** test 3 cases (A done-hôm-nay→True, B pending_approval→False, C done-ngày-khác→False). KHÔNG tự tin không test (xem §9 E2E gate).

**Pitfall — sửa schedule jobs.json PHẢI đồng bộ 5 trường:** Khi `patch` đổi `schedule.expr`, PHẢI cùng lúc sửa `schedule.display` + `schedule_display` + `next_run_at` + `prompt` (text mô tả). Quên sửa `prompt` → Bố đọc mô tả cũ ("Runs 09:05+10:05") gây rối. Backup `jobs.json` → `vault/_archives/cron/jobs_backup_YYYY-MM-DD.json` TRƯỚC edit (jobs.json KHÔNG vào git, xem §3). Sync script SSOT→profile/scripts luôn (§1.5).

## Related Skills
- `telegram-py-checklist` — cron Telegram script format + E2E test-send (§3e) + Pitfall 2 (Markdown 400)
- `windows-gitbash-msys-path` — MSYS path / search_files false-negative
- `vault-ops-automation` — vault automation hooks

## Reference Files
- `references/error-transcripts.md` — raw error messages từ cron runs 2026-07-18 (Script not found, outside scripts dir, HTTP 402, opencode-zen, bash fail)
- `references/cross-profile-discovery.md` — jobs.json schema đầy đủ + recipe audit cron xuyên profile + ví dụ review-telegram-sender
- `references/vault-scripts-ssot-path.md` — `vault/.scripts/` SSOT vs `vault/scripts/` stale trap + verify recipe (2026-07-23)
- `references/cron-verifier-gate-audit.md` — silent-failure grep recipe + 2 real bug transcripts (quota.py, col_telegram_intake.py), 2026-07-25
- `references/cron-silent-failure-6step.md` — compact 6-step audit quick-card (swallowed error → dangerous fallback → propagation gap → false green → function-ref missing → summary). Companion to §11.9 B0-B5. 2026-07-29.
- `references/watcher-commit-e2e-test.md` — RED-GREEN unit test + E2E rollback test recipe cho watcher git-commit (§12.5)
- `references/no-agent-git-watcher-pitfalls.md` — full watcher anatomy (unique trigger, red/green/ack, commit-once guard), repo-corruption transcript + recovery, reject-safe skeleton (§11.10 / §12.6 P1)
- `references/google-calendar-event-pitfalls.md` — GC recurring event create pitfalls: RRULE không lưu + start-time drift (verify bằng list tuần sau) + DeepSeek reasoning-model empty-content-on-200 do max_tokens nhỏ (§7.5)
- `references/gc_cron_fallback_template.md` — GC fallback event description template + create recipe (proven 2026-07-27 item-sales)
- `references/telegram-409-queue-file-pattern.md` — Option D queue-file pattern (bot writes file, watcher reads, zero 409) full skeleton + real deployment (§12.4)
