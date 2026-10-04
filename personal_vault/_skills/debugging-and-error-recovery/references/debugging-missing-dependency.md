# Debugging Missing Dependency Pattern

## Symptom
```
ModuleNotFoundError: No module named 'push_gcal'
```
Crash occurs at import time, blocking ALL case operations (not just calendar).

## Root Cause Analysis
1. **Import at module top** — `from push_gcal import ...` at line 16
2. **Crashes on import** — Before any CLI command runs
3. **Blocks everything** — Even `ops-cases list` fails

## Debugging Steps

### 1. Trace the Import Chain
```bash
python3 -c "from case_followup_orchestrator import main; main()"
```
→ Shows exact line of failure

### 2. Identify Import Location
```python
# Line 16 in case_followup_orchestrator.py
from push_gcal import load_env, get_calendar_service, build_event, TIMEZONE
```

### 3. Check Feature Usage
| Feature | Needs push_gcal? |
|---------|------------------|
| Case CRUD | No |
| Index/Kanban | No |
| Calendar events | **Yes** |
| NL commands | No |

**80% of use cases don't need calendar** — blocking all is wrong.

## Fix Pattern: Graceful Degradation
```python
try:
    from push_gcal import load_env, get_calendar_service, build_event, TIMEZONE
    _CALENDAR_AVAILABLE = True
except ImportError:
    _CALENDAR_AVAILABLE = False
    load_env = get_calendar_service = build_event = TIMEZONE = None

def _calendar_service():
    if not _CALENDAR_AVAILABLE:
        print("[WARN] Google Calendar not available (push_gcal not installed)")
        return None
    load_env()
    return get_calendar_service()
```

## Debugging Pattern: Long-Running Process Not Picking Up Code Changes

### Symptom
Code changes work in tests but not in the running service/bot. Old behavior persists after fix.

### Root Cause
**Long-running process loaded old bytecode at startup.** Changes to source files don't affect running process.

### Debugging Steps

1. **Verify process is actually restarted**:
   ```bash
   # Check if process was killed
   ps aux | grep python
   # Look for old PIDs still running
   ```

2. **Check Python bytecode caches**:
   ```bash
   find . -name "__pycache__" -type d
   find . -name "*.pyc"
   ```

2. **Verify environment variables loaded at process start**:
   - .env files loaded at process startup only
   - Changes to .env require full restart

3. **Verify .bat/.sh startup scripts load .env**:
   ```bat
   :: Windows .bat must explicitly load .env
   for /f "tokens=1,2 delims==" %%a in ('type ".env" ^| findstr /r /v "^#" ^| findstr "="') do set %%a=%%b
   ```

3. **Verify process actually restarted (not just looped)**:
   - Check for "Starting..." log message with new timestamp
   - Check process PID changed

### Fix Checklist
- [ ] Kill all related processes: `taskkill /F /IM python.exe`
- [ ] Clear all __pycache__: `find . -name "__pycache__" -exec rm -rf {} +`
- [ ] Clear .pyc files: `find . -name "*.pyc" -delete`
- [ ] Update startup script to load .env
- [ ] Full restart: kill → clear caches → restart
- [ ] Verify new process shows "Starting..." log with current timestamp

## Verification Steps
1. **Uninstall dependency**: `pip uninstall push_gcal`
2. **Run all tests**: `python3 scripts/tests/test_case_orchestrator.py`
3. **Test CLI**: `ops-cases new --slug test --title "Test" --no-calendar`
4. **Verify warnings**: Should see `[WARN] Google Calendar not available`

## Key Principle
> **Optional features should not block core functionality.** If 80% of users don't need a feature, make it gracefully disabled by default.