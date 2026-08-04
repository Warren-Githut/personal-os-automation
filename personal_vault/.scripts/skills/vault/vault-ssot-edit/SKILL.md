---
name: vault-ssot-edit
type: skill
status: active
created: 2026-07-09
last_updated: 2026-07-09
tags: [vault, ssot, consistency, cascade, manpower, edit-discipline]
description: >
  Discipline for editing Single Source of Truth markdown files in the Warren vault
  that carry the same number across multiple cross-referenced blocks/sections.
  Mandatory cascade + verification steps so dependent blocks don't go stale.
  Trigger: any edit to a vault SSOT file where a changed total/plan must propagate
  to per-store rows, gap blocks, exec summary, or cross-linked files.
---

# Vault SSOT Edit — cascading consistency discipline

## Trigger
Edit bất kỳ file SSOT markdown trong vault mà cùng 1 con số xuất hiện ở 2+ chỗ
cross-reference. Primary example: `30_KNOWLEDGE_BASE/wiki/04_labour_costs/Manpower_Master.md`
— Block 0 (metadata) / Block 1 (Plan) / Block 2 (Actual) / Block 3 (Gap) / Exec Summary
đều share Plan & Active totals. Khi bump 1 số, mọi chỗ khác phải theo.

## Steps (bắt buộc trước khi báo xong)
1. **Map trước khi sửa:** grep file tìm mọi chỗ chứa giá trị cũ (tên store + số).
2. Sửa block nguồn.
3. **Cascade tới TẤT CẢ block phụ thuộc** — bao gồm cả ô per-store, KHÔNG chỉ hàng Sys/Total.
4. **Recompute + verify totals:** tổng per-store rows PHẢI = hàng Total/Sys. Khác nhau = có cell stale.
5. Nếu file có Exec Summary / top-line bullet reference số đó → sửa luôn.
6. Check cross-linked files chỉ khi số đó là plan/SSOT value file khác phụ thuộc
   (vd repoint rename — xem reference).

## Pitfalls (đây là chỗ dễ ăn chửi)
- **Quên ô per-store khi bump total.** Bump LU5 Plan 18→19 ở Block 1 + Sys 68 là CHƯA ĐỦ.
  Block 3 có cột Plan riêng từng store (`| LU5 | 18 | 16 | -2 |`). Nếu chỉ sửa headline,
  Block 3 stale → Sys gap (-12) ≠ tổng store gap (-11). LUÔN grep giá trị cũ toàn file.
- **Đừng duplicate cột tính toán.** Nếu "gap vs plan" đã có ở block riêng (Block 3 Gap),
  KHÔNG thêm cột ± thừa vào Block 2 → tạo nguồn thứ 2 sẽ drift. Thay vào đó:
  (a) fix block gap stale, hoặc (b) thêm ± CHỈ tháng mới nhất với label rõ "vs Plan N",
  NEVER tháng lịch sử (baseline plan khác).
- **Tháng lịch sử có plan baseline khác.** May plan = 68 (có Office); Jan–Apr plan = 65.
  Tuyệt đối không tính ± tháng cũ so với plan hiện tại — táo cam.
- **Stale cross-block ≠ cố ý.** Khi thấy số không cộng khớp, coi là forgotten cascade, sửa đi.
  Đừng "để tạm context" rồi quên.

## PITFALL MỚI (2026-07-10): regenerate-then-splice tạo DUPLICATE section
Khi 1 script generator sinh lại 1 section (vd `gen_pl_ssot.py` → `13_Monthly_PL_Breakdown.v2.md`)
rồi ta splice vào SSOT, **phải drop heading của bản generated trước khi nối**, nếu không SSOT
sẽ có 2 bản `## Heading` (duplicate section). Triệu chứng: `re.findall(r'📋 FULL LINE-ITEM', t)`
trả 2 thay vì 1; hoặc SSOT bị hỏng cần `git checkout` reset.

**SAFE SPLICE PATTERN (đã verify 2026-07-10):**
```python
import re
main = "vault/10_OPERATION_DATA/13_Monthly_PL_Breakdown.md"
gen  = "vault/10_OPERATION_DATA/13_Monthly_PL_Breakdown.v2.md"   # đã có ## Heading ở dòng 0
l = open(main, encoding="utf-8").read().split("\n")
v = open(gen,  encoding="utf-8").read().split("\n")
# 1) XÓA mọi section cũ mang cùng heading khỏi main (chống duplicate)
out = []
i = 0; N = len(l)
while i < N:
    if "📋 FULL LINE-ITEM" in l[i]:          # heading của section cần thay
        i += 1
        while i < N and not l[i].startswith("## "): i += 1   # skip hết block cũ
        continue
    out.append(l[i]); i += 1
# 2) Tìm anchor chèn (vd COST STRUCTURE) và ghép generated body (GIỮ nguyên heading của v)
ci = [k for k,x in enumerate(out) if "🧮 COST STRUCTURE" in x][0]
head, tail = out[:ci], out[ci:]
final = "\n".join(head) + "\n" + "\n".join(v) + "\n\n" + "\n".join(tail)
open(main, "w", encoding="utf-8").write(final)
# 3) VERIFY ngay
t = open(main, encoding="utf-8").read()
assert len(re.findall(r"📋 FULL LINE-ITEM", t)) == 1
```
- Luôn `assert` count section == 1 sau mỗi splice. Nếu >1 → đã duplicate, `git checkout` + làm lại.
- Section mới sinh bởi script GIỮ heading của nó (v), chỉ XÓA bản cũ trong main.
- KHÔNG cắt `main[:ti] + v[1:]` (drop heading v) rồi nối tail — dễ lệch index và vẫn duplicate
  nếu main gốc đã có 2 bản (như commit 5fc694e từng có 2 FLI). Cách XÓA-ALL-rồi-chèn là an toàn nhất.

## PITFALL MỚI (2026-07-13): char-slice frontmatter injection BREAKS on CRLF files

Khi viết script backfill tự động thêm 1 field (vd `created:`) vào đầu frontmatter, **ĐỪNG cắt ký tự** (`txt[:3] + "created: ...\n" + txt[3:]`). Trên file CRLF (Obsidian save = `\r\n`), `txt[:3]` = `---\r` (cắt mất `\n`), kết quả `---\rcreated: 2026-07-13` → delimiter hỏng, YAML parse fail, frontmatter coi như "không có". 90 files corrupted trong 1 lần chạy.

**Triệu chứng:** `---created: 2026-07-13` dính liền trên 1 dòng; battle-test báo `No frontmatter found`; `yaml.safe_load` trả `None`.

**SAFE INJECT PATTERN (regex delimiter, CRLF-safe):**
```python
import re
m = re.match(r"^(---\r?\n)", txt)          # capture opening delimiter + its newline
if m and "created:" not in txt[m.end():txt.find("\n---", m.end())]:
    date_val = <nguồn: last_updated hoặc 2026-01-01 fallback>
    txt = txt[:m.end()] + f"created: {date_val}\n" + txt[m.end():]
```
- Dùng `r"\r?\n"` để accept cả LF và CRLF.
- Không cắt `txt[:3]` — luôn match delimiter line rồi insert SAUỜ nó.
- Verify ngay: `yaml.safe_load(txt[3:close])` phải có `created`, KHÔNG có `---\ncreated` glued.

**Verify-the-verifier:** nếu tự viết scan script đếm `---created` để check, nó sẽ bắt được lỗi — nhưng tốt nhất assert qua `yaml.safe_load` thực tế (parse thật, không string-match).

## User preference (2026-07-10)
Warren: "tôi rất ám ảnh chuyện hệ thống, nên mọi thứ cần phải consistent". → Mọi convention
mới (màu, format, target-rate, delta-direction) PHẢI đi vào generator script, không để lại
như 1 lần markdown edit tay. Nếu script cũ không theo format mới → rewrite, đừng patch chết.
Lần sau có file target Excel mới → `python3 scripts/gen_pl_target.py --xlsx <f> --rate 24000`
tự regenerate SSOT section + dashboard TARGET array (idempotent).

## Verify (trước commit)
Sau edit, chạy quick consistency: sum per-store == Total cho mọi block có cả 2.
Báo mọi mismatch trước khi commit. Dùng temp `hermes-verify-*.py` nếu cần assert.

## PITFALL MỚI (2026-07-13): `patch` tool rewrites WHOLE file + flips eol → byte-diff verify
Khi sửa 1 dòng trong file SSOT markdown bằng `patch` (mode=replace), tool có thể **ghi lại TOÀN BỘ file** và đổi line-ending (CRLF↔LF). Triệu chứng: `git diff --stat` báo "458 changed / 229 insertions" dù chỉ sửa 1 dòng. → **Reputable noise**, không phải edit thật.
**Root cause:** repo KHÔNG có `.gitattributes`; HEAD lưu eol lộn xộn (1 dòng LF, còn lại CRLF) → git text-diff hiểu sai whole-file flip.
**SAFE PATTERN (đã verify 2026-07-13):**
1. Sau mọi edit SSOT → verify bằng **byte-diff**, KHÔNG tin `git diff --stat`:
```python
import subprocess, difflib
head = subprocess.run(["git","show","HEAD:<path>"],capture_output=True).stdout
work = open("<path>","rb").read()
hl = head.split(b"\n"); wl = work.split(b"\n")
d = [l for l in difflib.unified_diff([x.decode("latin-1") for x in hl],
                                    [x.decode("latin-1") for x in wl], n=1) if l[:1] in "+-"]
print("CHANGED LINES:", len(d))   # phải = số dòng thực tế sửa
```
2. Nếu byte-diff chỉ ra đúng số dòng định sửa → OK. Nếu >số đó → tool đã rewrite, `git checkout -- <file>` + làm lại bằng Python **byte-precise replace** (search `old_bytes`, replace `new_bytes`, ghi `"wb"`). Ví dụ đã chạy: tìm 3 dòng bảng bằng bytes (có `\xc2\xa7` = §, `\xe1\xbb\xab` = ừ...), replace, assert `data.count(old)==1` trước khi write.
3. **Đề xuất riêng (KHÔNG bundled):** thêm `.gitattributes` (`*.md text eol=crlf`) để chặn noise vĩnh viễn. Scope discipline: "chỉ sửa X" = chỉ X.
**Verify-the-verifier:** `git diff --stat` là FALSE signal ở repo này. Luôn byte-diff.

## PITFALL MỚI (2026-07-28): CROSS-WEEK CONTAMINATION — cùng số stale ở 2 tuần liền kề
Khi 1 file SSOT có CÙNG giá trị stale ở 2 block tuần liền kề (vd `01_SSOT` W29 = W30 = `2,583` covers — copy-paste trap), mà Bố chỉ giao sửa 1 tuần (W30) → grep全局 + patch mù sẽ GHI giá trị W30-đúng (`2,503`) ĐÈ LÊN block W29. W29 thật (SQL `2,590`) bị bóp méo.

**Triệu chứng:** reviewer-node (ANCHORS A10) bắt "W29 covers = 2,503 WRONG, should be 2,590". GG tự sửa W29→2,503 vì thấy cùng chữ "2,583" trong cả 2 block.

**SAFE PATTERN (đã verify 2026-07-28):**
1. Trước patch, xác định block target BẰNG LINE RANGE, không bằng global string-match. Đọc file, tìm `## 2026-W30` heading → chỉ patch vùng giữa W30 và W29 heading.
2. Khi grep residual để verify, LUÔN exclude block tuần KHÔNG thuộc scope (vd `grep -v` line range W29, hoặc đọc tay từng hit).
3. Nếu 2 tuần liên tiếp có CÙNG số → NGHI COPY-PASTE (WARREN_MEMORY HARD RULE "SSOT covers duplicate guard") → query SQL IKKO xác nhận từng tuần RIÊNG, đừng assume chúng bằng nhau.
4. Safety net = reviewer-node độc lập (ANCHORS A10): spawn leaf subagent re-check trên disk, KHÔNG tin GG tự verify. Subagent bắt được cross-week error này khi GG bỏ sót.

**Quy tắc vàng:** "sửa W30" = sửa BLOCK W30. "sửa W29" = sửa BLOCK W29. KHÔNG bao giờ global-replace 1 số mà không biết nó thuộc tuần nào.

## References
- `references/manpower_master_blocks.md` — block layout của Manpower_Master.md và cascade map.
