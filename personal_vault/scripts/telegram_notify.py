#!/usr/bin/env python3
"Telegram notification helper."

import json
import os
import urllib.request


def get_telegram_token() -> str:
    personal_env = "C:/Users/khoans/AppData/Local/LUsinePersonalBot/.env"
    try:
        with open(personal_env, encoding="utf-8-sig") as f:
            for line in f:
                line = line.strip()
                if line.startswith("TELEGRAM_BOT_TOKEN="):
                    return line.split("=", 1)[1]
    except (OSError, ValueError):
        pass
    return os.getenv("TELEGRAM_BOT_TOKEN") or ""


def tg_api(method: str, payload: dict):
    token = get_telegram_token()
    if not token:
        print("TELEGRAM_BOT_TOKEN not set")
        return None
    url = f"https://api.telegram.org/bot{token}/{method}"
    data = json.dumps(payload).encode()
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode())
    except Exception as e:
        print(f"tg_api {method} failed: {e}")
        return None


def send_telegram(message: str) -> bool:
    resp = tg_api("sendMessage", {"chat_id": "2117653672", "text": message})
    return bool(resp and resp.get("ok"))
