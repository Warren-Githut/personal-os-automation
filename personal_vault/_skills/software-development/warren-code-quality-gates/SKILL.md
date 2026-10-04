---
name: warren-code-quality-gates
description: "Gates trước commit vault code."
type: skill
version: 1.0.0
status: active
applies_to: [Hermes Desktop]
trigger: Sau build/sửa vault code → chạy gates trước commit. Hoặc Bố bảo "quality pipeline".
---

# Warren Code Quality Gates

> Class-level discipline cho mọi vault code work (parser `.scripts/`, dashboard HTML, skill scripts). Bắt buộc trước `git commit` (zone 🟡). Không thay thế `code-simplification`/`simplify-code` (chúng là how-to dọn) — skill này là GATES chạy TRƯỚC/SAU simplify để đảm bảo không hỏng + không stale.

## Gate 1 — Ab-test BEFORE simplify (behavior-preserve proof)

**Tại sao:** Simplify (xóa dead code, gộp duplicate, rename) dễ đổi behavior ngầm. Phải có baseline để chứng minh "identical".

**Quy trình:**
1. Trước simplify: viết script so sánh OUTPUT của code hiện tại vs expected (vd payload JSON của 1 tuần).
2. Sau simplify: chạy lại script → assert OUTPUT IDENTICAL (ignore float noise, drop volatile fields như `rev_vnd`).
3. Nếu differs → revert simplify đó, debug.

**Thực tế (2026-07-27 item-sales):** ab-test script load parser, build W29 payload (baseline) vs simplified-module payload → `PAYLOAD EQUAL: True`. Confirm xóa `md_entry()` dead + gộp `agg_prev` 2 lần KHÔNG đổi 1 byte output.

**Pattern:**
```python
# baseline vs simplified (import from temp file with dead code removed)
b = norm(base_payload); s = norm(simp_payload)
assert b == s, "simplify changed behavior!"
```
- Parser rebind `sys.stdout` tại import → redirect print sang `sys.stderr` trong test script (tránh "I/O on closed file").
- Run qua `terminal` với `timeout 180` (SQL query chậm).

## Gate 2 — Template-Placeholder Guard (built ≠ template)

**Bug thực tế (2026-07-27):** `--emit-html` ghi built output vào CÙNG file chứa `__PAYLOADS__`. Lần 1 build xong → file hết placeholder → lần 2 `str.replace()` no-op SILENT → dashboard stale, không báo lỗi. Hoặc agent copy built đè template "để Bố thấy data" → mất placeholder → không re-build được.

**Rule (2 files):**
- `xxx.template.html` = có `__PLACEHOLDER__`, source of truth.
- `xxx.html` = built, link target Bố mở.
- Parser `--emit-html <template>`: thêm GUARD:
  ```python
  if "__PLACEHOLDER__" not in html:
      print("[ERR] template thiếu placeholder — KHÔNG ghi đè (tránh stale)")
      return
  ```
- Verify: `grep -c "__PLACEHOLDER__" template` == 1; `grep -c "PAYLOADS = \[" built` == 1.
- NEVER copy built onto template.

## Gate 3 — Legacy Entry Cleanup (tracker migration)

**Bug thực tế (2026-07-27):** Backfill W18–W29 SQL vào tracker còn 6 legacy GSheet entries (`## W23` không phải `## 2026-W23`). `upsert_week()` match chỉ `## 2026-Wxx` → bỏ sót legacy → 18 H2, 2 số mâu thuẫn cùng tuần (W23 legacy 4,828 vs new 5,211). Dashboard chỉ đọc JSON (12) nên đẹp, nhưng người/LLM đọc tracker thấy contradiction.

**Rule:**
- Sau migrate data source (GSheet→SQL, đổi format) → XÓA legacy entries có header format cũ.
- Verify: `grep -c "^## " tracker` == expected (12 không phải 18).
- Backup trước truncate (`cp tracker /tmp/tracker_before_legacy_$(date +%H%M%S).md`).
- `reviewer-node` (A10) hay bắt bug này → chạy nó.

## Gate 4 — Reviewer-node Stale Catch (A10)

Sau mọi simplify/backfill → spawn `reviewer-node` (fresh context, `delegate_task`) review output. Thường bắt:
- legacy entries dup (Gate 3)
- template placeholder mất (Gate 2)
- frontmatter stale (vd tracker còn khai `data_source: GSheet v2.0` dù đã SQL v3.0)
- dead code còn sót (md_entry, if False/pass loop)

Fix xong → re-verify (unit + abtest + cross-week A6 independent recompute) trước commit.

## Gate 5 — Frontmatter Sync

Khi đổi pipeline (data source, version, metric) → update tracker/dashboard frontmatter:
- `data_source`: GSheet → `IKKO SQL Server (read-only firewall)`
- `parser_version`: bump (vd 2.0 → 3.0)
- `last_updated`: ngày chạy
- `key_definitions`: đúng metric (revenue = Net = Gross×0.882, không phải Gross)

## Gate 6 — Wrong-Depth Review (cron/parser diffs)

**Tại sao:** Sửa ở 1 site mà sibling giữ nguyên flaw = band-aid. Cron/parser Warren có nhiều file cùng shape (lto_weekly_cron, google_review_monday_cron, item_sales_cron_runner) → fix 1 chỗ, chỗ khác vẫn hỏng. Hoặc cùng tên hàm nhưng semantics khác → merge mù vào `_utils.py` sẽ break 1 cron.

**Quy trình (cho mọi cron/parser diff):**
1. Với mỗi helper bị dup (TG send, `compute_current_week_label`, `should_skip`): `grep -rn "def <fn>" profile/scripts vault/.scripts` → so sánh BODY, không chỉ tên.
2. Check VAULT_ROOT: cron ở `profile/scripts` thì `SCRIPT_DIR.parent` = `warren-profile/` (KHÔNG có `10_OPERATION_DATA`) → sai. Phải `resolve_vault_root()` (env `WARREN_VAULT` → fallback). KHÔNG hardcode `C:\Users\khoans\…`.
3. `compute_current_week_label`: LTO = tuần TRƯỚC (Monday-of-yesterday), Google = tuần HIỆN TẠI. Cùng tên, khác nghĩa → KHÔNG merge mù. Dùng `compute_iso_week(ref, offset)` hoặc rename rõ.
4. Rule dup: TG send → share NOW (reconcile return bool vs dict, parse_mode HTML vs none). Week-label & skip → giữ dup-but-RENAME đến khi có lib parametrized (`week_offset`, `header_marker`) + regression test.
5. Precedent: shared-week-util đã DEFERRED RISKY (`10c702c`); year-boundary week-spam fix `8364473`. Week math = footgun → test trước.

**Chi tiết + recipe:** `references/warren_cron_review_pitfalls.md`

## Checklist trước commit (zone 🟡)
- [ ] Gate 1: ab-test PASS (identical)
- [ ] Gate 2: template guard OK, 2 files tách biệt
- [ ] Gate 3: tracker không legacy dup (grep count đúng)
- [ ] Gate 4: reviewer-node chạy, bugs fixed
- [ ] Gate 5: frontmatter sync
- [ ] Gate 6: wrong-depth review (nếu sửa cron/parser) — VAULT_ROOT resolve + same-name/different-semantics check
- [ ] Cross-week A6 verify (nếu parser): 12/12 khớp 100% vs SQL trực tiếp
- [ ] Unit test ALL PASS

## Cross-link
- `code-simplification` / `simplify-code`: how-to dọn (chạy SAU Gate 1)
- `verify-parser-output`: independent recompute (A6) cho parser
- `reviewer-node`: independent critic spawn
- `using-agent-skills`: quality-pipeline composition (chuỗi skill)
