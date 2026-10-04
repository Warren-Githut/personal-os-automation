# Warren-Vault Pipeline Build Pattern (2026-07-24)

Condensed pattern cho build pipeline wrap các parser có sẵn trong Warren vault.
Áp dụng cho: revenue screenshot pipeline, bất kỳ ingest Telegram → parser → SSOT.

## Architecture
1 orchestrator + 1 telegram intake + 2 cron (poll + heartbeat). Cả 2 gọi lại script có sẵn (KHÔNG copy logic OCR).

## Orchestrator (run_X_pipeline.py)
- `VAULT = Path(__file__).resolve().parents[1]` (vault/.scripts → vault). Thợ ở `vault/10_OPERATION_DATA/.parsers/`.
- argparse: `--sys --lu3 --lu5 --lu7 --week --override-json --test --no-git --no-tg`.
- `--test` → gọi parser `--test-json <fixture> --dry` (BẮT BUỘC --dry, không ghi SSOT).
- Map exit code → 🔴: `1`=THIẾU ẢNH, `2`=VERIFY FAIL, `4`=OCR FAIL.
- Sau xanh: gọi dashboard gen → git scoped push → build_report_v3 → send_telegram.
- Reuse `vault/.scripts/_send_telegram.py` (token từ `~/AppData/Local/LUsineWorkBot/.env`, chat `2117653672`).

## Telegram Intake (revweek_telegram_intake.py)
- Poll `getUpdates` (urllib, no_agent 0 token — pattern từ `col_telegram_intake.py`).
- Filter: `user_id == "2117653672"` + caption chứa `01_weekly_revenue`.
- Offset file `.revweek_telegram_offset.json` (ack SAU loop, không giữa chừng).
- **Persist-partial:** save ảnh ngay (`RAW_DIR/{week}_{slot}.png`, slot = số thứ tự đã có), đếm đủ 4 (sys/lu3/lu5/lu7) mới chạy pipeline. KHÔNG buffer file_id.
- Heartbeat: `--heartbeat-check` chỉ chạy 17:00 Thứ 2, nếu chưa `done` tuần đó → 🔔 nhắc (dedup qua `.revweek_heartbeat.json`).

## Cron (no_agent, free)
- Copy script vào `~/AppData/Local/hermes/profiles/warren-profile/scripts/` (cross-profile guard).
- `revweek-telegram-intake`: `*/30 8-17 * * 1`, deliver=all.
- `revweek-heartbeat`: `0 17 * * 1`, deliver=all.
- Test: `cronjob action=run` → check `execution_success: true`.

## Gotchas (bắt trong session)
- Test mode thiếu --dry → ghi đè SSOT thật (revert bằng `git checkout`).
- Parser OCR crash uncaught → wrap try/except + `sys.exit(4)`.
- `search_files` git-bash PATH FAIL trên vault subfolders → dùng `terminal grep`/`ls` thay.
- Ảnh AI giả KHÔNG khớp layout BI → parser đúng reject. Happy-path E2E chờ ảnh thật Bố gửi T2.
- Fixture JSON cho --test-json: `{"SYS":{net_rev,covers,avg,tickets}, "LU3"/"LU5"/"LU7":{...}}` (sum stores == SYS để qua L1).
