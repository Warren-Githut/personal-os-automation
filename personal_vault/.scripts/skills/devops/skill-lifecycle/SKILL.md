---
name: skill-lifecycle
description: "Skill library lifecycle management — từ lúc tạo → đảm bảo discoverable → dùng → retire. Tránh 'tàng kinh các' (skill hữu ích nhưng không ai biết để xài). Pattern từ lesson 2026-07-21: gsheet-pivot-parser-pitfalls (ops skill chất lượng, activity=0 vì thiếu discoverability)."
version: 1.0.0
category: devops
tags: [skill, lifecycle, discoverability, curation]
related_skills: [gsheet-pivot-parser-pitfalls]
---

# skill-lifecycle — Skill Library Lifecycle

> **Vấn đề:** Skill được tạo, lưu vào thư viện, nhưng không ai load → hữu ích nhưng không xài.
> **Nguyên nhân:** Hermes skill system là pull-based — chỉ load khi được reference ở SOUL, session-start, hoặc được skill_view() trong context.
> **Giải pháp:** Mỗi skill cần 1 lifecycle plan: tạo → archive (backup) → bảo vệ → gắn kết → dùng → retire.

---

## Lifecycle Stages

```
TẠO → ARCHIVE (backup vault + commit push) → BẢO VỆ (pin) → GẮN KẾT (SOUL/session-start ref) → DÙNG → RETIRE (unpin/archive/xóa)
```

---

## Stage 1: Tạo (Create)

Khi tạo skill mới:
- Đặt tên class-level (không phải session-specific)
- YAML frontmatter đầy đủ (name, description, tags, related_skills)
- Xác định category đúng (ops / devops / mkt / data-science ...)
- Nếu skill là component của 1 umbrella → set related_skills trỏ umbrella skill
- **Nếu skill KHÔNG có `category`** (vd: cross-domain tool như `explore`, `capture`, `restate`, `review-plan`, `idea-refine`) → PHẢI thêm tên skill vào whitelist của `skill-bundle-audit` §1 Bước 1. Nếu quên, skill đó sẽ bị audit coi là "system skill" và bỏ qua.

## Stage 2: Archive (Backup) 📦 🚨

**SAU khi tạo/sửa skill, BACKUP NGAY lên vault — HARD GATE (SOUL §5 Skill Archive Gate):**

```
1. Copy SKILL.md → vault/_archives/skills/<name>_SKILL_backup_YYYY-MM-DD.md
2. Nếu có scripts/ hoặc references/ → copy cả thư mục
3. git add + git commit + git push
4. In token 📦 ARCHIVE: ✅ <name>
```

**Tại sao quan trọng:**
- AppData `skills/` không được git track (nằm ngoài vault repo)
- Nếu mất máy / đổi laptop → mất toàn bộ skill
- Backup lên GitHub = bảo hiểm, restore được

**Khi nào backup:**
| Luôn backup | Có thể skip |
|-------------|-------------|
| Skill mới tạo (có SKILL.md) | File rỗng / placeholder |
| Skill vừa sửa (thay đổi content) | Skill bundled sẵn của Hermes |
| Parser/script mới trong skill | File test/temp |

## Stage 2.5: Skill SSOT Location & Sync Gate 🔄 (C5 — 2026-07-28)

> **Bài học cốt lõi (Warren correction):** Ghi rule vào WARREN_MEMORY / SOUL là **xác suất nhớ, KHÔNG đảm bảo**. Qua session mới, LLM có thể quên → skill chạy bản cũ (AppData) ≠ SSOT (vault) → bug thầm lặng. **Doc rule ≠ enforcement.** Phải có 3 lớp: (1) hard gate auto-load + (2) session-start gate + (3) automated drift detection.

**SSOT location (WARREN_MEMORY C5):**
- 🚨 **SSOT duy nhất cho mọi Hermes SKILL = `vault/.scripts/skills/<name>/SKILL.md`** (CÓ dấu chấm `.`, git-backed).
- Runtime mirror = `AppData/Local/hermes/profiles/warren-profile/skills/<name>/SKILL.md` (gitignored, KHÔNG backup).
- KHÔNG edit AppData trực tiếp (bị ghi đè mất khi sync từ SSOT).

**Skill SSOT Sync Gate — SAU MỖI create/patch/edit skill (workflow bắt buộc):**
```
1. SSOT write:  SỬA/GHI vault/.scripts/skills/<name>/SKILL.md
2. Mirror copy: copy 1 chiều → AppData/.../skills/<name>/SKILL.md
3. Verify diff: diff -q 2 file PHẢI IDENTICAL (không identical = chưa xong)
4. Commit/Push: git add + commit + push vault (SSOT)
5. Archive:     copy SKILL.md → vault/_archives/skills/<name>_SKILL_backup_YYYY-MM-DD.md + commit/push
→ Thiếu bước nào = DỪNG, KHÔNG báo "done".
```

**3-layer enforcement (đảm bảo qua session — đừng chỉ dựa memory):**
| Layer | File | Tác dụng |
|-------|------|----------|
| Gate 1 (auto-load) | `parser_script_checklist.md` → "Skill Sync Gate (C5)" block | Bắt buộc tick trước mọi skill edit |
| Gate 2 (session-start) | `SOUL.md` §5 "Skill SSOT Sync Gate 🔄" | GG thấy đầu mỗi session |
| Gate 3 (automated) | `vault_consistency_nightly.py` block **B5** (skill-drift) | Cron 10g bắt lệch SSOT↔runtime, báo đỏ TG nếu GG quên sync |

> **Drift detection snippet + full workflow:** xem `references/skill-ssot-sync-2026-07-28.md`. Sau mọi sửa nightly script → copy SSOT `vault/.scripts/vault_consistency_nightly.py` → `AppData/scripts/` (C4 cron rule) rồi verify `diff -q`.

---

## Stage 2.6 — Bulk SSOT Bootstrap (2026-07-29)

> Khi cần copy **toàn bộ skill hiện có** từ AppData runtime → vault SSOT trong 1 lần (không phải từng edit riêng lẻ). Phát sinh khi SSOT mới chỉ có vài skill nhưng runtime đã có 104+.

### Khi nào dùng
- Lần đầu thiết lập SSOT (vault `.scripts/skills/` còn trống)
- Phát hiện runtime có skill chưa được backup vào vault
- Trước khi triển khai multi-profile sync

### Workflow

```
B1. INVENTORY → scan AppData skills/ → liệt kê tất cả custom skill (SKILL.md)
B2. CATEGORIZE → phân loại từng skill vào 1 trong 4 category:
    ├── core/   — engineering chung (session-start, spec-driven, code-review, qa-gate…)
    ├── ops/    — L'Usine specific (lusine-sql-*, ops-col, weekly-revenue, promo-eval…)
    ├── stock/  — chứng khoán (stock-ingest, stock-deep-research, macro-frameworks…)
    └── personal/ — cá nhân (bctc-pdf-ingest, personal-morning-brief, capture-sleep…)
B3. CREATE → vault/.scripts/skills/{core,ops,stock,personal}/ directories
B4. COPY → mỗi skill directory (SKILL.md + linked files) → đúng category folder
B5. VERIFY → mọi skill trong AppData có SSOT copy tương ứng
B6. COMMIT → git add + commit vault (.scripts/skills/ là git-backed)
```

### Tiêu chí categorize (bảng nhanh)

| Tín hiệu trong skill | Category |
|----------------------|----------|
| Tên chứa `lusine-`, `ops-`, `weekly-`, `hourly-`, `promo-`, `col`, `lto` | ops/ |
| Tên chứa `stock-`, `macro-`, `bctc-`, `pnl-` | stock/ |
| Tên chứa `personal-`, `capture-`, `health`, `sleep` (nếu personal vault) | personal/ |
| Tên chứa `session-start`, `spec-driven`, `code-review`, `incremental`, `interview`, `tdd`, `qa-gate`, `safenet` | core/ |
| `using-agent-skills`, `compress-memory`, `reviewer-node`, `writing-great-skills` | core/ |
| Không rõ → đọc SKILL.md nội dung, check tags, category frontmatter | (theo domain) |

### Verification checklist
- [ ] Số skill SSOT == số skill runtime (trừ bundled common/ skills)
- [ ] Mỗi SSOT SKILL.md có diff 0 vs runtime copy gốc
- [ ] Linked files (references/, scripts/, templates/) được copy đầy đủ
- [ ] Git status sạch sau commit

---

## Stage 2.7 — Multi-Profile Distribution (2026-07-29)

> Sau khi SSOT đã đầy đủ, sync 1 chiều từ vault `.scripts/skills/` → AppData của **nhiều Hermes profile** (warren, stock, personal). Mỗi profile chỉ nhận skill thuộc category của nó.

### Category → Profile Mapping

| SSOT category | warren-profile | stock-profile | personal_profile |
|---------------|:---:|:---:|:---:|
| `core/*` | ✅ | ✅ | ✅ |
| `ops/*` | ✅ | ❌ | ❌ |
| `stock/*` | ❌ | ✅ | ❌ |
| `personal/*` | ❌ | ❌ | ✅ |

### Sync script pattern

Python script tại `vault/.scripts/sync_skills/sync_to_profiles.py`:

```python
"""Sync vault SSOT skills → mỗi Hermes profile theo mapping."""
import shutil, subprocess, sys
from pathlib import Path

VAULT = Path(__file__).resolve().parent.parent.parent  # vault/
APPDATA = Path.home() / "AppData" / "Local" / "hermes" / "profiles"

MAPPING = {
    "core":     ["warren-profile", "stock-profile", "personal_profile"],
    "ops":      ["warren-profile"],
    "stock":    ["stock-profile"],
    "personal": ["personal_profile"],
}

SSOT = VAULT / ".scripts" / "skills"

def sync():
    for category, profiles in MAPPING.items():
        src = SSOT / category
        if not src.exists():
            continue
        for skill_dir in src.iterdir():
            if not skill_dir.is_dir():
                continue
            for profile in profiles:
                dst = APPDATA / profile / "skills" / skill_dir.name
                dst.mkdir(parents=True, exist_ok=True)
                for src_file in skill_dir.rglob("*"):
                    if src_file.is_file():
                        rel = src_file.relative_to(skill_dir)
                        dst_file = dst / rel
                        dst_file.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(src_file, dst_file)

def verify():
    """diff -q mọi SSOT file vs runtime copy."""
    errors = []
    for category, profiles in MAPPING.items():
        src = SSOT / category
        if not src.exists():
            continue
        for skill_dir in src.iterdir():
            if not skill_dir.is_dir():
                continue
            for src_file in skill_dir.rglob("*"):
                if not src_file.is_file():
                    continue
                rel = src_file.relative_to(SSOT)
                for profile in profiles:
                    dst = APPDATA / profile / "skills" / rel
                    if not dst.exists():
                        errors.append(f"THIẾU: {profile}/skills/{rel}")
                        continue
                    r = subprocess.run(
                        ["diff", "-q", str(src_file), str(dst)],
                        capture_output=True, text=True
                    )
                    if r.returncode != 0:
                        errors.append(f"LỆCH: {profile}/skills/{rel}")
    return errors

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "sync"
    if mode == "sync":
        sync()
        errs = verify()
    elif mode == "verify":
        errs = verify()
    else:
        sys.exit(1)
    if errs:
        for e in errs:
            print(e)
        sys.exit(1)
    print("✅ Sync OK — tất cả profile đồng bộ")
```

### Sync trigger

| Trigger | Khi nào | Ai chạy |
|---------|---------|---------|
| **After skill create/edit** | Ngay sau khi sửa SSOT | GG thủ công (trong cùng session) |
| **Nightly cron** | 10:00 daily | `vault_consistency_nightly.py` block B6 |
| **Manual** | Bố gõ "sync skills" | GG chạy script |

### Consistency nightly (block B6)

Thêm vào `vault_consistency_nightly.py`:

```python
def b6_multi_profile_sync(f: Findings):
    from sync_skills.sync_to_profiles import verify
    errs = verify()
    for e in errs:
        f.add("red", "multi-profile-skill-drift", e)
```

### Verification
- [ ] Sync script tồn tại ở `vault/.scripts/sync_skills/sync_to_profiles.py`
- [ ] Chạy dry-run: `python sync_to_profiles.py verify` → 0 errors
- [ ] Mỗi profile có đúng skill theo mapping
- [ ] `diff -q` giữa SSOT và runtime = 0 lệch
- [ ] Nightly cron block B6 đã thêm

---

## Stage 3: Bảo Vệ (Pin) 🚨

**Sau khi tạo skill hữu ích, PHẢI pin ngay:**

```
hermes curator pin <skill-name>
```

**Khi nào pin:**
| Nên pin | Không cần |
|---------|-----------|
| Skill ops/pipeline thường xài (parser, cron, KPI) | Skill 1 lần (debug session, throwaway) |
| Skill chứa production lessons / pitfalls | Skill bundled sẵn (Hermes ship) |
| Skill cross-session (dùng lại nhiều lần) | Skill personal/stock profile |
| Skill chứa domain knowledge (marketing, recipe) | Skill đã deprecated/superseded |

## Stage 4: Gắn Kết (Reference) 🚨

**Pin chưa đủ — phải reference để Hermes biết skill tồn tại.**

### 4a. SOUL.md reference

Thêm vào `SOUL.md` §7 SEARCH PRIORITY CHAIN:

```markdown
| <Domain> | skill `<skill-name>` — mô tả ngắn khi nào load |

> **<Domain> work:** Khi làm <domain> → load skill `<skill-name>` (đã pin, curator không archive).
```

**Ví dụ đã làm (2026-07-21):**
```markdown
| Parser Pitfalls | skill `gsheet-pivot-parser-pitfalls` — load khi debug GSheet parser pipeline |

> **Parser work:** Khi debug/sửa GSheet parser pipeline → load skill `gsheet-pivot-parser-pitfalls` (đã pin, curator không archive).
```

### 4b. Session-start skill (optional)

Nếu skill là **core ops workflow** (cần mọi session):
- Thêm name vào list skills load trong `session-start` skill
- Chỉ dùng cho skill thực sự cần mỗi session (ví dụ: `luso-parsers`, `ops-col`)
- Tốn context → chọn lọc

### 4c. Cross-link (related_skills)

Nếu skill mới thuộc cùng domain với skill hiện có:
- Set `related_skills` ở cả 2 phía (bidirectional)
- Maintain trong quá trình audit

## Stage 5: Dùng (Use)

Khi làm việc trong domain có skill reference:
- Load skill trước khi bắt đầu task
- Cập nhật skill nếu phát hiện thiếu step/pitfall (không để lỗi lặp lại)

## Stage 6: Retire

Khi skill không còn dùng:
| `using-agent-skills` | 302 dòng, 3 chỗ lặp Interview Gate | 240 dòng, gộp 1 section | — (chỉ merge, không tách) |
| `lusine-parser-standardization` | 698 dòng, 57 dòng pitfalls (50+ entries) | 656 dòng, top 8 pitfalls | `references/pitfalls.md` (50+ entries) |

**Khi nào KHÔNG refactor:** Nếu section phình to là core workflow pattern (không phải data/reference) → giữ nguyên. Ví dụ: `ops-dashboard` có section dài về Chart.js pitfalls — đó là core knowledge, không tách.

---

## Stage 7: SSOT Hygiene — "Router Skills Must Only Route" 🚨

> **Lesson proven 2026-07-21:** `using-agent-skills` (the meta-router) had accumulated 200+ lines of gates (Freeze Gate, Step-by-Step, Consent Architecture, Skill-Creation Pipeline) that duplicated SOUL §5 and separate skills. Every section was correct content — but WRONG home.

### Principle
A skill whose PRIMARY JOB is to route/invoke other skills must:
- **Define ONLY the routing tree** — how to classify tasks and which skill to invoke
- **REFER to gates/rules** that exist elsewhere — never copy them inline
- **Keep routing pointers to spec-kit skills** — never describe their internal workflow

### Why
1. **SSOT violation**: Every duplicated gate or procedure creates 2 places to update → drift guaranteed
2. **Maintenance nightmare**: When the Freeze Gate changes, it must be updated in SOUL + using-agent-skills + every skill that copied it
3. **Context bloat**: A 200-line routing skill wastes context tokens re-loading content the agent already loaded from SOUL

### Detection
| Signal | Meaning |
|--------|---------|
| Skill has sections named after SOUL gates (Freeze, Step-by-Step, Verify) | DUPLICATE — purge from skill, keep in SOUL |
| Skill describes a separate skill's workflow in detail | DUPLICATE — replace with routing pointer |
| Skill has a backstory / historical decision ("Warren said X on Y date") | MOVE to WARREN_MEMORY or skill's references/ |
| Skill >150 lines but its only job is classification | Overgrown — strip to routing table |

### Fix procedure
1. **Map every section** against SSOT: does this content exist in SOUL, another skill, or user profile?
2. **If yes** → delete from this skill, leave a routing pointer (1 line)
3. **If no and unique** → keep, but consider if it belongs in a reference file (data/knowledge) vs SKILL.md (rules/how-to)
4. **Prune ruthlessly**: Every line that another SSOT already covers is waste
5. **Never delete knowledge** — move it to the correct SSOT

### Example (applied 2026-07-21: using-agent-skills cleanup)
| Removed section | Correct SSOT | Rationale |
|----------------|-------------|-----------|
| Interview & Freeze Gate (30 lines) | SOUL §5 | Already defined there |
| Step-by-Step Exec Gate (20 lines) | SOUL §5 | Already defined there |
| Spec-Kit Constitution detail (15 lines) | `speckit-constitution` skill | Separate skill |
| Spec-Kit Checklist detail (15 lines) | `speckit-checklist` skill | Separate skill |
| Spec-Kit Converge detail (15 lines) | `speckit-converge` skill | Separate skill |
| Consent-Gate Architecture (30 lines) | SOUL §5 / WARREN_MEMORY | Backstory, not routing |
| Self-Building Loop (20 lines) | `skill-lifecycle` | Belongs here |
| Proven Skill-Creation Pipeline (25 lines) | `skill-edit-discipline` / `skill-lifecycle` | Belongs here |
| Duplicate `agent-skills` skills (2 skills) | SOUL §5 "Ops workflow lock" | Already covered |

---

## Audit Checklist (định kỳ)

Mỗi lần curator chạy hoặc có dấu hiệu skill rot:

1. `hermes curator list-archived` — có skill ops nào cần restore?
2. `hermes curator usage | grep -E 'agent.*never'` — agent skill chưa từng dùng, cần pin/xóa?
3. SOUL.md §7 — có skill nào được reference nhưng đã archive/deprecated?
4. Skill vừa tạo — đã pin + reference chưa?
5. **Empty/broken references 🚨** — quét `references/` + `scripts/` trong tất cả custom skills:
   - `find skills/ -name "*.md" -size 0` → empty reference files → DELETE (sau khi verify không cross-reference)
   - `find skills/ -name "*.py"` → orphan scripts không được SKILL.md reference → DELETE/MOVE
   - `grep -rn "<filename>" skills/` trước khi xóa để đảm bảo không còn reference chéo
   > **Lesson 2026-07-21:** `using-agent-skills` had 2 empty refs (0 bytes, desde Jul 13) + 1 orphan `telegram_bot.py` (144 dòng, không cross-refs). Rot tích lũy âm thầm vì không có automated scan.

---

## References

- `gsheet-pivot-parser-pitfalls` — skill ops được pin + SOUL ref 2026-07-21 (ví dụ áp dụng lifecycle)
- Session lesson: skill có content chất lượng (production pitfalls) nhưng activity=0 vì thiếu discoverability

---

## Skill Refactor Pattern — When Skills Get Too Long

> **Pattern proven 2026-07-21 across 2 skills.**

**Trigger:** Skill >300 dòng, hoặc có 1 section chiếm >50% nội dung (thường là pitfalls table, reference data, hoặc post-mortems).

**Principle: Separation of Concerns — giống Qwen đề xuất nhưng áp dụng ĐÚNG:**
- Skill chính = RULES + HOW-TO (Hermes đọc mỗi lần load)
- Reference file = KNOWLEDGE BASE (tra cứu khi cần, không load mặc định)
- KHÔNG xóa kiến thức — chỉ di dời ra reference

**Refactor steps:**
1. **Xác định section phình to** — thường là pitfalls table, post-mortems, hoặc domain-specific data
2. **Giữ top 5-8 entries** quan trọng nhất trong skill chính (các entry xuất hiện nhiều lần, critical severity)
3. **Tạo file `references/<topic>.md`** với TOÀN BỘ entries gốc
4. **Thêm link 1 dòng** từ skill chính → reference: `> Full catalog (N+ entries): see \`references/<topic>.md\``
5. **KHÔNG xóa bất kỳ kiến thức nào** — reference file vẫn truy cập được qua `skill_view(name, file_path)`

**Ví dụ thực tế:**
| Skill | Trước | Sau | Reference |
|-------|-------|-----|-----------|
| `using-agent-skills` | 302 dòng, 3 chỗ lặp Interview Gate | 240 dòng, gộp 1 section | — (chỉ merge, không tách) |
| `lusine-parser-standardization` | 698 dòng, 57 dòng pitfalls (50+ entries) | 656 dòng, top 8 pitfalls | `references/pitfalls.md` (50+ entries) |

**Khi nào KHÔNG refactor:** Nếu section phình to là core workflow pattern (không phải data/reference) → giữ nguyên. Ví dụ: `ops-dashboard` có section dài về Chart.js pitfalls — đó là core knowledge, không tách.
