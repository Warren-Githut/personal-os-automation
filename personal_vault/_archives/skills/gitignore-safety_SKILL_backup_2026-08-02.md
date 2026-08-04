---
name: gitignore-safety
description: "Verify và maintain .gitignore an toàn — đảm bảo secret/db/memory KHÔNG bao giờ commit vào repo, mà không làm hỏng file thật. Dành cho warren-profile và mọi repo Hermes có chứa token/api_key. Capture bài học 2026-07-17: verify sai cách xóa mất google_token.json."
version: 1.0.0
tags: [git, gitignore, security, secret, verify, hygiene]
category: devops
related_skills: [skill-bundle-audit, vault-simplify-ssot]
---

# gitignore-safety — Verify .gitignore không rò rỉ secret

> **Mục đích:** Giữ repo sạch secret. Khi sửa `.gitignore`, phải VERIFY thực tế git có bỏ qua (ignore) đúng các file nhạy cảm — nhưng làm sao KHÔNG xóa/file thật.
> **Bối cảnh:** Warren non-IT, không biết git. Hermes tự quản repo. 2026-07-17 Hermes xóa nhầm `google_token.json` vì verify sai → bài học đóng gói ở đây.

---

## 1. KHI NÀO DÙNG
- Sửa `.gitignore` (thêm secret/db/memory vào ignore).
- Nghi ngờ repo đang lỡ commit secret (check `git log` / `git ls-files | grep -i token`).
- Trước khi dạy Warren `git add .` (phải chắc không lộ).

---

## 2. VERIFY AN TOÀN (HARD RULE)

### ❌ TUYỆT ĐỐI KHÔNG LÀM
```
touch .env && git check-ignore .env && rm .env   # SAI: nếu .env thật tồn tại, rm xóa luôn file thật chưa commit
```
→ 2026-07-17: Hermes tạo `.env`/`google_token.json` cùng tên file thật → `rm` xóa file thật → mất Google Calendar access, phải re-auth.

### ✅ CÁCH ĐÚNG (chọn 1)
**A. Check trực tiếp trên file thật (không tạo file):**
```bash
cd <repo> && git check-ignore -v google_token.json .env config.yaml
# exit 0 = ignored (an toàn). In ra dòng "<file>: <line>:<pattern>" để biết rule nào khớp.
```
- Không tạo file, không rủi ro.
- Nếu file chưa tồn tại → vẫn check được (git đọc pattern, không cần file có thật).

**B. Probe file giả trong subfolder (khi cần test nested pattern):**
```python
import os, subprocess, shutil
REPO = r"C:/Users/khoans/AppData/Local/hermes/profiles/warren-profile"
T = "_verify_probe_tmp"
os.makedirs(os.path.join(REPO, T), exist_ok=True)
for f in [".env", "auth.json", "state.db"]:
    open(os.path.join(REPO, T, f), "a").close()
    r = subprocess.run(["git","check-ignore", f"{T}/{f}"], cwd=REPO, capture_output=True, text=True)
    print("IGNORED" if r.returncode==0 else "LEAK!", f)
shutil.rmtree(os.path.join(REPO, T), ignore_errors=True)  # DỌN NGAY
```
- Dùng ĐÚNG tên thật (`.env` không phải `.env.probe` — suffix không khớp pattern).
- Nằm trong subfolder → không đè file thật ở root.
- `shutil.rmtree` cleanup ngay sau test.

**C. Temp script (không để trong repo):**
- Viết `C:/Users/khoans/AppData/Local/Temp/hermes-verify-gitignore.py`, chạy, xóa.
- Temp dir KHÔNG phải git repo → `git check-ignore` luôn LEAK giả. Phải chạy `check-ignore` với `cwd=<repo thật>`.

---

## 3. .gitignore CHUẨN (warren-profile)

Ignore những nhóm sau (chi tiết xem `references/standard-gitignore.md`):
- **Secrets:** `.env`, `*.env`, `auth.json`, `google_token.json`, `google_client_secret.json`, `config.yaml` (chứa api_key), `fix_token.py`
- **DB/state:** `*.db`, `*.db-shm`, `*.db-wal`, `state.db`, `projects.db`
- **Runtime:** `logs/`, `cache/`, `sessions/`, `cron/`, `memories/`, `scripts/`, `templates/`
- **Personal:** `memories/`, `MEMORY.md`, `USER.md`

⚠️ `skills/` thường đã ignore (skills có repo riêng) — đó là THIẾT KẾ, không phải bug.

- **Build artifacts / node deps:** `vault/node_modules/`, `vault/.scripts/_*.html` (test fixtures), `node_modules/` (anywhere in repo). See §8.

---

## 4. RECOVERY KHI LỠ XÓA SECRET
1. Search backup: `find C:/Users/khoans -name "google_token*.json"` (thường có ở `C:/Users/khoans/AppData/Local/hermes/`).
2. Copy lại vào profile: `cp <backup> <profile>/`.
3. Nếu token hết hạn → re-auth: `python3 vault/.scripts/google_reauth.py` (mở browser, Bố nhấn Allow).
4. Verify: `python3 -c "from google.oauth2.credentials import Credentials; c=Credentials.from_authorized_user_file('google_token.json',['https://www.googleapis.com/auth/calendar']); print(c.valid)"`

---

## 8. NODE_MODULES TRONG VAULT (learned 2026-07-28)

### 8.1 ROOT CAUSE — tại sao `vault/node_modules/` xuất hiện
- `vault/package.json` tồn tại (để track 1 dep legit: `@modelcontextprotocol/server-memory`).
- Khi GG/subagent chạy `npm install <pkg>` **tại thư mục `vault/`** → npm tạo `vault/node_modules/` (hàng ngàn file).
- **Hậu quả kép:**
  1. **Obsidian chậm:** Obsidian index TOÀN BỘ vault → thư mục rác hiện đầy trong file explorer, nặng app.
  2. **Repo bloat:** nếu `.gitignore` chưa có `node_modules/` → `git add` kéo cả ngàn file lên GitHub.
- **Phát hiện 2026-07-28:** dep `jsdom` được cài vào vault NHƯNG **KHÔNG DÙNG** — script verify (`html_dashboard_verify.py`) chỉ gọi binary `node` (đã có trên PATH: `C:/Program Files/nodejs/node`, `node --check` + VM render). `npm install` là lãng phí → rác thừa.

### 8.2 HARD RULE — KHÔNG `npm install` trong vault
- ❌ TUYỆT ĐỐI không `npm install` bên trong `vault/` (hay bất kỳ subfolder vault nào).
- ✅ Nếu cần verify JS: dùng system `node` binary trực tiếp (không dep). VD gate dashboard: `python3 vault/.scripts/html_dashboard_verify.py <file.html>` → script gọi `node` ngầm.
- ✅ Nếu THỰC SỰ cần 1 dep (hiếm): install NGOÀI vault (vd `C:/temp/`), hoặc add path vào `.gitignore` + `git check-ignore` verify TRƯỚC mọi push.

### 8.3 CLEANUP (khi đã lỡ tạo)
```bash
cd <repo>
rm -rf vault/node_modules              # an toàn — generated, không phải source
git checkout -- vault/package.json vault/package-lock.json   # revert dep thừa
# .gitignore đã có vault/node_modules/ (§3) — verify:
git check-ignore -v vault/node_modules && echo "IGNORED ✓"
git status --short                    # node_modules phải biến khỏi untracked
```
- Obsidian sẽ tự dọn `node_modules/` khỏi index sau vài phút; hoặc Bố restart Obsidian cho sạch ngay.
- KHÔNG commit `package-lock.json`/`package.json` chứa dep rác (revert về nguyên bản).

## 5. BANNED
- ❌ `touch` file cùng tên secret thật rồi `rm`.
- ❌ `git add .` khi chưa verify `.gitignore` (Warren không biết git).
- ❌ Commit `google_token.json` / `.env` (push lên GitHub = lộ).
- ❌ Dùng `execute_code` để verify (bị cron gate block) — dùng `terminal` + python.

## 6. VERIFY GATE
Sau sửa `.gitignore`: chạy §2 cách A hoặc B → tất cả secret trả `IGNORED`. Thiếu 1 = FAIL, sửa tiếp.

---

## 7. WINDOWS-SPECIFIC LEAK + GIT-ADD WORKAROUNDS (learned 2026-07-26)

### 7.1 `*.suffix` secrets leak (auth.json.corrupt)
`.gitignore` ghi `auth.json` → git ignore CHÍNH XÁC `auth.json`, KHÔNG bắt `auth.json.corrupt` / `auth.json.bak`.
Một file corrupt/backup copy CHỨA TOKEN THẬT vẫn bị commit → LEAK.
**Fix:** thêm wildcard `auth.json.*` (hoặc `*.corrupt` nếu muốn broad). Luôn check-ignore VỚI ĐUÔI THẬT trước push:
```bash
git check-ignore -v "auth.json.corrupt"   # phải trả IGNORED
```

### 7.2 `git add -f` KHÔNG stage được file trong ignored dir (MSYS/git quirk)
Khi `.gitignore` có `skills/` (ignore toàn bộ), `git add -f skills/_deleted/...` trả exit 0 NHƯNG KHÔNG stage (git im lặng bỏ qua).
Exception `!skills/_deleted_2026-07-26/` cũng không có hiệu lực nếu parent `skills/` bị ignore bằng directory-rule.
**Fix sequence đã verified:**
1. Đổi `skills/` → `skills/*` (ignore nội dung, cho phép track subdir explicit).
2. Thêm exception: `!skills/_deleted_2026-07-26/` + `!skills/_deleted_2026-07-26/**`.
3. NẾU vẫn không stage → `git add -f` vẫn fail → dùng **`git update-index --add -- <file>`** (bypass add, write thẳng vào index). Loop: `find ... -print0 | while read -d ''; do git update-index --add -- "$f"; done`.
4. Cleanup: bỏ `.pyc` khỏi stage (`git reset -q -- <file>`).

### 7.3 SECRET LEAK PRE-PUSH CHECKLIST (bắt buộc trước mọi push)
```bash
cd <repo>
git status --short
git diff --cached --name-only | grep -iE "auth\.json|token|\.env|secret|google_client" && echo "❌ LEAK" || echo "✅ CLEAN"
git check-ignore -v "auth.json.corrupt" "desktop/" "state/"
```
- ❌ `git add -A` / `git add .` — chỉ stage đúng path cần thiết.
- ❌ `npm install` bên trong `vault/` (tạo `vault/node_modules/` → rác Obsidian + repo bloat). Xem §8.
- Nếu repo ignore `skills/` → skill-archive KHÔNG vào git trừ khi force-add như §7.2.
