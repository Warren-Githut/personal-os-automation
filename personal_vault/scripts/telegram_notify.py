#!/usr/bin/env python3
"""Telegram notification helper."""

import json
import os
import urllib.request
from pathlib import Path


def get_telegram_token() -> str:
    """Get Telegram bot token — prefer personal life bot, fallback to env."""
    # 1) Personal life bot token (LUsinePersonalBot)
    personal_env = Path("C:/Users/khoans/AppData/Local/LUsinePersonalBot/.env")
    if personal_env.exists():
        with open(personal_env, encoding="utf-8-sig") as f:
            for line in f:
                line = line.strip()
                if line.startswith("TELEGRAM_BOT_TOKEN="):
                    return line.split("=", 1)[1]

    # 2) Global env var (HORION / LUsineWorkBot — may be stale)
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if token:
        return token

    return ""


def send_telegram(message: str) -> bool:
    """Send message to Telegram chat."""
    token = get_telegram_token()
    if not token:
        print("⚠️  TELEGRAM_BOT_TOKEN not set, skipping Telegram notification")
        return False
    
    try:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        data = json.dumps({"chat_id": "2117653672", "text": message}).encode()
        req = urllib.request.Request(
            url,
            data=json.dumps({"chat_id": "2117653672", "text": message}).encode(),
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status == 200
    except Exception as e:
        print(f"⚠️  Telegram send failed: {e}")
        return False