# Heartbeat Management for `_cron_heartbeat.json`

## Purpose
Safely update the `cron_heartbeat.json` file used by Hermes to track the last execution time of cron jobs (e.g., `model-router-daily`). This file uses a custom format: `1|{json}` where the JSON payload follows.

## Safe Update Procedure
1. **Read the current file** with `path.read_text(encoding='utf-8')`.
2. **Split on the first `|`** to separate the leading counter from the JSON payload.
   - If no `|` exists, treat the whole file as JSON (legacy format) or skip update.
3. **Load the JSON payload** safely (`json.loads`).
4. **Modify the desired field** (e.g., `crons['model-router-daily']['last_heartbeat']`).
5. **Re‑serialize the JSON** with `json.dumps(data, indent=2, ensure_ascii=False)`.
6. **Re‑prepend the counter** (`'1|'`) and write back to the file.
7. **Validate** the written file by reading it back and ensuring it parses.

## Example Script (`update_heartbeat_simple.py`)
```python
import json, pathlib, datetime
p = pathlib.Path('C:/Users/khoans/Documents/Warren_OS_Local/vault/_cron_heartbeat.json')
txt = p.read_text(encoding='utf-8')
parts = txt.split('|', 1)
json_str = parts[1] if len(parts) > 1 else txt
data = json.loads(json_str)
if 'crons' not in data:
    data['crons'] = {}
data['crons']['model-router-daily'] = {}
data['crons']['model-router-daily']['last_heartbeat'] = datetime.datetime.utcnow().replace(microsecond=0).isoformat() + 'Z'
new_txt = '1|' + json.dumps(data, indent=2, ensure_ascii=False)
p.write_text(new_txt)
```

## Pitfalls & Fixes
- **SyntaxError on write** – Ensure the JSON is valid before writing. A missing comma or stray trailing comma will cause a `SyntaxError`.
- **File not found** – The path must be correct; use an absolute path or verify environment variables.
- **Overwriting unrelated crons** – Only modify the specific `cron_id` you intend; avoid generic updates that could corrupt other entries.
- **Race condition** – If multiple processes write to the file simultaneously, use a file lock or perform the update in a single atomic batch via the `memory` tool if possible.

## Integration with Cron‑Job Ops
- Add `references/heartbeat-management.md` to the skill’s reference list (see `cron-job-ops` skill patch).
- When a cron job fails to start, first verify the heartbeat entry exists and is recent. If the `last_heartbeat` is older than expected, re‑run the update script before investigating deeper issues.
- Document any manual heartbeat updates in the cron job’s run log to maintain an audit trail.

## Related References
- `references/error-transcripts.md`
- `references/cross-profile-discovery.md`
- `references/no-agent-scan-pattern.md`