# L'Usine Ops Lifecycle — Proven Patterns Reference

## 1. Graceful Degradation for Optional Dependencies

When a feature depends on an optional external library (e.g., `push_gcal` for Google Calendar, `aiogram` for Telegram):

```python
try:
    from optional_lib import needed_function
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    needed_function = None

def my_function():
    if not _AVAILABLE:
        print("[WARN] Optional feature not available, skipping")
        return fallback_behavior()
```

Core functionality works without the optional dependency.

---

## 2. Telegram Bot Integration (aiogram 3.x)

Wire to existing NL handler, use allowlist, split long messages.

---

## 3. Battle Test Pattern (3 Flexible + 3 A/B)

Core behaviors + valid approach comparisons. Run in temp dirs. 100% pass required.

---

## 4. Graceful Degradation for Calendar/Telegram

Core ops always work. External integrations skipped with clear warnings. `--no-calendar` default=True.

---

## 5. Skill Packaging for Multi-Profile

- Source of truth in vault, skills are thin wrappers
- Install per profile: `hermes skill install . --profile <name>`

---

## 6. Template System for Structured Data

```python
def build_body_from_payload(payload):
    fields = {"Vấn đề": None, "Bối cảnh": None, ...}
    # Populate from headings, fallback to heuristic split
```

---

## 7. Multi-Profile Skill Distribution & Sync

```bash
# Fix in vault, then deploy
for profile in warren-profile lusine-profile personal_profile; do
  cp -r vault/scripts/skill-name/* ~/.hermes/profiles/$profile/skills/skill-name/
done
find ~/.hermes/profiles -name "__pycache__" -exec rm -rf {} +
```

---

## 8. Vietnamese Slug Generation (Unicode NFD)

```python
def _slugify(text: str) -> str:
    text = unicodedata.normalize("NFD", text)
    text = "".join(c for c in text if unicodedata.category(c) != "Mn")
    text = re.sub(r"[^\w\s-]", "", text.lower())
    text = re.sub(r"[-\s]+", "-", text).strip("-")
    return text[:48]
```

---

## 9. VAULT_ROOT Resolution

Use absolute path or env var, not relative-to-skill.

**Windows .bat pattern:**
```bat
@echo off
cd /d %SKILL_DIR%
set PYTHONPATH=%SKILL_DIR%;%VAULT_SCRIPTS_DIR%
:loop
python -m skill.module
timeout /t 5 >nul
goto loop
```

---

## 10. Long-Running Process Restart Protocol

```bash
taskkill /F /IM python.exe
find ~/.hermes/profiles -name "__pycache__" -exec rm -rf {} +
# Then restart all instances
```

---

## 11. Multi-Vault, Multi-Bot Architecture

**One bot = One vault.** Zero routing logic between vaults/bots.

See `references/multi-vault-multi-bot-architecture.md` for full details.

---

## 12. Ops Data File Redesign (60/40 Machine/Human Split)

**Context:** An operational tracking file (Item Sales log, Revenue log, etc.) needs to serve two audiences:
- **Machine (Hermes)**: needs structured data for automated analysis, cross-checks, trend computation
- **Human (Warren)**: needs quick decisions — what changed, what's wrong, what to do

**Pattern:** Split each weekly entry into 4 sections with clear audience ownership:

| Section | Audience | Format |
|---------|----------|--------|
| Executive Summary | Human | 3-4 bullets: system total, top flag, star item, recommendation |
| Scorecard | Both | 1 markdown table: stores + System with deltas |
| JSON block | Machine | Hidden in HTML comment — store groups, top items, BCG, flags |
| Flags & Actions | Human | Structured alerts: price warnings, cross-check flags, BCG summary |

**Key decisions:**
- JSON is wrapped in `<!-- HERMES JSON BLOCK ... -->` — invisible to human, grep-able by machine
- 60% of tokens go to machine data (JSON block), 40% to human (summary + scorecard + flags)
- Remove all boilerplate: no 40-line template comments, no per-store group tables (humans don't need every item group)
- Keep decision-support data visible: BCG quadrants, price alerts, cross-check flags

**Deliverables checklist:**
1. Redesign format → get Warren to approve a CONCRETE visual (markdown table + dashboard) — abstract proposals not enough
2. Build dashboard HTML FIRST (self-contained Chart.js, File→Open) — Warren needs to SEE it to approve
3. Modify parser to output new format
4. Add machine JSON block (hidden)
5. Set up cross-reference checks (e.g. vs RevLog) that generate 🚩 flags, not hard blocks
6. Update accumulation JSON for trend data
7. Add dashboard link to central index (00_DASHBOARDS.md)
8. Set recurring calendar event for weekly review

**Token savings:** ~38% fewer lines per week (87 vs 141), template overhead eliminated entirely.

**Example:** Item Sales v2.0 — `item_sales_parser.py`, `11_Item_Sales_Weekly_Log_Star_Horse_Tracker.md`
