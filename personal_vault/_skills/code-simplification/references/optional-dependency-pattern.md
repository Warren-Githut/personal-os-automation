# Optional Dependency Pattern for Python

## Problem
Code depends on an optional external library (e.g., `push_gcal` for Google Calendar) but should:
1. Work without it (graceful degradation)
2. Not crash on import if missing
3. Clearly inform user when feature is unavailable

## Pattern: Try/Except Import with Sentinel

```python
# At module top level
try:
    from push_gcal import load_env, get_calendar_service, build_event, TIMEZONE
    _CALENDAR_AVAILABLE = True
except ImportError:
    _CALENDAR_AVAILABLE = False
    # Define stubs for type hints / runtime checks
    load_env = get_calendar_service = build_event = TIMEZONE = None
```

## Usage Patterns

### 1. Guard Calendar Functions
```python
def _calendar_service():
    """Get Google Calendar service. Returns None if not available."""
    if not _CALENDAR_AVAILABLE:
        print("[WARN] Google Calendar not available (push_gcal not installed)")
        return None
    load_env()
    return get_calendar_service()

def _build_calendar_payload(slug: str, case_data: dict) -> tuple:
    if not _CALENDAR_AVAILABLE:
        raise RuntimeError("Google Calendar not available (push_gcal not installed)")
    # ... rest of function
```

### 2. Graceful Degradation in Main Flow
```python
def create_case(args):
    # ... create case logic ...
    
    if create_calendar:
        if not _CALENDAR_AVAILABLE:
            print("[WARN] Google Calendar not available (push_gcal not installed). Skipping calendar creation.")
        else:
            try:
                link, event_id, date_str, time_str = _build_calendar_payload(slug, case_data)
                apply_followup_side_effects(slug, case_data, date_str, event_id, "GCAL CREATE")
            except Exception as error:
                print(f"[WARN] Calendar creation failed: {error}")
```

### 3. Early Return Pattern
```python
def main():
    if not _CALENDAR_AVAILABLE:
        print("[WARN] Google Calendar not available (push_gcal not installed).")
        print("       Case file and index updated. Run 'followup --slug X' after installing push_gcal.")
        return
    
    # ... rest of calendar logic
```

## Key Principles

| Principle | Implementation |
|---------|----------------|
| **Fail gracefully** | Initialize `_CALENDAR_AVAILABLE` at import time |
| **Fail fast, fail clearly** | Check `_CALENDAR_AVAILABLE` before calendar ops |
| **Stubs for type checking** | Define `None` placeholders for type hints |
| **User-facing warnings** | Print clear `[WARN]` messages with action |
| **No crashes** | Never let missing optional dep crash the app |

## Usage in Multiple Entry Points

```python
# In main CLI
if args.calendar and not _CALENDAR_AVAILABLE:
    print("[WARN] Cannot create calendar event - push_gcal not installed")
    sys.exit(1)

# In library functions
def some_calendar_feature():
    if not _CALENDAR_AVAILABLE:
        raise RuntimeError("Feature requires push_gcal package")
```

## Environment Variable Alternative

Instead of hardcoding availability, allow runtime override:
```python
# Allow forcing disabled for testing
_CALENDAR_AVAILABLE = True
try:
    from push_gcal import load_env, get_calendar_service, build_event, TIMEZONE
except ImportError:
    _CALENDAR_AVAILABLE = False
    load_env = get_calendar_service = build_event = TIMEZONE = None

# Allow env var override
if os.getenv("DISABLE_CALENDAR", "").lower() in ("1", "true", "yes"):
    _CALENDAR_AVAILABLE = False
```

## Key Benefits

| Benefit | How Achieved |
|---------|--------------|
| Zero-friction for users | Works without optional deps |
| Clear error messages | `[WARN]` prefix, actionable advice |
| Type safety | Stubs maintain type hints |
| Testable | Mock `_CALENDAR_AVAILABLE` in tests |
| Zero config | Auto-detects availability |