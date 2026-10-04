# Optional Dependency Pattern (push_gcal example)

## Problem
External dependency (`push_gcal` for Google Calendar) breaks the build when not installed, blocking all case operations.

## Solution: Graceful Degradation with Feature Flag

```python
# 1. Try/except import with availability flag
try:
    from push_gcal import load_env, get_calendar_service, build_event, TIMEZONE
    _CALENDAR_AVAILABLE = True
except ImportError:
    _CALENDAR_AVAILABLE = False
    load_env = get_calendar_service = build_event = TIMEZONE = None

# 2. Guard calendar operations
def _calendar_service() -> Any:
    if not _CALENDAR_AVAILABLE:
        print("[WARN] Google Calendar not available (push_gcal not installed)")
        return None
    load_env()
    return get_calendar_service()

def create_calendar_event(...):
    if not _CALENDAR_AVAILABLE:
        print("[WARN] Google Calendar not available (push_gcal not installed). Skipping.")
        return None
    # ... normal calendar logic
```

## CLI Default: Zero Friction
```python
parser.add_argument("--no-calendar", action="store_true", default=True, 
                    help="Skip Google Calendar (default)")
```

## Behavior
| Scenario | Behavior |
|----------|----------|
| `push_gcal` installed, `--calendar` | Full calendar integration |
| `push_gcal` installed, `--no-calendar` (default) | Case ops only, no calendar |
| `push_gcal` NOT installed, any flag | Case ops work, calendar skipped with warning |

## Multi-Profile Benefit
Single fix in shared vault → works across all profiles (warren, lusine, personal) without per-profile config.