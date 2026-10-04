# Cron Verifier-Gate Audit — Worked Example (2026-07-25)

> Context: Warren đọc bài @vartekxx về Context/Loop Engineering ("verifier gate = tăng 2-3x chất lượng; without verifier = agent đồng tình với chính nó on repeat"). Yêu cầu audit 16 cron warren-profile cho verifier gaps + adapt framework.

## Grep recipe (chạy cho mọi no_agent job)
```bash
cd "C:/Users/khoans/Documents/Warren_OS_Local"
grep -inE "verify|assert|raise|sys.exit|except" vault/.scripts/<script>.py | head -20
# hoặc profile script:
grep -inE "verify|assert|raise|sys.exit|except" <profile>/skills/<skill>/scripts/<script>.py
```
- Có `sys.exit(1)` / `raise` khi data sai → ✅ cứng.
- Chỉ `except (X, Y):` nuốt lỗi, KHÔNG exit → ❌ silent-failure GAP.
- LLM cron (`no_agent=false`): đọc prompt preview — có bước check rõ ràng không (thiếu cả tầng prompt lẫn script = gap 2 tầng).

## 16-job kết quả (tóm tắt)
| Job | Script/Type | Verifier | State |
|---|---|---|---|
| 97c05046989a | review-telegram-sender (no_agent) | sys.exit(1) no-token/state-fail | ✅ cứng |
| 7a080d54e0ac | col-deterministic-watcher (no_agent) | `_verify_dumps_consistency` Guest×AC vs Net cùng dump, non-circular (ghi rõ NOT GSheet) | ✅ cứng (A6/A9/A10) |
| 630a59454d48 | menu-gp-accumulate | sys.exit(1) ×9 + raise | ✅ cứng |
| b51a6f29fb83 | gen-today-daily | exit(0 if ok else 1) | ✅ cứng |
| e58f50ad03ac | fill-promo-tracking | sys.exit(1) | ✅ cứng |
| 9e9689fc9b77 / cfe813f046cf | Vault Consistency Nightly ×2 | SSOT conflict ≥5% scan | ✅ cứng |
| 56940ae5a698 | weekly-revenue-sql (LLM+skill) | 3-layer verify trong pipeline | ✅ downstream |
| 35a514c71140 / 96a51b396925 | revweek intake ×2 (no_agent) | poller thôi, verify ở pipeline | 🟡 downstream, chưa check |
| **d235537ac561** | **Model Router Daily Report (LLM, quota.py)** | **load_state() nuốt corruption → auto-reset 0, KHÔNG exit; prompt chỉ "run+send"** | ❌ **GAP 2 tầng** |
| **16d81e801a39** | **col-telegram-intake (no_agent)** | **_token()/_get_updates() nuốt MỌI exception → return None/[]** | ❌ **GAP silent** |
| 5b7f65238cfe / a423cfe9598b | Skills Backup / session-backup | backup-only, fail=skip | 🟡 low-risk |
| 5b989c1b38b4 | review-queue-watcher | draft-only, sender verify sau | 🟡 low-risk |
| ce45efa2e9f3 | Weekly Loop Doctor (LLM) | audit skill tự check | ✅ tự-check |

## 2 GAP + fixes đề xuất (zone 🟡, chưa apply — chờ Warren duyệt)
- **F1** `quota.py` (d235537ac561): `load_state()` → nếu json corrupt → `sys.exit(1)` + log, KHÔNG reset 0. ~5 dòng.
- **F2** `col_telegram_intake.py` (16d81e801a39): catch riêng token/network fail → N lần fail → heartbeat alert / exit ≠ 0 thay vì return None/[]. ~10 dòng.

## Reviewer-node (A10) transcript — critic bắt blind spot
Con tự mãn "chỉ 1 gap (Model Router)". Critic (leaf, fresh context) đọc trực tiếp quota.py + col_telegram_intake.py + review_telegram_sender.py + col_deterministic_watcher.py + col_queue_handler.py + jobs.json, bắt:
1. Con mô tả sai bản chất gap #1 (bảo "fetch fail" — thực ra quota.py KHÔNG fetch, nó đọc local state, auto-reset 0).
2. Con bỏ sót gap #2 (col-telegram-intake nuốt exception → silent no-op) dù tự gán "assume ok".
3. 2 over-claim: gán verifier cho intake job (col-telegram-intake, revweek intake) trong khi verify nằm downstream (approve_col read-back / pipeline 3-layer).
4. Xác nhận ĐÚNG: review-telegram-sender + col-deterministic-watcher có verifier cứng, non-circular.

Lesson: audit verifier = class task BẮT BUỘC qua reviewer-node (A10). Tự audit dễ tự mãn "chỉ 1 gap".

## Adapt vs Steal verdict (bài @vartekxx)
- **Adapt (miễn phí, đang làm):** 4 operations (Write/Select/Compress/Isolate) + verifier gate philosophy. Ghi vào WARREN_MEMORY §External Knowledge.
- **Skip (tooling Claude Code):** CLAUDE.md 200-line, /loop, hooks/Stop, Routines cloud, Dynamic Workflows fan-hundreds — ta có bản Hermes riêng, overkill 3-store.
- **Không build mới:** moratorium + "infrastructure before usage data".
