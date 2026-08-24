#!/usr/bin/env python3
"""TDD tests for telegram_health_poller confirmation gate (STRICT mode).

Gate contract (2026-08-24 fix): vault is written ONLY on an explicit
'ok'/'yes'. Expiry -> remind up to MAX_REMINDERS then cancel - never write.

Run: pytest test_telegram_health_poller.py -v
Or:  python3 test_telegram_health_poller.py
"""
import tempfile
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import telegram_health_poller as p

# ---- isolate state files into TEMP (never touch real cron state) ----
_TMP = Path(tempfile.mkdtemp(prefix="poller_test_"))
p.OFFSET_FILE = _TMP / "offset.json"
p.PENDING_FILE = _TMP / "pending.json"

# ---- recorders (avoid real Telegram / vault writes) ----
CALLS = {"send": [], "write": [], "sync": []}


def fake_send(text, reply_to=None):
    CALLS["send"].append((text, reply_to))
    return 99999


WRITE_RESULT = {"ok": True}  # flip to False to simulate dup-guard hit


def fake_write(data):
    CALLS["write"].append(data)
    return WRITE_RESULT["ok"]


def fake_sync(date):
    CALLS["sync"].append(date)
    return {"gsheet_synced": 1, "gsheet_error": None,
            "committed": True, "pushed": True, "git_error": None}


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


def test_expired_pending_reminds_never_writes():
    """GREEN: expired draft -> reminder sent, vault NEVER written."""
    _seed_pending()
    pend = p.load_pending()
    pend["ts"] = "2020-01-01T00:00:00"
    p.save_pending(pend)
    orig = p.get_updates
    p.get_updates = lambda off: []  # no new updates branch
    try:
        p.poll_once()
    finally:
        p.get_updates = orig
    assert not CALLS["write"], "expired draft must NEVER write_vault"
    assert CALLS["send"], "expired draft must send a reminder"
    assert p.load_pending() is not None, "draft stays pending after reminder"


def test_expired_after_max_reminders_cancels():
    """GREEN: draft past MAX_REMINDERS -> cancelled, still never written."""
    _seed_pending()
    pend = p.load_pending()
    pend["ts"] = "2020-01-01T00:00:00"
    pend["reminders"] = p.MAX_REMINDERS
    p.save_pending(pend)
    orig = p.get_updates
    p.get_updates = lambda off: []
    try:
        p.poll_once()
    finally:
        p.get_updates = orig
    assert not CALLS["write"], "cancel path must NEVER write_vault"
    assert p.load_pending() is None, "cancelled draft must be deleted"


def test_new_message_with_date_no_longer_autoapproves():
    """RED-turned-GREEN (2026-08-24): a plain message containing the ISO date
    used to auto-approve an expired pending. Now it must NOT write; the
    expired-draft tending sends at most a reminder/cancel."""
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
    orig = p.get_updates
    p.get_updates = lambda off: updates
    try:
        p.poll_once()
    finally:
        p.get_updates = orig
    assert not CALLS["write"], "date-in-text must NOT auto-approve any more"


def test_standalone_ok_approves():
    """RED: Bố gõ 'ok' STANDALONE (không reply thread) phải approve.
    Đây là root cause thực tế — Bố gõ 'ok' không reply vào draft."""
    _seed_pending()
    pend = p.load_pending()
    pend["chat_id"] = 2117653672
    p.save_pending(pend)
    updates = [
        {
            "update_id": 9200,
            "message": {
                "message_id": 800,
                "reply_to_message_id": None,  # standalone, không reply
                "chat": {"id": 2117653672},
                "from": {"id": 2117653672, "is_bot": False},
                "text": "ok",
            },
        }
    ]
    p.process_reply(updates)
    assert CALLS["write"], "standalone 'ok' must approve (root cause fix)"
    assert p.load_pending() is None


def test_standalone_skip_discards():
    """RED: Bố gõ 'skip' STANDALONE phải bỏ qua."""
    _seed_pending()
    pend = p.load_pending()
    pend["chat_id"] = 2117653672
    p.save_pending(pend)
    updates = [
        {
            "update_id": 9201,
            "message": {
                "message_id": 801,
                "reply_to_message_id": None,
                "chat": {"id": 2117653672},
                "from": {"id": 2117653672, "is_bot": False},
                "text": "skip",
            },
        }
    ]
    p.process_reply(updates)
    assert not CALLS["write"], "standalone 'skip' must NOT write"
    assert p.load_pending() is None


def test_standalone_other_text_ignored():
    """GREEN: standalone text không phải ok/skip → giữ pending."""
    _seed_pending()
    pend = p.load_pending()
    pend["chat_id"] = 2117653672
    p.save_pending(pend)
    updates = [
        {
            "update_id": 9202,
            "message": {
                "message_id": 802,
                "reply_to_message_id": None,
                "chat": {"id": 2117653672},
                "from": {"id": 2117653672, "is_bot": False},
                "text": "cái gì thế",
            },
        }
    ]
    p.process_reply(updates)
    assert not CALLS["write"], "non-ok/skip standalone ignored"
    assert p.load_pending() is not None


def test_vietnamese_rejection_skips_immediately():
    """GREEN (2026-08-24): 'không'/'chưa'/'hủy' must cancel the draft
    immediately - previously they fell through and the draft auto-approved
    after 30 minutes."""
    for word in ("không", "chưa", "hủy", "ko"):
        _seed_pending()
        updates = [
            {
                "update_id": 9203,
                "message": {
                    "message_id": 803,
                    "reply_to_message_id": 177,
                    "chat": {"id": 2117653672},
                    "text": word,
                },
            }
        ]
        p.process_reply(updates)
        assert not CALLS["write"], f"'{word}' must NEVER write_vault"
        assert p.load_pending() is None, f"'{word}' must cancel draft now"


def test_ok_reports_after_sync_with_truthful_result():
    """GREEN (2026-08-24 step 2): on 'ok', sync runs BEFORE the Telegram
    report, and the report reflects the real sync result."""
    _seed_pending()
    order = []
    real_write, real_sync = p.write_vault, p.sync_and_commit

    def w(data):
        r = real_write(data)
        order.append("write")
        return r

    def s(date):
        r = real_sync(date)
        order.append("sync")
        return r

    p.write_vault, p.sync_and_commit = w, s
    updates = [{"update_id": 9300, "message": {
        "message_id": 900, "reply_to_message_id": 177,
        "chat": {"id": 2117653672}, "text": "ok"}}]
    try:
        p.process_reply(updates)
    finally:
        p.write_vault, p.sync_and_commit = real_write, real_sync
    assert order == ["write", "sync"], "sync must run before reporting path"
    assert len(CALLS["send"]) == 1, "exactly one report message"
    txt = CALLS["send"][0][0]
    assert "GSheet +1 row" in txt, "report must contain truthful GSheet count"
    assert "Git pushed" in txt, "report must reflect git result"
    assert "+ sync GSheet + git push." not in txt, "no canned success claim"


def test_dup_guard_on_write_vault():
    """GREEN (2026-08-24 step 2): write into a log that already has the date
    must write NOTHING and report 'already in vault' instead of duplicating."""
    _seed_pending()
    WRITE_RESULT["ok"] = False  # simulate dup-guard hit inside real write_vault
    updates = [{"update_id": 9400, "message": {
        "message_id": 910, "reply_to_message_id": 177,
        "chat": {"id": 2117653672}, "text": "ok"}}]
    try:
        p.process_reply(updates)
    finally:
        WRITE_RESULT["ok"] = True
    assert not CALLS["sync"], "dup-guard hit -> no GSheet sync attempted"
    assert any("đã có trong vault" in t for t, _ in CALLS["send"]), \
        "caller must be told the date already exists"


def test_nfd_input_still_parses_bp():
    """GREEN (2026-08-24 step 2): NFD Vietnamese input must still capture BP."""
    import unicodedata
    nfc = ("[capture-sleep] Health log jul 25: Health: 7h30 | quality 88 | "
           "62kg | 18h | Huyết áp: 99/71")
    nfd = unicodedata.normalize("NFD", nfc)
    d = p.extract_sleep(nfd)
    assert d is not None and d["bp"] == "99/71", \
        "NFC normalization must rescue BP from NFD input"


if __name__ == "__main__":
    # minimal runner without pytest
    tests = [
        test_reply_match_source_msgid_with_emoji,
        test_reply_whitespace_only_ok,
        test_reply_skip_variant,
        test_expired_pending_reminds_never_writes,
        test_expired_after_max_reminders_cancels,
        test_new_message_with_date_no_longer_autoapproves,
        test_standalone_ok_approves,
        test_standalone_skip_discards,
        test_standalone_other_text_ignored,
        test_vietnamese_rejection_skips_immediately,
        test_ok_reports_after_sync_with_truthful_result,
        test_dup_guard_on_write_vault,
        test_nfd_input_still_parses_bp,
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
