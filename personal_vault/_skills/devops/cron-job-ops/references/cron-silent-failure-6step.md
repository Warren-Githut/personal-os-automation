# Silent-Failure Audit — 6-Step Quick Card

> Compact audit methodology cho cron jobs. Adapted từ oh-my-hermes (MIT, 303★). Bố approve 2026-07-29.
> Mở rộng: `cron-job-ops` §11.9 (audit procedure) + §11.8 (anti-patterns). Companion reference.

---

## 6 bước (chạy theo thứ tự)

| # | Bước | Lệnh | Phát hiện |
|---|------|------|-----------|
| 1 | **Swallowed Error** | `grep -rn "except.*:\s*pass" *.py` | Code nuốt lỗi âm thầm → silent no-op |
| 2 | **Dangerous Fallback** | `grep -rn "except.*:\s*return 0\|return \"\"\|return None" *.py` | Trả giá trị an toàn giả → số sai |
| 3 | **Propagation Gap** | `grep -rn "sys.exit(0)" *.py` (trong except/error block) | Báo OK dù thực sự lỗi |
| 4 | **False Green** | Cross-check `last_status=ok` vs `script` còn tồn tại | Báo OK nhưng script đã xóa |
| 5 | **Function-Ref Missing** | So sánh `calls` vs `defs` cho mỗi helper function (`_token`, `_send_telegram`, ...) | `NameError` từ copy-paste rớt hàm |
| 6 | **Tổng hợp** | Bảng 🔴 CRITICAL / 🟡 WARNING / 🟢 OK | Báo cáo gọn, đề xuất fix |

---

## Chi tiết từng bước

### B1 — Swallowed Error (`except: pass`)
```bash
cd vault/.scripts && grep -rnE "except.*:\s*pass$" *.py
cd profile/scripts && grep -rnE "except.*:\s*pass$" *.py
```
- ✅ Cleanup trong `finally` (vd `os.unlink`) = LOW risk
- ❌ Nuốt lỗi parse/network = HIGH risk → silent no-op

### B2 — Dangerous Fallback (`return 0`/`return ""`)
```bash
cd vault/.scripts && grep -rnE "except.*:\s*return 0\b|except.*:\s*return \"\"|except.*:\s*return None" *.py
```
- ✅ Parse function trả 0 cho cell rỗng = MEDIUM risk (dữ liệu sai)
- ❌ State/network function trả 0 = HIGH risk (báo cáo sai)

### B3 — Propagation Gap (`sys.exit(0)` trong error path)
```bash
cd vault/.scripts && grep -rn "sys.exit(0)" *.py
```
- ✅ End-of-main = OK
- ❌ Trong `if not args: sys.exit(0)` = SAI → `exit(1)` mới đúng

### B4 — False Green
```bash
# Lấy cronjob list → với mỗi no_agent last_status=ok → check script tồn tại
for f in $(cronjob list | grep -A5 '"ok"' | grep 'script":' | grep -oP '"\K[^"]+\.py'); do
  test -f "profile/scripts/$f" && echo "OK: $f" || echo "🔴 MISSING: $f"
done
```
- Script bị xóa nhưng cron vẫn báo OK → Bố tưởng đang chạy

**⚠️ PITFALL — Secondary bugs surface only after first fix:** When a script crashes at line N on `NameError`, fixing that bug reveals the NEXT bug at line N+1 that was never reached before. **Always run the script empirically after EVERY fix** — don't claim "done" after a single patch. Real case (2026-07-29): `col_telegram_intake.py` — fixed `_token()` undefined (B5), ran script → `NameError: urllib.request` not imported at line 46 (B4 empirical). Two bugs, same file, both silent until the first was cleared.

### B5 — Function-Ref Missing (new 2026-07-29)
```bash
cd vault/.scripts
for f in *.py; do
  for fn in _token _get_updates _allowed_users _send_telegram _today_already_logged _queue _approve; do
    calls=$(grep -cP "[^a-z_]$fn\(" "$f" 2>/dev/null || echo 0)
    defs=$(grep -cP "^def $fn\(" "$f" 2>/dev/null || echo 0)
    [ "$calls" -gt "$defs" ] && echo "🔴 $f: $fn called $calls but defined $defs"
  done
done
```
- **Real bug:** `col_telegram_intake.py` gọi `_token()` không có `def` → NameError mỗi 30p
- Grep `except:pass` KHÔNG bắt được pattern này (không phải exception trong try)

### B6 — Tổng hợp báo cáo
```
🔴 [N] CRITICAL — cần fix ngay
🟡 [N] WARNING — theo dõi
🟢 [N] OK

─── CRITICAL ──────────────────────────────
🔴 SWALLOWED ERROR: file.py:NN — except: pass
   → Impact: ...
   → Fix: ...
─── WARNING ───────────────────────────────
🟡 DANGEROUS FALLBACK: file.py:NN — return 0
...

→ Bố muốn fix cái nào trước?
```

---

## Kết hợp với §11.9 audit procedure

| Bước này | = | §11.9 step |
|----------|---|------------|
| B1 | → | B1 (grep swallow) |
| B2 | → | B1 + B2 (3-state phân biệt) |
| B3 | → | (new) |
| B4 | → | (new) |
| B5 | → | **B0** (function-ref check) |
| B6 | → | Báo cáo cuối |

> Gọi `cron-job-ops` §11.9 B3-B5 nếu cần sâu hơn (reviewer-node + exit-code test + patch vòng 2).

---

## Output mẫu (của session 2026-07-29)

```
🔴 [1] CRITICAL — col_telegram_intake.py: _token() undefined (B5)
   → COL Telegram intake CHẾT từ 28/07
   → Fix: thêm def _token() block
🟡 [3] WARNING — gen_today_daily error, item-sales error, return 0 fallbacks
🟢 [12] OK
```
