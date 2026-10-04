# Skill SSOT Sync — 2026-07-28 (lesson + recipe)

## Tại sao cần (Warren correction)
"Con có chắc dù qua session mới, bất cứ khi nào update skill/scripts, con đều sẽ nhớ và làm vậy ko?"
→ GG thừa nhận: memory/doc rule là **xác suất**, không đảm bảo. LLM qua session mới có thể quên → chạy bản AppData cũ ≠ vault SSOT → bug thầm lặng.
→ **Doc rule ≠ enforcement.** Phải có automated gate.

## SSOT location (WARREN_MEMORY C5)
- SSOT = `vault/.scripts/skills/<name>/SKILL.md` (git-backed, CÓ dấu chấm)
- Runtime = `AppData/Local/hermes/profiles/warren-profile/skills/<name>/SKILL.md` (gitignored)
- KHÔNG edit AppData trực tiếp.

## Sync workflow (SAU MỖI skill edit)
```
1. GHI     vault/.scripts/skills/<name>/SKILL.md
2. COPY    → AppData/.../skills/<name>/SKILL.md   (1 chiều)
3. DIFF    diff -q 2 file  → PHẢI IDENTICAL
4. COMMIT  git add + commit + push vault
5. ARCHIVE copy → vault/_archives/skills/<name>_SKILL_backup_YYYY-MM-DD.md + commit/push
```

## 3-layer enforcement
| Layer | File | Note |
|-------|------|------|
| Gate 1 | `parser_script_checklist.md` → "Skill Sync Gate (C5)" | auto-load step 3.5 session-start |
| Gate 2 | `SOUL.md` §5 "Skill SSOT Sync Gate 🔄" | thấy đầu session |
| Gate 3 | `vault_consistency_nightly.py` block B5 | cron 10g, báo đỏ nếu lệch |

## Drift detection snippet (block B5 — vault_consistency_nightly.py)
```python
def _read(p):
    try:
        return p.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return None

def b5_skill_sync_drift(f: Findings):
    ssot_skills = VAULT_ROOT / ".scripts" / "skills"
    runtime_skills = Path(os.environ.get(
        "APPDATA", r"C:/Users/khoans/AppData/Local")) / "hermes" / "profiles" / "warren-profile" / "skills"
    if not ssot_skills.exists():
        return
    for sp in ssot_skills.rglob("SKILL.md"):
        rel = sp.relative_to(ssot_skills)
        rt = runtime_skills / rel
        if not rt.exists():
            f.add("yellow", "skill-drift",
                  f"Skill runtime thiếu: {rel} (SSOT có, AppData chưa copy)")
            continue
        a, b = _read(sp), _read(rt)
        if a is None or b is None:
            continue
        if a.replace("\r\n", "\n") != b.replace("\r\n", "\n"):
            f.add("red", "skill-drift",
                  f"Skill lệch SSOT↔runtime: {rel} — GG quên sync (C5). Chạy diff + copy lại.")
```
Gọi trong `main()`: `b5_skill_sync_drift(f)` sau `b4_schema(f)`.

## Pitfall đã tránh
- `parser_script_checklist.md` patch bằng `patch` tool bị 7 matches → phải dùng anchor dài hơn (gồm dòng "File hệ thống Hermes").
- SOUL.md patch fuzzy match vô tình XÓA dòng `compress-memory → vault only` → phải restore ngay (verify grep count sau patch).
- `vault_consistency_nightly.py` SSOT ở `vault/.scripts/` (mới hơn AppData 27/07 vs 25/07) → sửa SSOT rồi copy sang AppData, verify `diff -q`.
