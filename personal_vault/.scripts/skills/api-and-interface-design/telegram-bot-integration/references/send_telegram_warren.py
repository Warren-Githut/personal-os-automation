"""Send a Telegram message (+ optional file) to Warren via @lusine_work_bot.

Usage:
    python3 send_telegram_warren.py "message text" [path/to/attachment.md]

- Reads token + chat_id from C:/Users/khoans/AppData/Local/LUsineWorkBot/.env
- UTF-8 safe (no shell variable mangling)
- Verify-then-send is separate (run getMe check before this if unsure)

Hardcode bot source: LUsineWorkBot/.env  (NOT LUsineBot / LUsinePersonalBot)
"""
import os, sys, json, urllib.request, urllib.parse
from pathlib import Path

ENV = Path(r"C:/Users/khoans/AppData/Local/LUsineWorkBot/.env")
env = {}
for ln in open(ENV, encoding="utf-8-sig"):
    ln = ln.strip()
    if ln and not ln.startswith("#") and "=" in ln:
        k, v = ln.split("=", 1)
        env[k.strip()] = v.strip()
TOKEN = env["TELEGRAM_BOT_TOKEN"]
CHAT = env["TELEGRAM_ALLOWED_USERS"].split(",")[0].strip()
BASE = f"https://api.telegram.org/bot{TOKEN}"


def post(url, data=None, files=None):
    if files:
        boundary = "----hermesbot"
        parts = []
        for k, v in data.items():
            parts.append(f"--{boundary}\r\nContent-Disposition: form-data; name=\"{k}\"\r\n\r\n{v}\r\n".encode("utf-8"))
        for k, fp in files.items():
            fn = os.path.basename(fp)
            parts.append(f"--{boundary}\r\nContent-Disposition: form-data; name=\"{k}\"; filename=\"{fn}\"\r\nContent-Type: application/octet-stream\r\n\r\n".encode("utf-8"))
            parts.append(open(fp, "rb").read())
            parts.append(b"\r\n")
        parts.append(f"--{boundary}--\r\n".encode("utf-8"))
        req = urllib.request.Request(url, data=b"".join(parts),
                                    headers={"Content-Type": f"multipart/form-data; boundary={boundary}"})
        return json.loads(urllib.request.urlopen(req, timeout=30).read().decode("utf-8"))
    data = urllib.parse.urlencode(data).encode("utf-8")
    return json.loads(urllib.request.urlopen(urllib.request.Request(url, data=data), timeout=30).read().decode("utf-8"))


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 send_telegram_warren.py \"message\" [file]")
        sys.exit(1)
    msg = sys.argv[1]
    r1 = post(f"{BASE}/sendMessage", {"chat_id": CHAT, "text": msg})
    print("sendMessage:", "OK" if r1.get("ok") else r1)
    if len(sys.argv) >= 3:
        fp = sys.argv[2]
        if not Path(fp).exists():
            print(f"File not found: {fp}")
            sys.exit(1)
        r2 = post(f"{BASE}/sendDocument", {"chat_id": CHAT}, {"document": fp})
        print("sendDocument:", "OK" if r2.get("ok") else r2)


if __name__ == "__main__":
    main()
