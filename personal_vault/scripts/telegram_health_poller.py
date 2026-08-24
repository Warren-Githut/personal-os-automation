#!/usr/bin/env python3
"""Telegram health log poller — [capture-sleep] tag capture with confirmation gate.

Polls the personal life bot (1-1 chat) for messages tagged [capture-sleep].
Proposes a draft back to Telegram -> waits for 'ok' / 'skip' reply ->
writes to 051_Sleep_Log.md -> syncs GSheet -> git commit+push (scoped).

Designed for non-interactive cron (no_agent=True). Each poll is a single
cycle: process pending reply (if any), then process new tagged messages.
Confirmation gate is STRICT: the vault is written ONLY on an explicit
'ok'/'yes' from Warren. An expired draft is re-asked a few times, then
cancelled - never auto-approved, never inferred from chat history.

Usage:
  python3 telegram_health_poller.py --once      # single poll cycle
  python3 telegram_health_poller.py --dry-run   # parse sample, no writes/sends
"""

import argparse
import json
import os
import subprocess
import sys
import time
import urllib.request
from datetime import datetime
from pathlib import Path

# Reuse existing parse / write / sync logic from process_sleep.py
sys.path.insert(0, str(Path(__file__).resolve().parent))
import process_sleep as ps  # noqa: E402
from telegram_notify import get_telegram_token, send_telegram, tg_api  # noqa: E402

VAULT_ROOT = Path("C:/Users/khoans/Documents/Personal_OS")
SLEEP_LOG = VAULT_ROOT / "personal_vault" / "10_PULSE" / "051_Sleep_Log.md"
CHAT_ID = "2117653672"
SCRIPTS_DIR = Path(__file__).resolve().parent
OFFSET_FILE = SCRIPTS_DIR / ".telegram_offset.json"
PENDING_FILE = SCRIPTS_DIR / ".telegram_pending.json"
LOCK_FILE = SCRIPTS_DIR / ".telegram_poller.lock"
LOCK_STALE_SEC = 300   # lock older than 5 min = crashed cycle, safe to steal
TAG = "[capture-sleep]"
MAX_REMINDERS = 3        # re-ask an expired draft this many times, then cancel
REMINDER_INTERVAL_MIN = 10  # minimum minutes between two reminders
OK_WORDS = ("ok", "yes", "okay", "y")
# Vietnamese + English rejections. normalize_reply lowercases and KEEPS
# Vietnamese diacritics, so both bare and marked forms are listed.
SKIP_WORDS = (
    "skip", "no", "n", "cancel",
    "ko", "khong", "không",          # không / ko
    "chua", "chưa",                  # chưa
    "huy", "huỷ", "hủy",             # huỷ / hủy
)


# --------------------------------------------------------------------------- #
# Telegram API helpers (stdlib urllib only)
# tg_api / get_telegram_token imported from telegram_notify (single source)
# --------------------------------------------------------------------------- #
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
# Cross-cycle lock (Windows-safe, timestamp-only)
# --------------------------------------------------------------------------- #
_lock_token: str | None = None  # exact lockfile content written by THIS cycle


def acquire_lock() -> bool:
    """Take the poll-cycle lock atomically; False when another holds it.

    Timestamp-staleness only (pure stdlib): on Windows os.kill(pid, 0) is
    NOT a safe liveness probe, so the recorded pid is informational. A lock
    older than LOCK_STALE_SEC belongs to a crashed (or stuck) cycle and is
    stolen: unlinked, then re-created EXCLUSIVELY (O_CREAT|O_EXCL) so two
    simultaneous starters cannot both win. Fail-open: if the state dir
    refuses all lock ops we continue unlocked - a broken state dir must
    never permanently silence the poller.
    """
    global _lock_token
    try:
        if LOCK_FILE.exists():
            try:
                age = time.time() - LOCK_FILE.stat().st_mtime
            except FileNotFoundError:
                age = None  # vanished between exists() and stat(): benign race
            if age is not None and age < LOCK_STALE_SEC:
                return False  # another cycle is (probably) still running
            try:
                LOCK_FILE.unlink()  # steal the stale lock
            except FileNotFoundError:
                pass  # another thief got there first; exclusive create decides
        _lock_token = json.dumps(
            {"pid": os.getpid(), "ts": datetime.now().isoformat()}
        )
        fd = os.open(str(LOCK_FILE), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(_lock_token)
        return True
    except FileExistsError:
        _lock_token = None  # lost the create race: the winner owns the lock
        return False
    except OSError:
        print("⚠️ Lockfile unusable - continuing WITHOUT lock (fail-open)")
        return True


def release_lock() -> None:
    """Release ONLY if this cycle still owns the lock (exact content match).

    Never deletes a fresher lock: if our cycle overran LOCK_STALE_SEC and
    another cycle stole the lock, deleting on exit would strip the thief's
    protection and admit a third concurrent cycle (theft-cascade bug).
    Best-effort: never raises into the caller.
    """
    global _lock_token
    try:
        if _lock_token is not None and LOCK_FILE.exists() \
                and LOCK_FILE.read_text(encoding="utf-8") == _lock_token:
            LOCK_FILE.unlink()
        _lock_token = None
    except OSError as e:
        print(f"⚠️ Could not remove lockfile: {e}")


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


def write_vault(data: dict) -> bool:
    """Write the entry to 051_Sleep_Log.md, guarded against duplicates.

    Completion criterion: returns True when the log gains exactly one new
    dated entry; returns False and writes NOTHING when that date already
    exists (idempotent). Messaging stays with the caller.
    """
    if ps.is_duplicate(SLEEP_LOG.read_text(encoding="utf-8"), data)[0]:
        print(f"⚠️ Dup-guard: {data['date']} already in vault, write skipped")
        return False
    entry = ps.build_entry(data, "telegram:@LUsinePersonalBot")
    ps.append_to_sleep_log([entry])
    return True


def sync_and_commit(date: str) -> dict:
    """Run GSheet sync + scoped git commit. Returns a TRUTHFUL result dict;
    messaging decisions belong to the caller (never claim before knowing).
    """
    result = {"gsheet_synced": None, "gsheet_error": None,
              "committed": False, "pushed": False, "git_error": None}
    # GSheet sync — FAIL LOUD, do not swallow (Bố must know if GSheet missed)
    try:
        n = ps.sync_to_gsheet(send_notify=False)
        result["gsheet_synced"] = n
        if not n:
            result["gsheet_error"] = "sync trả 0 row (check token/API/share)"
    except Exception as e:  # noqa: BLE001
        result["gsheet_error"] = str(e)

    try:
        subprocess.run(
            ["git", "add", str(SLEEP_LOG)],
            cwd=str(VAULT_ROOT),
            capture_output=True,
            text=True,
            check=False,
        )
        # Commit message states only what git does - never promises GSheet.
        msg = f"feat(health): telegram [capture-sleep] {date} (auto)"
        r = subprocess.run(
            ["git", "commit", "-m", msg],
            cwd=str(VAULT_ROOT),
            capture_output=True,
            text=True,
            check=False,
        )
        if r.returncode == 0:
            result["committed"] = True
            # Hard timeout: a hung push (slow VPN / credential prompt) must
            # not pin the cycle open past the poller's stale-lock window.
            pr = subprocess.run(
                ["git", "push"],
                cwd=str(VAULT_ROOT),
                capture_output=True,
                text=True,
                check=False,
                timeout=60,
            )
            result["pushed"] = pr.returncode == 0
            if pr.returncode != 0:
                result["git_error"] = ((pr.stderr or pr.stdout).strip() or "push failed")[:200]
        else:
            result["git_error"] = ((r.stdout or r.stderr).strip() or "commit failed")[:200]
    except Exception as e:  # noqa: BLE001
        result["git_error"] = str(e)
    return result


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
    mid = send_msg(draft)  # gửi tin mới đứng riêng (không reply) để Bố thấy rõ trên Telegram
    if mid:
        save_pending(
            {
                "status": "awaiting_approval",
                "proposal_msg_id": mid,
                "source_msg_id": message.get("message_id"),
                "chat_id": message.get("chat", {}).get("id"),
                "data": data,
                "ts": datetime.now().isoformat(),
            }
        )
        print(f"✅ Proposed draft for {data['date']}, awaiting approval")


def normalize_reply(text: str) -> str:
    """Lowercase, strip whitespace, drop emoji/symbols → bare word.

    Vietnamese diacritics are PRESERVED ('không' stays 'không'), so
    SKIP_WORDS lists both bare ASCII and diacritic forms.
    'ok 👍' -> 'ok', '  Skip ✅ ' -> 'skip', 'YES' -> 'yes'
    """
    if not text:
        return ""
    # keep only letters/digits, lowercase
    cleaned = "".join(ch for ch in text.lower() if ch.isalnum())
    return cleaned


def process_reply(updates: list) -> None:
    pending = load_pending()
    if not pending or pending.get("status") != "awaiting_approval":
        return
    prop_id = pending["proposal_msg_id"]
    src_id = pending.get("source_msg_id")
    chat_id = pending.get("chat_id")
    for u in updates:
        m = u.get("message", {})
        rid = m.get("reply_to_message_id")
        # match reply to EITHER the proposal OR the original source message
        is_reply_match = rid in (prop_id, src_id)
        # OR standalone confirm from Bố in the same 1-1 chat (root-cause fix)
        is_standalone = (
            rid is None
            and chat_id is not None
            and m.get("chat", {}).get("id") == chat_id
            and not m.get("from", {}).get("is_bot")
        )
        if not (is_reply_match or is_standalone):
            continue
        txt = normalize_reply(m.get("text", "") or "")
        if txt in OK_WORDS:
            if write_vault(pending["data"]):
                res = sync_and_commit(pending["data"]["date"])
                parts = [f"✅ Đã ghi vault {pending['data']['date']}."]
                if res["gsheet_synced"]:
                    parts.append(f"GSheet +{res['gsheet_synced']} row.")
                elif res["gsheet_error"]:
                    parts.append(f"⚠️ GSheet chưa sync: {res['gsheet_error']}")
                else:
                    parts.append("GSheet đã cập nhật sẵn.")
                if res["committed"] and res["pushed"]:
                    parts.append("Git pushed ✓")
                else:
                    parts.append(f"⚠️ Git: {res['git_error'] or 'không commit'}")
                send_msg(" ".join(parts), reply_to=prop_id)
            else:
                # Dup-guard hit: entry already exists, nothing written.
                send_msg(
                    f"⚠️ Ngày {pending['data']['date']} đã có trong vault, "
                    f"bỏ qua (không ghi lần 2).",
                    reply_to=prop_id,
                )
                save_pending(None)
                return
            save_pending(None)
            return
        elif txt in SKIP_WORDS:
            send_msg("⏭️ Đã bỏ qua.", reply_to=prop_id)
            save_pending(None)
            return
        # any other text -> ignore, keep waiting


def pending_timed_out(pending: dict, timeout_min: int = 30) -> bool:
    """True if pending has waited longer than timeout_min."""
    try:
        ts = datetime.fromisoformat(pending["ts"])
    except (KeyError, ValueError):
        return False
    elapsed = (datetime.now() - ts).total_seconds()
    return elapsed > timeout_min * 60


def _minutes_since(ts_str: str | None) -> float | None:
    """Minutes since an ISO timestamp, or None if unparseable."""
    try:
        return (datetime.now() - datetime.fromisoformat(ts_str or "")).total_seconds() / 60
    except (TypeError, ValueError):
        return None


def handle_expired_pending(pending: dict) -> None:
    """Tend an expired draft WITHOUT ever writing the vault.

    Re-ask Warren up to MAX_REMINDERS times (at least REMINDER_INTERVAL_MIN
    apart), then cancel the draft. Completion criterion: pending file ends up
    either refreshed with reminder counters, or deleted - data untouched.
    """
    reminders = int(pending.get("reminders", 0))
    since_last_ask = _minutes_since(pending.get("last_reminder_ts"))
    if since_last_ask is not None and since_last_ask < REMINDER_INTERVAL_MIN:
        return  # asked recently, stay quiet
    age_min = _minutes_since(pending.get("ts")) or 0.0
    prop_id = pending["proposal_msg_id"]
    date = pending["data"]["date"]
    if reminders >= MAX_REMINDERS:
        send_msg(
            f"🗑 Draft {date} đã huỷ sau {MAX_REMINDERS} lần nhắc không thấy 'ok'.\n"
            f"Gửi lại tin [capture-sleep] để tạo draft mới.",
            reply_to=prop_id,
        )
        save_pending(None)
        print(f"🗑 Cancelled expired draft for {date} after {MAX_REMINDERS} reminders")
        return
    send_msg(
        f"⏰ Đã {age_min:.0f} phút, chưa thấy 'ok' cho ngày {date}.\n"
        f"👉 Reply 'ok' để ghi vault, 'skip' để bỏ.",
        reply_to=prop_id,
    )
    save_pending({
        **pending,
        "reminders": reminders + 1,
        "last_reminder_ts": datetime.now().isoformat(),
    })
    print(f"⏰ Reminder #{reminders + 1} sent for {date}")


def poll_once() -> None:
    """Single cron cycle under an overlap guard.

    A FRESH lock (< LOCK_STALE_SEC) means another cycle is mid-flight:
    exit silently (cron just retries next tick). Stale locks are stolen;
    the lock is released in finally - crash or not - but only if this
    cycle still owns it.
    """
    if not acquire_lock():
        # Overlap guard: a cycle CAN exceed the 120s tick - the worst
        # offender is the untimed `git push` in sync_and_commit; tg calls
        # (socket cap 15s) and GSheet subprocesses (60s x2) are bounded.
        print("⏭️ Another poll cycle holds the lock - exiting quietly")
        return
    try:
        _poll_once_locked()
    finally:
        release_lock()


def _poll_once_locked() -> None:
    offset = load_offset()
    updates = get_updates(offset)
    if not updates:
        # No new updates: still tend an expired draft (remind / cancel only).
        pending = load_pending()
        if pending and pending.get("status") == "awaiting_approval" \
                and pending_timed_out(pending):
            handle_expired_pending(pending)
        return
    process_reply(updates)
    for u in updates:
        process_new_message(u)
    # Expired draft without an 'ok' in this batch -> remind / cancel.
    # NEVER writes the vault here - only an explicit 'ok' via process_reply does.
    pending = load_pending()
    if pending and pending.get("status") == "awaiting_approval" \
            and pending_timed_out(pending):
        handle_expired_pending(pending)
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
