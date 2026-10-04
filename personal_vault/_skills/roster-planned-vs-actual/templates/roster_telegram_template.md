# Telegram Roster Format Template

Manager sends this format every Saturday for the next week.

## Template

```
LU3 Roster (DD-DD Mmm YYYY):
Mon DD/MM: Mgmt X, Lead X, SA X, Bar X, CDP X, Cook X, Cleaner X = Totalh
Tue DD/MM: Mgmt X, Lead X, SA X, Bar X, CDP X, Cook X, Cleaner X = Totalh
Wed DD/MM: Mgmt X, Lead X, SA X, Bar X, CDP X, Cook X, Cleaner X = Totalh
Thu DD/MM: Mgmt X, Lead X, SA X, Bar X, CDP X, Cook X, Cleaner X = Totalh
Fri DD/MM: Mgmt X, Lead X, SA X, Bar X, CDP X, Cook X, Cleaner X = Totalh
Sat DD/MM: Mgmt X, Lead X, SA X, Bar X, CDP X, Cook X, Cleaner X = Totalh
Sun DD/MM: Mgmt X, Lead X, SA X, Bar X, CDP X, Cook X, Cleaner X = Totalh

LU5 Roster:
Mon DD/MM: Mgmt X, Lead X, SA X, Bar X, CDP X, Cook X, Cleaner X = Totalh
...

LU7 Roster:
Mon DD/MM: Mgmt X, Lead X, SA X, Bar X, CDP X, Cook X, Cleaner X = Totalh
...
```

## Segment definitions

| Segment | Role | Description |
|---------|------|-------------|
| Mgmt | FOH Management | RM, ARM, Shift Manager |
| Lead | FOH Floor Lead | Supervisor, Captain |
| SA | FOH Service Agent | Waiter/waitress |
| Bar | FOH Bar Team | Bartender, barista |
| CDP | BOH Leader | Chef de Partie |
| Cook | BOH Cook | Commis, Demi Chef |
| Cleaner | Cleaner | Dishwasher, cleaner |

## Rules

1. **Use numeric dates only**: `DD/MM` or `DD-MM` (e.g., `15/9` or `15-09`)
2. **Total must equal sum of segments**: `= 114h` means all segments sum to 114
3. **One line per day**: Start with day name (Mon, Tue, etc.)
4. **All 3 stores**: LU3, LU5, LU7 each get their own block
5. **All 7 days**: Monday through Sunday

## Example (complete)

```
LU3 Roster (15-21 Sep 2026):
Mon 15/9: Mgmt 10, Lead 8, SA 36, Bar 8, CDP 8, Cook 28, Cleaner 16 = 114h
Tue 16/9: Mgmt 10, Lead 8, SA 30, Bar 6, CDP 6, Cook 24, Cleaner 16 = 100h
Wed 17/9: Mgmt 10, Lead 8, SA 32, Bar 6, CDP 6, Cook 26, Cleaner 16 = 104h
Thu 18/9: Mgmt 10, Lead 8, SA 34, Bar 8, CDP 8, Cook 28, Cleaner 16 = 112h
Fri 19/9: Mgmt 10, Lead 8, SA 38, Bar 10, CDP 8, Cook 30, Cleaner 16 = 120h
Sat 20/9: Mgmt 10, Lead 8, SA 40, Bar 12, CDP 10, Cook 32, Cleaner 16 = 128h
Sun 21/9: Mgmt 10, Lead 8, SA 38, Bar 10, CDP 8, Cook 30, Cleaner 16 = 120h
```
