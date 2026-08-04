# OAuth token expired / revoked — re-auth flow (2026-07-17 real case)

## Symptom
```
google.auth.exceptions.RefreshError: ('invalid_grant: Token has been expired or revoked.')
```
Token `warren-profile/google_token.json` hết hạn (expiry timestamp trong past) hoặc bị Google revoke.

## Fix (verified 2026-07-17)
Chạy script re-auth có sẵn — mở browser, Warren bấm Allow, token mới ghi đè:
```bash
python3 "C:/Users/khoans/Documents/Warren_OS_Local/vault/.scripts/google_reauth.py"
```
Script: `InstalledAppFlow` + `run_local_server(port=8080, prompt="consent")` → ghi lại `google_token.json` (token + refresh + expiry).

## Verify
Script in ra `token valid: True` → OK. Sau đó create/patch event bình thường.

## Notes
- `google_token.json` / `google_client_secret.json` = SECRET. KHÔNG commit vào git (skills repo hay vault repo).
- Nếu không có `google_client_secret.json` → lấy từ Google Cloud Console (OAuth client desktop) hoặc hỏi Warren.
- Sau re-auth, mọi flow trong `oauth-recurring-event-patch.md` chạy lại được.
