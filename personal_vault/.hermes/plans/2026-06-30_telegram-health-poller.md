# Implementation Plan: Telegram Health Poller

> **For Hermes:** Build incrementally slice-by-slice. Code review gate sau mỗi slice trước khi merge.

**Goal:** Warren gửi `[capture-sleep]` + health data vào Telegram → Hermes auto-parse → propose draft → confirm (ok/edit/skip) → append vào `051_Sleep_Log.md`.

**Architecture:** Poll-based Python script (stdlib + Telegram HTTP API), state machine qua JSON file, cron 2 phút. Import existing `process_sleep.py` cho parse + insight logic. Import existing `telegram_notify.py` cho send.

**Tech Stack:** Python 3.14, stdlib only (urllib, json, re, pathlib), git-bash cron.

**Dependency Graph:**
```
telegram_notify.py (existing)    process_sleep.py (existing)
         │                               │
         ▼                               ▼
      telegram_health_poller.py (NEW)
         │
         ▼
    .telegram_pending.json (state)
         │
         ▼
    051_Sleep_Log.md (target)
```

---

## Tasks

### Phase 1: Foundation — Slice 1 (Dry-run: poll + parse)

**Slice 1: Core poll + parse loop (--dry-run)**

**Objective:** Poll Telegram getUpdates, lọc message có `[capture-sleep]`, parse metrics, in ra stdout. KO ghi file, KO send message.

**Files:**
- Create: `scripts/telegram_health_poller.py`
- Read-only: `scripts/process_sleep.py` (dùng SLEEP_PATTERN, MONTH_MAP, parse_all_sleep_logs)
- Read-only: `scripts/telegram_notify.py` (dùng get_telegram_token)

**Acceptance criteria:**
- [ ] `python3 telegram_health_poller.py --dry-run` poll Telegram, in ra messages mới
- [ ] Message có `[capture-sleep]` → parse đúng sleep/quality/weight/fasting/BP
- [ ] Message ko có tag → bỏ qua (in "ignored")
- [ ] Message sai format → báo "⚠️ Could not parse" ko crash
- [ ] Ko ghi vào 051_Sleep_Log.md, ko ghi state file

**Implementation detail:**

```python
#!/usr/bin/env python3
"""
Telegram Health Poller — poll [capture-sleep] messages, confirm, append to sleep log.
"""
import argparse
import json
import os
import re
import sys
import urllib.request
from datetime import datetime, timedelta
from pathlib import Path

# ── Config ──
VAULT_ROOT = Path("C:/Users/khoans/Documents/Personal_OS/personal_vault")
SCRIPTS_DIR = VAULT_ROOT / "scripts"
SLEEP_LOG = VAULT_ROOT / "10_PULSE" / "051_Sleep_Log.md"
PENDING_FILE = SCRIPTS_DIR / ".telegram_pending.json"
CHAT_ID = "2117653672"
POLL_TIMEOUT_MIN = 30

CAPTURE_TAG = "[capture-sleep]"

# Import existing helpers
sys.path.insert(0, str(SCRIPTS_DIR))
from telegram_notify import get_telegram_token, send_telegram
from process_sleep import (
    SLEEP_PATTERN, MONTH_MAP, CURRENT_YEAR,
    parse_all_sleep_logs, build_entry, is_duplicate,
    append_to_sleep_log, generate_insight
)


def fetch_updates(token: str, offset: int = 0) -> tuple[list[dict], int]:
    """Poll Telegram for new messages. Returns (messages, new_offset)."""
    url = f"https://api.telegram.org/bot{token}/getUpdates"
    params = {"offset": offset, "timeout": 10}
    url += "?" + "&".join(f"{k}={v}" for k, v in params.items())
    
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read())
        if not data.get("ok"):
            return [], offset
        result = data["result"]
        if not result:
            return [], offset
        new_offset = result[-1]["update_id"] + 1
        return result, new_offset
    except Exception as e:
        print(f"⚠️  Poll failed: {e}", file=sys.stderr)
        return [], offset


def is_from_warren(msg: dict) -> bool:
    """Check if message is from Warren's chat."""
    chat = msg.get("message", {}).get("chat", {})
    return str(chat.get("id")) == CHAT_ID


def has_capture_tag(msg: dict) -> bool:
    """Check if message contains [capture-sleep] tag."""
    text = msg.get("message", {}).get("text", "")
    return CAPTURE_TAG.lower() in text.lower()


def parse_health_message(text: str) -> list[dict]:
    """Parse [capture-sleep] health log text → list of metric dicts."""
    return parse_all_sleep_logs(text)


def main():
    parser = argparse.ArgumentParser(description="Telegram Health Poller")
    parser.add_argument("--dry-run", action="store_true", help="Preview only, no writes")
    parser.add_argument("--once", action="store_true", help="Run one cycle, then exit")
    args = parser.parse_args()
    
    DRY_RUN = args.dry_run
    
    # Get token
    token = get_telegram_token()
    if not token:
        print("❌ No Telegram token found", file=sys.stderr)
        sys.exit(1)
    
    if DRY_RUN:
        print("🔍 DRY RUN — no files or Telegram will be modified\n")
    
    # Read last offset
    # ... (will be fleshed out in Slice 2)
    
    # Poll
    messages, new_offset = fetch_updates(token)
    print(f"📡 Polled: {len(messages)} new message(s)")
    
    for update in messages:
        msg = update.get("message", {})
        text = msg.get("text", "")
        
        if not is_from_warren(update):
            print(f"  ⏭️ Ignored: not from Warren")
            continue
        
        if not has_capture_tag(update):
            print(f"  ⏭️ Ignored (no tag): {text[:50]}...")
            continue
        
        print(f"  📝 Processing: {text[:80]}...")
        
        metrics_list = parse_health_message(text)
        if not metrics_list:
            print("  ⚠️  Could not parse health metrics from message")
            if not DRY_RUN:
                send_telegram(
                    f"⚠️ Không parse được health data từ:\n{text[:200]}\n\n"
                    f"Anh gửi lại với format:\n"
                    f"{CAPTURE_TAG} Health log <tháng ngày>: 🏥 Health: <sleep> | quality <N> | <kg> | <h> | Huyết áp: <BP>"
                )
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
            
            # Generate draft
            draft = build_entry(metrics, source_file="telegram_bot")
            print(f"\n📋 DRAFT:\n{draft}\n")
            
            insight = generate_insight(metrics)
            print(f"💡 Insight: {insight}")


if __name__ == "__main__":
    main()
```

**Code simplification checks:**
- [x] Preserve behavior: dùng lại `parse_all_sleep_logs`, `build_entry`, `is_duplicate`, `generate_insight` từ process_sleep — ko copy
- [x] Clarity > cleverness: if/else rõ ràng, ko reduce/trick
- [x] Scope to change: chỉ 1 file mới, ko modify existing scripts

**5-axis review:**
- Correctness: parse đúng format hiện tại; edge case message ko có tag, sai format
- Readability: function naming rõ (`fetch_updates`, `is_from_warren`, `has_capture_tag`)
- Architecture: import existing helpers, ko duplicate
- Security: token từ `get_telegram_token()` (đã có sẵn), ko log token
- Performance: 1 request HTTP mỗi lần chạy — negligible

**Verify:** `python3 scripts/telegram_health_poller.py --dry-run`

---

**Slice 2: State file + offset tracking (--dry-run)**

**Objective:** Thêm offset tracking và pending state file (JSON). Vẫn --dry-run, ko send message thật.

**Files:**
- Modify: `scripts/telegram_health_poller.py`
- Create (auto): `scripts/.telegram_pending.json`

**Acceptance criteria:**
- [ ] Offset file lưu update_id → lần chạy sau ko poll lại message cũ
- [ ] Parse `[capture-sleep]` → save pending entry vào `.telegram_pending.json`
- [ ] Pending state có: date, raw_text, draft_entry, status="awaiting", timestamp, original_message_id
- [ ] Pending quá 30 phút → tự cleanup (timeout)
- [ ] `--dry-run` vẫn ko ghi file thật

**Implementation detail — thêm vào main():**

```python
# ── Offset tracking ──
OFFSET_FILE = SCRIPTS_DIR / ".telegram_offset.txt"

def read_offset() -> int:
    if OFFSET_FILE.exists():
        return int(OFFSET_FILE.read_text().strip())
    return 0

def write_offset(offset: int):
    OFFSET_FILE.write_text(str(offset))

# ── Pending state ──

def load_pending() -> dict:
    if PENDING_FILE.exists():
        return json.loads(PENDING_FILE.read_text(encoding="utf-8"))
    return {"entries": []}

def save_pending(state: dict):
    """Atomic write: .tmp → rename."""
    tmp = PENDING_FILE.with_suffix(".tmp")
    tmp.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.rename(PENDING_FILE)

def add_pending(entry: dict, draft: str, original_msg_id: int):
    """Add a pending confirmation entry."""
    state = load_pending()
    # Remove any existing pending for same date
    state["entries"] = [e for e in state["entries"] if e.get("date") != entry["date"]]
    state["entries"].append({
        "date": entry["date"],
        "raw_text": entry.get("_raw", ""),
        "draft": draft,
        "metrics": {k: v for k, v in entry.items() if k != "_raw"},
        "status": "awaiting",
        "created_at": datetime.now().isoformat(),
        "original_message_id": original_msg_id,
        "proposal_message_id": None,
    })
    save_pending(state)

def cleanup_stale_pending():
    """Remove pending entries older than POLL_TIMEOUT_MIN."""
    state = load_pending()
    cutoff = datetime.now() - timedelta(minutes=POLL_TIMEOUT_MIN)
    before = len(state["entries"])
    state["entries"] = [
        e for e in state["entries"]
        if datetime.fromisoformat(e["created_at"]) > cutoff
    ]
    if len(state["entries"]) != before:
        save_pending(state)
        print(f"  🧹 Cleaned up {before - len(state['entries'])} stale pending entry(ies)")
```

**Code simplification checks:**
- [x] Atomic write pattern (giống best practice, tránh corrupt)
- [x] `load_pending` / `save_pending` là pure functions, dễ test
- [x] Ko hardcode path — dùng SCRIPTS_DIR constant từ đầu file

---

### Phase 2: Core — Slice 3 (Send real proposal)

**Slice 3: Gửi proposal thật qua Telegram (--once)**

**Objective:** Khi có `[capture-sleep]` message mới, Hermes gửi proposal draft về Telegram cho Warren. Dùng `send_telegram()` từ `telegram_notify.py`.

**Files:**
- Modify: `scripts/telegram_health_poller.py`

**Acceptance criteria:**
- [ ] Gửi message Telegram: draft entry + "👉 Reply 'ok', 'edit ...', or 'skip'"
- [ ] Lưu `proposal_message_id` vào pending state
- [ ] `--dry-run` ko send thật
- [ ] Nếu đã có pending entry cho date đó → ko gửi proposal mới

**Proposal message format:**
```
📋 [capture-sleep] Draft:
━━━
Sleep: 5h40 | Quality: 54/100 | Fasting: 18h | Weight: 61kg | Blood pressure: 97/70

Insight: Sleep 5h40 thấp hơn baseline 7h...

━━━
👉 Reply:
• "ok" → append ngay
• "edit ngủ 6h, quality 60" → chỉnh theo edit
• "skip" → huỷ, ko ghi
```

**Logic thêm vào:**

```python
def send_proposal(metrics: dict, draft: str) -> int | None:
    """Send proposal to Warren, return message_id if successful."""
    insight = generate_insight(metrics)
    bp_line = f" | Blood pressure: {metrics['bp']}" if metrics.get('bp') else ""
    
    proposal = (
        f"📋 {CAPTURE_TAG} Draft:\n"
        f"━━━\n"
        f"Sleep: {metrics['sleep']} | Quality: {metrics['quality']}/100 | "
        f"Fasting: {metrics['fasting']} | Weight: {metrics['weight']}{bp_line}\n\n"
        f"Insight: {insight}\n"
        f"━━━\n"
        f"👉 Reply:\n"
        f"• \"ok\" → append ngay\n"
        f"• \"edit [nội dung]\" → chỉnh theo edit\n"
        f"• \"skip\" → huỷ, ko ghi"
    )
    
    # Use Telegram API directly to get message_id
    token = get_telegram_token()
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = json.dumps({"chat_id": CHAT_ID, "text": proposal}).encode()
    try:
        req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            result = json.loads(resp.read())
            return result.get("result", {}).get("message_id")
    except Exception as e:
        print(f"⚠️  Send proposal failed: {e}", file=sys.stderr)
        return None
```

---

**Slice 4: Xử lý reply + append vào 051_Sleep_Log.md (--once)**

**Objective:** Đọc reply từ Warren (ok/edit/skip), append entry vào sleep log khi confirmed.

**Files:**
- Modify: `scripts/telegram_health_poller.py`

**Acceptance criteria:**
- [ ] Warren reply "ok" → append draft vào 051_Sleep_Log.md
- [ ] Warren reply "edit sleep 6h | quality 60" → update metrics → generate new draft → append
- [ ] Warren reply "skip" → xoá pending, ko ghi
- [ ] Reply ko phải ok/edit/skip → báo "Please reply ok/edit/skip"
- [ ] Gửi xác nhận "✅ Done!" / "✅ Updated & appended!" / "⏭️ Skipped"
- [ ] Dedup check trước khi append (tránh race condition)

**Detection logic — reply check:**

```python
def is_reply_to_proposal(update: dict, pending: dict) -> bool:
    """Check if this update is a reply to a pending proposal."""
    msg = update.get("message", {})
    reply_to = msg.get("reply_to_message", {})
    reply_msg_id = reply_to.get("message_id")
    
    for entry in pending.get("entries", []):
        if entry.get("proposal_message_id") == reply_msg_id:
            return True
    return False

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
```

**Append flow (khi confirmed):**

```python
def confirm_and_append(metrics: dict, draft: str, edit_text: str | None = None) -> str:
    """Confirm entry: optionally edit, then append to sleep log.
    Returns status message for Telegram.
    """
    # Build final entry
    if edit_text:
        # Apply edit: try to parse override metrics from edit text
        # Format: "edit sleep 6h | quality 60"
        edited = dict(metrics)  # copy
        # Simple override parsing
        edit_lower = edit_text.lower()
        
        # Override sleep: "sleep 6h"
        sleep_m = re.search(r'(?:ngủ|sleep)\s*([\dh]+)', edit_lower)
        if sleep_m:
            edited['sleep'] = sleep_m.group(1).strip()
        
        # Override quality: "quality 60"
        q_m = re.search(r'quality\s*(\d+)', edit_lower)
        if q_m:
            edited['quality'] = q_m.group(1)
        
        # Override weight: "weight 62" or "cân 62"
        w_m = re.search(r'(?:weight|cân)\s*([\d.]+)', edit_lower)
        if w_m:
            edited['weight'] = w_m.group(1) + 'kg'
        
        # Override fasting: "fasting 16h" or "nhịn 16h"
        f_m = re.search(r'(?:fasting|nhịn|fast)\s*(\d+)h?', edit_lower)
        if f_m:
            edited['fasting'] = f_m.group(1) + 'h'
        
        # Override BP: "bp 100/70" or "huyết áp 100/70"
        bp_m = re.search(r'(?:bp|huyết áp|huyet ap)\s*(\d+/\d+)', edit_lower)
        if bp_m:
            edited['bp'] = bp_m.group(1)
        
        draft = build_entry(edited, source_file="telegram_bot")
        status = "✅ Updated & appended!"
    else:
        status = "✅ Done!"
    
    # Append to sleep log
    count = append_to_sleep_log([draft])
    if count == 0:
        return "⚠️ Nothing appended (duplicate?)"
    
    return status
```

---

### Phase 3: Hardening — Slice 5 (Battle test)

**Slice 5: Battle test — stress edge cases**

**Objective:** Test script với loạt input độc hại. Ko crash, xử lý gracefully.

**Test cases (chạy với --dry-run):**

| # | Input | Expected |
|---|-------|----------|
| 1 | `[capture-sleep] Health log june 30: 🏥 Health: 5h40 \| quality 54 \| 61kg \| 18h \| BP 97/70` | Parse OK |
| 2 | `[capture-sleep] Health log june 30: 🏥 Health: bad input` | ⚠️ Parse fail |
| 3 | `Hello world` (no tag) | ⏭️ Ignore |
| 4 | `[capture-sleep]` (empty after tag) | ⚠️ Parse fail |
| 5 | `[capture-sleep] Health log june 30: ...` (duplicate date) | ⏭️ Duplicate |
| 6 | Ko có network → mất kết nối Telegram API | ⚠️ Poll fail, ko crash |
| 7 | State file corrupt (JSON invalid) | Tự reset state, ko crash |
| 8 | 10 message `[capture-sleep]` liên tiếp | Xử lý từng cái, ko overwhelm |
| 9 | Message cực dài (10K chars) | Ko crash, parse phần đầu |
| 10 | Emoji/unicode linh tinh trong message | Ko crash |

**Implementation — thêm resilience:**

```python
def load_pending() -> dict:
    """Load pending state with corrupt-file recovery."""
    if not PENDING_FILE.exists():
        return {"entries": []}
    try:
        return json.loads(PENDING_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        print("⚠️  Pending file corrupt, resetting", file=sys.stderr)
        # Backup corrupt file
        corrupt = PENDING_FILE.with_suffix(".json.corrupt")
        PENDING_FILE.rename(corrupt)
        return {"entries": []}
```

---

### Phase 4: Validation — Slice 6 (A/B test)

**Slice 6: A/B test — Hermes chat vs Telegram output**

**Objective:** Gửi cùng health data qua Hermes chat và Telegram → so sánh output format.

**Test protocol:**
1. Gửi `[capture-sleep] Health log june 30: 🏥 Health: 5h40 | quality 54 | 61kg | 18h | BP 97/70` vào Telegram
2. Confirm "ok" → entry vào 051_Sleep_Log.md
3. Gửi `Health log june 30: 🏥 Health: 5h40 | quality 54 | 61kg | 18h | BP 97/70` vào Hermes chat → capture-sleep
4. So sánh 2 entry trong 051_Sleep_Log.md

**Expected:** Format giống hệt nhau (source khác nhau: `telegram_bot` vs `direct_paste`).

---

### Phase 5: Production — Slice 7 (Cron deploy)

**Slice 7: Deploy cron + monitoring**

**Objective:** Tạo cron job chạy mỗi 2 phút, monitor 24h đầu.

**Files:**
- Create: Cron job `telegram-capture-health`

**Cron config:**
```bash
# Cron job:
# - name: telegram-capture-health
# - schedule: every 2m
# - script: telegram_health_poller.py (no_agent=True)
# - workdir: C:\Users\khoans\Documents\Personal_OS\personal_vault
# - deliver: origin (về Hermes chat nếu có lỗi)
```

**Script cron mode:** Khi chạy không flag → poll + process tự động (cron mode).

**Monitoring 24h đầu:**
- Check `.telegram_offset.txt` được update mỗi lần chạy
- Check `.telegram_pending.json` không accumulate entries "awaiting" quá hạn
- Check Warren nhận được proposal + có thể confirm
- Nếu có lỗi → auto report về Hermes chat qua cron deliver

---

## Checkpoints

### Checkpoint 1: Sau Slice 2 (dry-run hoàn chỉnh)
- [ ] `python3 scripts/telegram_health_poller.py --dry-run` chạy ko lỗi
- [ ] Parse đúng health metrics từ message test
- [ ] Pending state file format đúng
- [ ] Offset tracking hoạt động

### Checkpoint 2: Sau Slice 4 (core flow hoàn chỉnh)
- [ ] Gửi `[capture-sleep]` → nhận proposal trên Telegram
- [ ] Reply "ok" → entry trong 051_Sleep_Log.md
- [ ] Reply "edit ..." → entry update theo edit
- [ ] Reply "skip" → ko ghi

### Checkpoint 3: Sau Slice 5 (battle test pass)
- [ ] 10 edge case test cases pass
- [ ] Ko crash với input độc hại
- [ ] State file recovery hoạt động

### Checkpoint 4: Sau Slice 6 (A/B match)
- [ ] Telegram output format === Hermes chat output format
- [ ] Insight quality tương đương

### Checkpoint 5: Sau Slice 7 (production)
- [ ] Cron chạy 24h ko lỗi
- [ ] Warren confirm flow hoạt động ổn định

---

## Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Telegram API thay đổi | HIGH | Dùng API cơ bản (getUpdates/sendMessage) — ổn định nhất |
| Network timeout giữa cycle | MOD | Retry 1 lần trong `fetch_updates()`, ko crash |
| State file corrupt do crash mid-write | LOW | Atomic write (.tmp → rename) + corrupt recovery |
| Warren gửi 2 message `[capture-sleep]` cùng ngày | LOW | Dedup by date + pending check trước khi propose |
| Script chạy overlapping (cron 2' + manual) | LOW | Offset tracking + pending state là idempotent |
| Token expire / revoke | HIGH | Script báo lỗi rõ, Warren biết để update token |

## Open Questions
- Có muốn notification âm thanh khi nhận được proposal ko? (Telegram bot có thể gửi giọng nói?)
- Script có nên tự động `--once` và ko có loop mode? (Cho cron chạy mỗi 2 phút riêng)
