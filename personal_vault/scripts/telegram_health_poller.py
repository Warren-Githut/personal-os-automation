#!/usr/bin/env python3
"""
Telegram Health Poller — poll [capture-sleep] messages, confirm, append to sleep log.

Modes:
  --dry-run    Preview only: parse + show, no writes, no Telegram sends
  --once       Run one full cycle (poll → propose → check reply → append)

Cron mode (no flag): chạy tự động mỗi 2 phút via cron.
"""
import argparse
import json
import re
import sys
import urllib.request
from datetime import datetime, timedelta
from pathlib import Path

# ──────────────────────────────────────────────────────────────────────────────
# CONFIG
# ──────────────────────────────────────────────────────────────────────────────
VAULT_ROOT = Path("C:/Users/khoans/Documents/Personal_OS/personal_vault")
SCRIPTS_DIR = VAULT_ROOT / "scripts"
SLEEP_LOG = VAULT_ROOT / "10_PULSE" / "051_Sleep_Log.md"
PENDING_FILE = SCRIPTS_DIR / ".telegram_pending.json"
OFFSET_FILE = SCRIPTS_DIR / ".telegram_offset.txt"
CHAT_ID = "2117653672"
POLL_TIMEOUT_MIN = 30
CAPTURE_TAG = "[capture-sleep]"

sys.path.insert(0, str(SCRIPTS_DIR))

from telegram_notify import get_telegram_token
from process_sleep import (
    parse_all_sleep_logs, build_entry, is_duplicate,
    append_to_sleep_log, generate_insight
)


# ──────────────────────────────────────────────────────────────────────────────
# TELEGRAM API
# ──────────────────────────────────────────────────────────────────────────────
def fetch_updates(token: str, offset: int = 0) -> tuple[list[dict], int]:
    """Poll Telegram for new messages. Returns (updates, new_offset)."""
    poll_timeout = 10  # long-poll seconds

    def _do_poll(timeout: int) -> tuple[list[dict], int]:
        url = f"https://api.telegram.org/bot{token}/getUpdates"
        params = {"offset": offset, "timeout": timeout}
        url += "?" + "&".join(f"{k}={v}" for k, v in params.items())
        try:
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=timeout + 5) as resp:
                data = json.loads(resp.read())
            if not data.get("ok"):
                print(f"⚠️  Telegram API returned ok=false: {data}", file=sys.stderr)
                return [], offset
            result = data["result"]
            if not result:
                return [], offset
            new_offset = result[-1]["update_id"] + 1
            return result, new_offset
        except urllib.error.HTTPError as e:
            if e.code == 409:
                raise  # re-raise for retry logic
            print(f"⚠️  HTTP {e.code} polling Telegram: {e}", file=sys.stderr)
            return [], offset
        except urllib.error.URLError as e:
            print(f"⚠️  Network error polling Telegram: {e}", file=sys.stderr)
            return [], offset
        except json.JSONDecodeError as e:
            print(f"⚠️  Invalid JSON from Telegram: {e}", file=sys.stderr)
            return [], offset
        except Exception as e:
            print(f"⚠️  Poll failed: {e}", file=sys.stderr)
            return [], offset

    # Try long-poll first, fallback to short-poll on 409 Conflict
    try:
        return _do_poll(poll_timeout)
    except urllib.error.HTTPError as e:
        if e.code == 409:
            print("⚠️  409 Conflict (stale long-poll), retrying with short poll...", file=sys.stderr)
            return _do_poll(0)
        return [], offset


def send_telegram_msg(token: str, text: str, reply_to: int | None = None) -> int | None:
    """Send message to Warren via Telegram. Returns message_id or None."""
    payload = {"chat_id": CHAT_ID, "text": text}
    if reply_to:
        payload["reply_to_message_id"] = reply_to

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    try:
        data = json.dumps(payload).encode()
        req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            result = json.loads(resp.read())
            return result.get("result", {}).get("message_id")
    except urllib.error.URLError as e:
        print(f"⚠️  Network error sending Telegram: {e}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"⚠️  Send failed: {e}", file=sys.stderr)
        return None


# ──────────────────────────────────────────────────────────────────────────────
# MESSAGE FILTERS
# ──────────────────────────────────────────────────────────────────────────────
def is_from_warner(update: dict) -> bool:
    """Check if update is from Warren's chat."""
    chat = update.get("message", {}).get("chat", {})
    return str(chat.get("id")) == CHAT_ID


def has_capture_tag(update: dict) -> bool:
    """Check if message contains [capture-sleep] tag."""
    text = update.get("message", {}).get("text", "")
    return CAPTURE_TAG.lower() in text.lower()


def get_message_text(update: dict) -> str:
    """Get message text safely."""
    return update.get("message", {}).get("text", "")


def get_message_id(update: dict) -> int:
    """Get message_id from update."""
    return update.get("message", {}).get("message_id", 0)


def is_reply_to_proposal(update: dict, pending: dict) -> int | None:
    """Check if this update is a reply to a pending proposal.
    Returns the index in pending['entries'] or None."""
    msg = update.get("message", {})
    reply_to = msg.get("reply_to_message_id")
    if not reply_to:
        return None
    for i, entry in enumerate(pending.get("entries", [])):
        if entry.get("proposal_message_id") == reply_to:
            return i
    return None


# ──────────────────────────────────────────────────────────────────────────────
# PENDING STATE
# ──────────────────────────────────────────────────────────────────────────────
def load_pending() -> dict:
    """Load pending state with corrupt-file recovery."""
    if not PENDING_FILE.exists():
        return {"entries": []}
    try:
        return json.loads(PENDING_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        print("⚠️  Pending file corrupt, resetting", file=sys.stderr)
        corrupt = PENDING_FILE.with_suffix(".json.corrupt")
        try:
            PENDING_FILE.rename(corrupt)
        except Exception:
            PENDING_FILE.unlink(missing_ok=True)
        return {"entries": []}


def save_pending(state: dict):
    """Atomic write: .tmp → rename."""
    tmp = PENDING_FILE.with_suffix(".tmp")
    tmp.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.rename(PENDING_FILE)


def add_pending(metrics: dict, draft: str, original_msg_id: int, proposal_msg_id: int | None = None):
    """Add a pending confirmation entry."""
    state = load_pending()
    # Remove any existing pending for same date
    state["entries"] = [e for e in state["entries"] if e.get("date") != metrics["date"]]
    state["entries"].append({
        "date": metrics["date"],
        "draft": draft,
        "metrics": metrics.copy(),
        "status": "awaiting",
        "created_at": datetime.now().isoformat(),
        "original_message_id": original_msg_id,
        "proposal_message_id": proposal_msg_id,
    })
    save_pending(state)


def remove_pending_by_idx(idx: int):
    """Remove a pending entry by index."""
    state = load_pending()
    if 0 <= idx < len(state["entries"]):
        state["entries"].pop(idx)
        save_pending(state)


def cleanup_stale_pending() -> int:
    """Remove pending entries older than POLL_TIMEOUT_MIN. Returns count removed."""
    state = load_pending()
    cutoff = datetime.now() - timedelta(minutes=POLL_TIMEOUT_MIN)
    before = len(state["entries"])
    state["entries"] = [
        e for e in state["entries"]
        if datetime.fromisoformat(e["created_at"]) > cutoff
    ]
    if len(state["entries"]) != before:
        save_pending(state)
    return before - len(state["entries"])


# ──────────────────────────────────────────────────────────────────────────────
# OFFSET TRACKING
# ──────────────────────────────────────────────────────────────────────────────
def read_offset() -> int:
    """Read last processed update_id offset."""
    if OFFSET_FILE.exists():
        try:
            return int(OFFSET_FILE.read_text().strip())
        except (ValueError, OSError):
            return 0
    return 0


def write_offset(offset: int):
    """Write offset atomically."""
    tmp = OFFSET_FILE.with_suffix(".tmp")
    tmp.write_text(str(offset))
    tmp.rename(OFFSET_FILE)


# ──────────────────────────────────────────────────────────────────────────────
# REPLY PARSING
# ──────────────────────────────────────────────────────────────────────────────
def parse_reply(text: str) -> tuple[str, str | None]:
    """Parse Warren's reply. Returns (action, edit_text).
    action: 'ok', 'edit', 'skip', or 'unknown'
    """
    text = text.strip().lower()
    if text == "ok":
        return "ok", None
    if text == "skip":
        return "skip", None
    if text.startswith("edit"):
        edit_content = text[4:].strip()
        if edit_content:
            return "edit", edit_content
        return "unknown", None
    return "unknown", None


def apply_edit(metrics: dict, edit_text: str) -> dict:
    """Apply edit overrides to metrics. Returns new metrics dict."""
    edited = dict(metrics)
    edit_lower = edit_text.lower()

    # Override sleep: "sleep 6h" or "ngủ 6h"
    m = re.search(r'(?:ngủ|sleep|ngu)\s*([\dh]+)', edit_lower)
    if m:
        edited['sleep'] = m.group(1).strip()

    # Override quality: "quality 60" or "chất lượng 60"
    m = re.search(r'(?:quality|chất lượng|chat luong)\s*(\d+)', edit_lower)
    if m:
        edited['quality'] = m.group(1)

    # Override weight: "weight 62" or "cân 62"
    m = re.search(r'(?:weight|cân|can)\s*([\d.]+)\s*(?:kg)?', edit_lower)
    if m:
        edited['weight'] = m.group(1) + 'kg'

    # Override fasting: "fasting 16h" or "nhịn 16h"
    m = re.search(r'(?:fasting|nhịn|nhin|fast)\s*(\d+)h?', edit_lower)
    if m:
        edited['fasting'] = m.group(1) + 'h'

    # Override BP: "bp 100/70" or "huyết áp 100/70"
    m = re.search(r'(?:bp|huyết áp|huyet ap|huyetap)\s*(\d+/\d+)', edit_lower)
    if m:
        edited['bp'] = m.group(1)

    return edited


# ──────────────────────────────────────────────────────────────────────────────
# PROPOSAL
# ──────────────────────────────────────────────────────────────────────────────
def build_proposal_text(metrics: dict) -> str:
    """Build proposal message text for Telegram."""
    insight = generate_insight(metrics)
    bp_line = f" | Blood pressure: {metrics['bp']}" if metrics.get('bp') else ""

    return (
        f"📋 {CAPTURE_TAG} Draft:\n"
        f"━━━\n"
        f"Sleep: {metrics['sleep']} | Quality: {metrics['quality']}/100 | "
        f"Fasting: {metrics['fasting']} | Weight: {metrics['weight']}{bp_line}\n\n"
        f"Insight:\n{insight}\n"
        f"━━━\n"
        f"👉 Reply:\n"
        f"• \"ok\" → append ngay\n"
        f"• \"edit [nội dung]\" → chỉnh theo edit\n"
        f"• \"skip\" → huỷ, ko ghi"
    )


def confirm_and_append(metrics: dict, draft: str, edit_text: str | None = None) -> str:
    """Confirm entry: optionally edit, then append to sleep log.
    Returns status message.
    """
    if edit_text:
        edited = apply_edit(metrics, edit_text)
        draft = build_entry(edited, source_file="telegram_bot")
        status = "✅ Updated & appended!"
    else:
        edited = metrics
        status = "✅ Done!"

    # Check duplicate one more time
    log_content = SLEEP_LOG.read_text(encoding="utf-8") if SLEEP_LOG.exists() else ""
    dup, key = is_duplicate(log_content, edited)
    if dup:
        return f"⚠️ Skipped: {key} already exists in log"

    count = append_to_sleep_log([draft])
    if count == 0:
        return "⚠️ Nothing appended (error in append_to_sleep_log)"

    return status


# ──────────────────────────────────────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="Telegram Health Poller")
    parser.add_argument("--dry-run", action="store_true",
                        help="Preview only: parse + show, no writes, no sends")
    parser.add_argument("--once", action="store_true",
                        help="Run one full cycle, then exit")
    args = parser.parse_args()

    DRY_RUN = args.dry_run

    # ── Token ──
    token = get_telegram_token()
    if not token:
        print("❌ No Telegram token found. Check LUsinePersonalBot/.env", file=sys.stderr)
        sys.exit(1)
    print(f"{'🔍 DRY RUN — ' if DRY_RUN else ''}🚀 Telegram Health Poller")

    # ── Offset ──
    offset = read_offset()
    print(f"📡 Offset: {offset}")

    # ── Poll ──
    updates, new_offset = fetch_updates(token, offset)
    print(f"📡 Polled: {len(updates)} new message(s)")
    for u in updates:
        mid = get_message_id(u)
        text = get_message_text(u)
        print(f"  [msg_id={mid}] text={text[:80]}")

    # ── Process each update ──
    pending = load_pending()
    stale_count = cleanup_stale_pending()
    if stale_count:
        print(f"  🧹 Cleaned {stale_count} stale pending entry(ies)")

    for update in updates:
        msg_text = get_message_text(update)
        msg_id = get_message_id(update)

        # 1) Not from Warren → skip
        if not is_from_warner(update):
            print(f"  ⏭️ [msg_id={msg_id}] Not from Warren's chat")
            continue

        # 2) Check if this is a reply to a pending proposal
        pending_idx = is_reply_to_proposal(update, pending)
        if pending_idx is not None:
            action, edit_text = parse_reply(msg_text)
            entry = pending["entries"][pending_idx]
            print(f"  💬 [msg_id={msg_id}] Reply to proposal: action='{action}'")

            if action == "ok":
                if DRY_RUN:
                    print(f"    📋 Would append:\n{entry['draft']}\n")
                else:
                    status = confirm_and_append(entry["metrics"], entry["draft"])
                    send_telegram_msg(token, status, reply_to=msg_id)
                    print(f"    ✅ {status}")
                remove_pending_by_idx(pending_idx)

            elif action == "edit":
                if DRY_RUN:
                    edited = apply_edit(entry["metrics"], edit_text)
                    new_draft = build_entry(edited, source_file="telegram_bot")
                    print(f"    📋 Would append (edited):\n{new_draft}\n")
                else:
                    status = confirm_and_append(entry["metrics"], entry["draft"], edit_text=edit_text)
                    send_telegram_msg(token, status, reply_to=msg_id)
                    print(f"    ✅ {status}")
                remove_pending_by_idx(pending_idx)

            elif action == "skip":
                if not DRY_RUN:
                    send_telegram_msg(token, "⏭️ Skipped, nothing written.", reply_to=msg_id)
                print(f"    ⏭️ Skipped")
                remove_pending_by_idx(pending_idx)

            else:
                msg = (
                    f"❓ Mình không hiểu reply này.\n"
                    f"Reply:\n"
                    f"• \"ok\" → append\n"
                    f"• \"edit [nội dung]\" → chỉnh rồi append\n"
                    f"• \"skip\" → huỷ"
                )
                if not DRY_RUN:
                    send_telegram_msg(token, msg, reply_to=msg_id)
                print(f"    ❓ Unknown reply: '{msg_text[:50]}'")

            # Reload pending after mutation
            pending = load_pending()
            continue

        # 3) Check if has [capture-sleep] tag
        if not has_capture_tag(update):
            print(f"  ⏭️ [msg_id={msg_id}] No {CAPTURE_TAG} tag")
            continue

        print(f"  📝 [msg_id={msg_id}] Processing: {msg_text[:80]}...")

        # 4) Parse health metrics
        metrics_list = parse_all_sleep_logs(msg_text)
        if not metrics_list:
            msg = (
                f"⚠️ Không parse được health data từ:\n{msg_text[:200]}\n\n"
                f"Vui lòng gửi đúng format:\n"
                f"{CAPTURE_TAG} Health log <tháng ngày>: 🏥 Health: <sleep> | "
                f"quality <N> | <kg> | <h> | Huyết áp: <BP>"
            )
            if not DRY_RUN:
                send_telegram_msg(token, msg, reply_to=msg_id)
            print(f"    ⚠️  Could not parse")
            continue

        for metrics in metrics_list:
            print(f"    ✅ Parsed: {metrics['date']} | Sleep: {metrics['sleep']} | "
                  f"Quality: {metrics['quality']} | Weight: {metrics['weight']} | "
                  f"Fasting: {metrics['fasting']} | BP: {metrics.get('bp', 'N/A')}")

            # Check duplicate
            log_content = SLEEP_LOG.read_text(encoding="utf-8") if SLEEP_LOG.exists() else ""
            dup, key = is_duplicate(log_content, metrics)
            if dup:
                print(f"    ⏭️ Duplicate: {key} already exists")
                continue

            # Check if already pending for this date
            already_pending = any(
                e.get("date") == metrics["date"] and e.get("status") == "awaiting"
                for e in pending.get("entries", [])
            )
            if already_pending:
                print(f"    ⏭️ Already pending for {metrics['date']}")
                continue

            # Generate draft
            draft = build_entry(metrics, source_file="telegram_bot")
            insight = generate_insight(metrics)
            print(f"\n📋 DRAFT:\n{draft}\n")
            print(f"💡 Insight: {insight}")

            # Send proposal
            proposal_text = build_proposal_text(metrics)
            if DRY_RUN:
                print(f"📲 Would send proposal:\n{proposal_text}\n")
            else:
                proposal_msg_id = send_telegram_msg(token, proposal_text, reply_to=msg_id)
                if proposal_msg_id:
                    add_pending(metrics, draft, msg_id, proposal_msg_id)
                    print(f"    ✅ Proposal sent (msg_id={proposal_msg_id})")
                else:
                    print(f"    ❌ Failed to send proposal")

    # ── Save offset ──
    if new_offset > offset and not DRY_RUN:
        write_offset(new_offset)
        print(f"📡 New offset: {new_offset}")
    elif DRY_RUN:
        print(f"📡 Would save offset: {new_offset}")


if __name__ == "__main__":
    main()
