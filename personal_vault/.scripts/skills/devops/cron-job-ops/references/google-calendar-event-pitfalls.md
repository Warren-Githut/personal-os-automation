# Google Calendar Event Pitfalls (warren-profile cron fallback)

Reproduction recipes + gotchas khi tạo GC recurring event làm fallback cho cron (dùng `google-workspace/scripts/google_api.py calendar create`). `google-workspace` là bundled skill — KHÔNG sửa nó; capture pitfall ở đây.

## 1. Recurrence (RRULE) có thể KHÔNG được lưu (verify bằng list tuần sau)

**Symptom (2026-07-27 GrabFood cron):** tạo event với `--recurrence "FREQ=WEEKLY;BYDAY=MO"` → `calendar list` JSON KHÔNG có field `recurrence` (hoặc `None`). Event chỉ xuất hiện 1 lần, không lặp.

**Verify bắt buộc — list tuần SAU:**
```bash
GAPI="python C:/Users/khoans/AppData/Local/hermes/profiles/warren-profile/skills/productivity/google-workspace/scripts/google_api.py"
$GAPI calendar list --start 2026-08-10T00:00:00+07:00 --end 2026-08-10T23:59:00+07:00 \
  | python3 -c "import sys,json; d=json.load(sys.stdin); [print('FOUND:',e['summary'],e.get('start')) for e in d if 'GrabFood' in e.get('summary','')]"
```
- Thấy event ở tuần sau → RRULE đã lưu ✅
- Không thấy → xóa + tạo lại.

**Note:** `calendar list` trong view thường KHÔNG show field `recurrence` ngay cả khi đã lưu (chỉ hiện khi list đúng ngày occurrence). Cách chắc chắn = list tuần sau và xem event có hiện lại không.

## 2. Start time có thể drift

**Symptom:** truyền `--start 2026-07-27T07:00:00+07:00` nhưng event ghi `2026-07-27T11:00:00+07:00`.

**Fix:** luôn verify `start` field sau create:
```bash
$GAPI calendar list --start 2026-07-27T00:00:00+07:00 --end 2026-07-27T23:59:00+07:00 \
  | python3 -c "import sys,json; d=json.load(sys.stdin); [print(e['summary'],'|',e.get('start')) for e in d if 'GrabFood' in e.get('summary','')]"
```
Nếu sai → `calendar delete <id>` + create lại với start đúng.

## 3. Safe create sequence

1. `calendar create --summary ... --start <T2 07:00> --end <+15m> --description "$DESC" --recurrence "FREQ=WEEKLY;BYDAY=MO"`
2. `calendar list` tuần này → assert `start` đúng.
3. `calendar list` tuần sau → assert event xuất hiện lại (RRULE ok).
4. Nếu 2 hoặc 3 sai → `calendar delete <id>` → tạo lại.

## 4. DeepSeek key test (real call, không chỉ models list)

`/v1/models` trả 200 KHÔNG chứng minh chat hoạt động. Test THẬT:
```python
import os,urllib.request,json
key=os.environ["DEEPSEEK_API_KEY"]  # hoặc đọc từ .env
body=json.dumps({"model":"deepseek-v4-flash","messages":[{"role":"user","content":"Say hello in one word."}],"max_tokens":50,"temperature":0.3}).encode()
req=urllib.request.Request("https://api.deepseek.com/v1/chat/completions",data=body,headers={"Authorization":f"Bearer {key}","Content-Type":"application/json"},method="POST")
r=urllib.request.urlopen(req,timeout=30); data=json.load(r)
print(r.status, repr(data["choices"][0]["message"]["content"]), data["choices"][0].get("finish_reason"), data.get("usage"))
```
- **Gotcha:** `max_tokens` quá nhỏ (vd 20) → STATUS 200 NHƯNG `content=''` (reasoning model tiêu `reasoning_tokens` trước). Set >=50.
- Context-preview "Authentication Fails (governor)" là cảnh báo chung của URL, KHÔNG phải lỗi key — luôn test real call để confirm.
