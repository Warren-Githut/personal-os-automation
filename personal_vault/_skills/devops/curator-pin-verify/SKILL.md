---
name: curator-pin-verify
description: "Real-time verify curator pin state when `hermes curator status` shows stale cached count. Covers .usage.json verification and the pin-vs-status display lag."
status: active
created_by: agent
created: 2026-07-21
version: 1.0
triggers:
  - "vua pin skill, hermes curator status van show so cu"
  - "curator pin khong hoat dong"
  - "verify pin state real-time"
  - "khiem tra .usage.json"
---

# curator-pin-verify

> **Pitfall phát hiện 2026-07-21:** `hermes curator pin <name>` trả "pinned" success nhưng `hermes curator status` vẫn show số cũ. Đây là **cache display**, không phải lỗi.

## Root cause

`hermes curator status` đọc từ **last curator run report** (chạy 7d/lần), không real-time. Pinning ghi ngay vào `.usage.json` nhưng display chỉ refresh sau curator run kế tiếp.

## Verify real-time

```bash
python3 -c "import json; d=json.load(open('C:/Users/khoans/AppData/Local/hermes/profiles/warren-profile/skills/.usage.json')); print('Pinned:', [k for k,v in d.items() if v.get('pinned')])"
```

## Khi audit

1. Chạy `hermes curator pin <name>` → success message
2. Verify real-time bằng lệnh đọc `.usage.json` (ở trên)
3. `hermes curator status` chỉ đúng sau curator run kế tiếp

## File location

`<profile>/skills/.usage.json` — JSON dict:
```json
{
  "skill-name": {
    "pinned": true,
    "state": "active",
    "last_activity_at": "...",
    "use": 0, "view": 0, "patches": 0, "activity": 0
  }
}
```

## Liên quan

- `hermes-curator-hygiene` — curator setup + pin management
- `audit-automation` §2f — curator check trong audit (cần update pin count verify step)
