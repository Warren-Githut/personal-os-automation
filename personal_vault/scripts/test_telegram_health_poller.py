#!/usr/bin/env python3
"""TDD tests for telegram_health_poller.process_reply() flexible matching.

Run: pytest test_telegram_health_poller.py -v
Or:  python3 test_telegram_health_poller.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import telegram_health_poller as p

# ---- recorders (avoid real Telegram / vault writes) ----
CALLS = {"send": [], "write": [], "sync": []}


def fake_send(text, reply_to=None):
    CALLS["send"].append((text, reply_to))
    return 99999


def fake_write(data):
    CALLS["write"].append(data)


def fake_sync(date):
    CALLS["sync"].append(date)


p.send_msg = fake_send
p.write_vault = fake_write
p.sync_and_commit = fake_sync


def _seed_pending(prop_id=177, src_id=175):
    for k in CALLS:
        CALLS[k] = []
    pending = {
        "status": "awaiting_approval",
        "proposal_msg_id": prop_id,
        "source_msg_id": src_id,
        "data": {
            "date": "2026-07-30",
            "sleep": "7h30",
            "quality": "90",
            "weight": "62kg",
            "fasting": "18h",
            "bp": "97/71",
        },
        "ts": "2026-07-31T08:10:45.184704",
    }
    p.save_pending(pending)
    return pending


def test_reply_match_source_msgid_with_emoji():
    """RED: reply to source_msg_id (175) with emoji text must be approved."""
    _seed_pending()
    updates = [
        {
            "update_id": 9001,
            "message": {
                "message_id": 500,
                "reply_to_message_id": 175,  # source, NOT proposal
                "text": "ok 👍",
            },
        }
    ]
    p.process_reply(updates)
    assert CALLS["write"], "write_vault should fire for flexible reply match"
    assert p.load_pending() is None, "pending must be cleared after approve"


def test_reply_whitespace_only_ok():
    """RED: '  ok  ' with trailing/leading spaces must approve."""
    _seed_pending()
    updates = [
        {
            "update_id": 9002,
            "message": {
                "message_id": 501,
                "reply_to_message_id": 177,
                "text": "  ok  ",
            },
        }
    ]
    p.process_reply(updates)
    assert CALLS["write"], "write_vault should fire for whitespace-padded ok"
    assert p.load_pending() is None


def test_reply_skip_variant():
    """RED: 'skip' reply (any casing/emoji) must discard."""
    _seed_pending()
    updates = [
        {
            "update_id": 9003,
            "message": {
                "message_id": 502,
                "reply_to_message_id": 177,
                "text": "Skip ✅",
            },
        }
    ]
    p.process_reply(updates)
    assert not CALLS["write"], "write_vault must NOT fire on skip"
    assert p.load_pending() is None, "pending cleared on skip"


def test_timeout_fallback_no_updates():
    """GREEN: pending >30min with no new updates -> auto-approve."""
    _seed_pending()
    # backdate ts >30 min
    pend = p.load_pending()
    pend["ts"] = "2020-01-01T00:00:00"
    p.save_pending(pend)
    p.poll_once()
    assert CALLS["write"], "timeout fallback must write_vault"
    assert p.load_pending() is None


def test_timeout_fallback_new_message_same_chat():
    """GREEN: pending >30min + new msg same chat/date -> auto-approve."""
    _seed_pending()
    pend = p.load_pending()
    pend["ts"] = "2020-01-01T00:00:00"
    pend["chat_id"] = 2117653672
    p.save_pending(pend)
    updates = [
        {
            "update_id": 9100,
            "message": {
                "message_id": 600,
                "chat": {"id": 2117653672},
                "text": "[capture-sleep] Health log 2026-07-30: something",
            },
        }
    ]
    p.process_reply(updates)
    # not matched by reply logic, but poll_once fallback should catch
    p.poll_once.__wrapped__ if hasattr(p.poll_once, "__wrapped__") else None
    # emulate get_updates returning our fake by monkeypatching
    orig = p.get_updates
    p.get_updates = lambda off: updates
    try:
        p.poll_once()
    finally:
        p.get_updates = orig
    assert CALLS["write"], "timeout+new-msg fallback must write_vault"
    assert p.load_pending() is None


if __name__ == "__main__":
    # minimal runner without pytest
    tests = [
        test_reply_match_source_msgid_with_emoji,
        test_reply_whitespace_only_ok,
        test_reply_skip_variant,
        test_timeout_fallback_no_updates,
        test_timeout_fallback_new_message_same_chat,
    ]
    failed = 0
    for t in tests:
        try:
            t()
            print(f"PASS {t.__name__}")
        except AssertionError as e:
            failed += 1
            print(f"FAIL {t.__name__}: {e}")
        finally:
            p.save_pending(None)  # cleanup
    print(f"RESULT: {'RED' if failed else 'GREEN'} ({len(tests)-failed}/{len(tests)} passed)")
    sys.exit(1 if failed else 0)
