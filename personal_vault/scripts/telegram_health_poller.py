#!/usr/bin/env python3
"""Telegram health log poller — [capture-sleep] tag capture with confirmation gate.

Polls the personal life bot (1-1 chat) for messages tagged [capture-sleep].
Proposes a draft back to Telegram -> waits for 'ok' / 'skip' reply ->
writes to 051_Sleep_Log.md -> syncs GSheet -> git commit+push (scoped).

Designed for non-interactive cron (no_agent=True). Each poll is a single
cycle: process pending reply (if any), then process new tagged messages.

Usage:
  python3 telegram_health_poller.py --once      # single poll cycle
  python3 telegram_health_poller.py --dry-run   # parse sample, no writes/sends
"""

import argparse
import json
import subprocess
import sys
import urllib.request
from datetime import datetime
from pathlib import Path

# Reuse existing parse / write / sync logic from process_sleep.py
sys.path.insert(0, str(Path(__file__).resolve().parent))
import process_sleep as ps  # noqa: E402
from telegram_notify import get_telegram_token, send_telegram  # noqa: E402

VAULT_ROOT = Path("C:/Users/khoans/Documents/Personal_OS")
SLEEP_LOG = VAULT_ROOT / "personal_vault" / "10_PULSE" / "051_Sleep_Log.md"
CHAT_ID = "2117653672"
SCRIPTS_DIR = Path(__file__).resolve().parent
OFFSET_FILE = SCRIPTS_DIR / ".telegram_offset.json"
PENDING_FILE = SCRIPTS_DIR / ".telegram_pending.json"
TAG = "[capture-sleep]"


# --------------------------------------------------------------------------- #
# Telegram API helpers (stdlib urllib only)
# --------------------------------------------------------------------------- #
def tg_api(method: str, payload: dict):
    token = get_telegram_token()
    if not token:
        print("⚠️  TELEGRAM_BOT_TOKEN not set, skipping Telegram")
        return None
    url = f"https://api.telegram.org/bot{token}/{method}"
    data = json.dumps(payload).encode()
    req = urllib.request.Request(
        url, data=data, headers={"Content-Type": "application/json"}
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return json.loads(r.read().decode())
    except Exception as e:  # noqa: BLE001
        print(f"⚠️  tg_api {method} failed: {e}")
        return None


def get_updates(offset: int) -> list:
    resp = tg_api(
        "getUpdates",
        {"offset": offset, "timeout": 5, "allowed_updates": ["message"]},
    )
    if not resp or not resp.get("ok"):
        return []
    return resp["result"]


def send_msg(text: str, reply_to: int | None = None) -> int | None:
    payload = {"chat_id": CHAT_ID, "text": text}
    if reply_to:
        payload["reply_to_message_id"] = reply_to
    resp = tg_api("sendMessage", payload)
    if resp and resp.get("ok"):
        return resp["result"]["message_id"]
    return None


# --------------------------------------------------------------------------- #
# State files
# --------------------------------------------------------------------------- #
def load_offset() -> int:
    try:
        return json.loads(OFFSET_FILE.read_text(encoding="utf-8"))["offset"]
    except Exception:
        return 0


def save_offset(o: int) -> None:
    OFFSET_FILE.write_text(json.dumps({"offset": o}), encoding="utf-8")


def load_pending() -> dict | None:
    try:
        return json.loads(PENDING_FILE.read_text(encoding="utf-8"))
    except Exception:
        return None


def save_pending(p: dict | None) -> None:
    if p is None:
        PENDING_FILE.unlink(missing_ok=True)
    else:
        PENDING_FILE.write_text(
            json.dumps(p, ensure_ascii=False, indent=2), encoding="utf-8"
        )


# --------------------------------------------------------------------------- #
# Parse / draft / write
# --------------------------------------------------------------------------- #
def extract_sleep(text: str) -> dict | None:
    body = text.replace(TAG, "", 1).strip()
    parsed = ps.parse_all_sleep_logs(body)
    return parsed[0] if parsed else None


def build_draft(data: dict) -> str:
    insight = ps.generate_insight(data)
    bp = f" | BP: {data['bp']}" if data.get("bp") else ""
    return (
        f"📋 Draft [capture-sleep] {data['date']}:\n"
        f"Sleep: {data['sleep']} | Quality: {data['quality']}/100 | "
        f"Fasting: {data['fasting']} | Weight: {data['weight']}{bp}\n"
        f"Insight: {insight}\n"
        f"👉 Reply 'ok' để ghi vault, 'skip' để bỏ."
    )


def write_vault(data: dict) -> None:
    entry = ps.build_entry(data, "telegram:@LUsinePersonalBot")
    ps.append_to_sleep_log([entry])


def sync_and_commit(date: str) -> None:
    try:
        n = ps.sync_to_gsheet(send_notify=False)
        print(f"✅ GSheet sync: {n} row(s)")
    except Exception as e:  # noqa: BLE001
        print(f"⚠️  GSheet sync failed: {e}")

    try:
        subprocess.run(
            ["git", "add", str(SLEEP_LOG)],
            cwd=str(VAULT_ROOT),
            capture_output=True,
            text=True,
            check=False,
        )
        msg = f"feat(health): telegram [capture-sleep] {date} + GSheet sync (auto)"
        r = subprocess.run(
            ["git", "commit", "-m", msg],
            cwd=str(VAULT_ROOT),
            capture_output=True,
            text=True,
            check=False,
        )
        if r.returncode == 0:
            subprocess.run(
                ["git", "push"],
                cwd=str(VAULT_ROOT),
                capture_output=True,
                text=True,
                check=False,
            )
            print(f"✅ Git committed+pushed {date}")
        else:
            out = (r.stdout or r.stderr).strip()
            print(f"⚠️  Git commit skipped: {out}")
    except Exception as e:  # noqa: BLE001
        print(f"⚠️  Git failed: {e}")


# --------------------------------------------------------------------------- #
# Handlers
# --------------------------------------------------------------------------- #
def process_new_message(update: dict) -> None:
    message = update.get("message") or {}
    text = message.get("text", "")
    if TAG not in text:
        return  # ignore non-tagged messages
    data = extract_sleep(text)
    if not data:
        send_msg(
            "⚠️ Không parse được sleep data. Format chuẩn:\n"
            "[capture-sleep] Health log jul 25: 🏥 Health: 7h30 | quality 88 | "
            "62kg | 18h | Huyết áp: 99/71",
            reply_to=message.get("message_id"),
        )
        return
    # --- ACKNOWLEDGE: luôn báo nhận ngay khi parse được (TRƯỚC dup-check) ---
    ack = send_msg(
        f"✅ Đã nhận [capture-sleep] {data['date']} — đang xử lý...",
        reply_to=message.get("message_id"),
    )
    if not ack:
        print(f"⚠️ ACK send failed for {data['date']} (token/env issue?)")
    if ps.is_duplicate(SLEEP_LOG.read_text(encoding="utf-8"), data)[0]:
        send_msg(
            f"⚠️ Ngày {data['date']} đã có trong vault, bỏ qua (không tạo draft).",
            reply_to=message.get("message_id"),
        )
        return
    draft = build_draft(data)
    mid = send_msg(draft, reply_to=message.get("message_id"))
    if mid:
        save_pending(
            {
                "status": "awaiting_approval",
                "proposal_msg_id": mid,
                "source_msg_id": message.get("message_id"),
                "data": data,
                "ts": datetime.now().isoformat(),
            }
        )
        print(f"✅ Proposed draft for {data['date']}, awaiting approval")


def process_reply(updates: list) -> None:
    pending = load_pending()
    if not pending or pending.get("status") != "awaiting_approval":
        return
    prop_id = pending["proposal_msg_id"]
    for u in updates:
        m = u.get("message", {})
        if m.get("reply_to_message_id") == prop_id:
            txt = (m.get("text", "") or "").strip().lower()
            if txt == "ok":
                write_vault(pending["data"])
                send_msg(
                    f"✅ Đã ghi vault {pending['data']['date']} + sync GSheet + git push.",
                    reply_to=prop_id,
                )
                sync_and_commit(pending["data"]["date"])
                save_pending(None)
                return
            elif txt == "skip":
                send_msg("⏭️ Đã bỏ qua.", reply_to=prop_id)
                save_pending(None)
                return
            # any other text -> ignore, keep waiting


def poll_once() -> None:
    offset = load_offset()
    updates = get_updates(offset)
    # allow manual recoverability for stuck pending without deleting state
    if not updates:
        return
    process_reply(updates)
    for u in updates:
        process_new_message(u)
    new_offset = max(u["update_id"] for u in updates) + 1
    save_offset(new_offset)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--once", action="store_true", help="single poll cycle")
    ap.add_argument(
        "--dry-run", action="store_true", help="parse sample, no writes/sends"
    )
    args = ap.parse_args()

    if args.dry_run:
        sample = (
            "[capture-sleep] Health log jul 25: 🏥 Health: 7h30 | quality 88 | "
            "62kg | 18h | Huyết áp: 99/71"
        )
        d = extract_sleep(sample)
        print("PARSED:", d)
        print("DRAFT:\n", build_draft(d) if d else "NONE")
        return

    poll_once()


if __name__ == "__main__":
    main()
