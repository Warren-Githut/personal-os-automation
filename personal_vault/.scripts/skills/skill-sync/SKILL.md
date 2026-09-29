---
name: skill-sync
description: "Sync 1 skill từ AppData (nơi Bố patch) → vault SSOT (.scripts/skills) + archive + git commit/push. Chạy được từ mọi profile (warren/stock/personal). Trigger: 'skill-sync <skill-name>' hoặc 'sync <skill-name>'."
version: 1.2.0
tags: [skill, sync, backup, git, ssot]
related_skills: ["commit-push-gate", "vault-sync-debugging"]
disable-model-invocation: true
---

# skill-sync

> Đồng bộ 1 skill Bố vừa patch ở AppData → két sắt git (vault `.scripts/skills/`) + backup `_archives/skills/` + push GitHub.
> **Chạy từ bất kỳ profile nào** (warren / stock / personal) — skill tự detect profile hiện tại và resolve đúng vault + repo.

## Trigger
```
skill-sync <skill-name>     → đồng bộ skill đó
sync <skill-name>           → alias, y hệt
skill-sync --help           → in hướng dẫn
```
Ví dụ: `skill-sync stock-ingest` (từ warren, stock, hay personal đều được).

## Hard rules (KHÔNG đụng)
- SOUL §5 Skill SSOT Sync Gate + Skill Archive Gate = guardrail. Skill này là thực thi của 2 gate đó.
- SSOT = vault `.scripts/skills/<name>/SKILL.md`. KHÔNG sửa AppData trực tiếp làm nguồn. Copy 1 chiều SSOT → AppData.
- Commit vào repo của **profile đang chạy** (warren→warren-os-lusine, stock→warren-os-lusine do symlink, personal→personal-os-automation). KHÔNG bao giờ commit sang repo profile khác.
- Archive vào `<vault>/_archives/skills/<name>_SKILL_backup_YYYY-MM-DD.md`.

## 🚨 MANDATORY PRE/POST RULES (bài học 2026-08-02)
- **🔴 SAU KHI PATCH SKILL → BẮT BUỘC CHẠY skill-sync NGAY.** Không chỉ commit/push warren-profile git repo rồi báo "xong". Quên sync = vault SSOT thiếu bản mới → lỡ 1 nhịp. Quy tắc: mọi lần Bố approve patch → cuối luôn `skill-sync <name>` trước khi claim done.
- **🔴 TRƯỚC KHI grep/patch → `find` PATH THẬT.** Stock-profile skills là symlink → vật lý ở `warren-profile/skills/`, và có thể có thư mục trung gian (vd `stock-insider-dealing` nằm ở `warren-profile/skills/stock/stock-insider-dealing/`, KHÔNG phải `stock-profile/skills/stock-insider-dealing/`). Đoán path → grep sai → tưởng chưa patch. Luôn `find . -name SKILL.md -path "*<name>*"` trước.

## Process (6 bước, mỗi bước có completion criterion)

### Step 1 — Detect profile + resolve paths
Xác định profile hiện tại từ `HERMES_PROFILE` env hoặc path `AppData/Local/hermes/profiles/<X>`.
Resolve:
- `APP_SKILLS` = `C:/Users/khoans/AppData/Local/hermes/profiles/<X>/skills/`
- `VAULT_SSOT` + `VAULT_ARCHIVE` + `GIT_REPO` theo bảng:

| Profile | APP_SKILLS (vật lý) | VAULT_SSOT | VAULT_ARCHIVE | GIT_REPO |
|---------|---------------------|------------|---------------|----------|
| warren-profile | warren-profile/skills | Warren_OS_Local/vault/.scripts/skills | Warren_OS_Local/vault/_archives/skills | warren-os-lusine (master) |
| stock-profile | warren-profile/skills (symlink) | Stock_OS/stock_vault/.scripts/skills | Stock_OS/stock_vault/_archives/skills | stock-os-automation (master) |
| personal_profile | personal_profile/skills | Personal_OS/personal_vault/.scripts/skills | Personal_OS/personal_vault/_archives/skills | personal-os-automation |

*Note: stock-profile skills là symlink → vật lý nằm ở warren-profile/skills. Nên SSOT + repo = warren.*

**🔴 MULTI-SSOT SCAN (bắt buộc — bài học 2026-09-29):** Một skill có thể tồn tại ở NHIỀU path trong vault (VD: `stock-valuation-model` có cả `.scripts/skills/stock/stock-valuation-model/` lẫn `.scripts/skills/stock-valuation-model/`). Chỉ verify 1 path → báo "synced" oan.
```bash
find <VAULT_SSOT> -ipath "*<name>*" -name SKILL.md
```
- Nếu trả về >1 path → **copy vào TẤT CẢ**, verify `diff -rq` từng bản.
- Nếu trả về 0 path → skill chưa có trong vault, tạo mới ở path chuẩn `<VAULT_SSOT>/<name>/`.

**Completion:** Đường dẫn 4 biến đã xác định và `APP_SKILLS/<name>` tồn tại. Nếu `<name>` không có trong APP_SKILLS → DỪNG, báo Bố "skill <name> không tồn tại ở profile <X>".

### Step 2 — Ensure SSOT dir exists
Nếu `VAULT_SSOT/<name>` chưa có → `mkdir -p`. Với personal mà `personal_vault/.scripts` chưa có → tạo luôn (`mkdir -p personal_vault/.scripts/skills`).
**Completion:** `VAULT_SSOT/<name>` tồn tại.

### Step 3 — Copy skill AppData → SSOT (1 chiều)
**🔴 COLLISION GATE — kiểm tra repo ĐÍCH TRƯỚC khi `cp`.** `cp -r` ghi đè không hỏi: nếu session khác đang sửa `VAULT_SSOT/<name>` và chưa commit, bạn sẽ xoá sạch công sức họ rồi commit thay bằng nội dung của mình. Chạy trước Step 3:
```bash
git -C <VAULT_ROOT> status --porcelain <SSOT path>   # đích có đang sửa chưa commit?
git -C <VAULT_ROOT> diff --stat <SSOT path>
```
- **Sạch** → copy bình thường.
- **CÓ DIFF CHƯA COMMIT** → **DỪNG, KHÔNG `cp`**, hỏi Bố và đưa lựa chọn (giữ nguyên / merge 2 bên / bỏ sync). Bố thường chọn *"giữ nguyên, con không đụng, tôi hỏi session kia commit trước"*.

**Chứng minh diff thuộc về BẠN trước khi kết luận:** grep một marker đặc trưng **duy nhất trong bản của bạn** ở cả hai nơi.
```bash
grep -c "<marker-riêng-của-bạn>" <APP_SKILLS>/<name>/SKILL.md   # >0 = bản của bạn
grep -c "<marker-riêng-của-bạn>" <VAULT_SSOT>/<name>/SKILL.md    #  0 = chưa có ⇒ diff KHÔNG phải của bạn
```
`0` ở SSOT ⇒ tuyệt đối không overwrite. **Đừng suy từ "cùng đường dẫn" mà kết luận là của mình.**

**🔴 MARKER GREP KHÔNG PHẢI IDENTITY CHECK (ACV 26/09, review /review bắt được).** Marker `2/2 ở cả hai nơi` chỉ chứng minh **hai dòng marker tồn tại**, KHÔNG chứng minh file giống nhau. ACV: `SKILL.md` AppData 27.270B vs SSOT 28.763B, 14 dòng contract-rule chỉ có ở SSOT (`Header bắt buộc có ngày`, `source: không rỗng`, `Từng claim EPS/P/E … cùng dòng`). Nếu báo "đã merge xong, không cần sync" bằng cơ sở marker ⇒ sai.
**Bắt buộc, theo thứ tự:**
1. `diff -rq` hai bên. Nếu khác → **chưa merge xong**, dù có marker.
2. So **mtime** từng file để biết hướng nào mới hơn. **Không đoán hướng sync.**
3. Marker grep chỉ dùng cho **ownership** ("diff này là của tôi hay của người khác"), không dùng cho **equality**.

**🔴 HƯỚNG SYNC PHẢI THEO CHIỀU MỚI HƠN, KHÔNG THEO CHIỀU MẶC ĐỊNH.** Skill này copy **AppData → SSOT**. Nếu SSOT mới hơn (mtime lớn hơn) thì chạy `skill-sync` sẽ **xoá công sức mới nhất** — đúng thứ COLLISION GATE sinh ra để chặn. ACV 26/09: SSOT mới hơn ở cả 3 file (`bots.md` +3h13, `gen_swarm.py` +3h09) nhưng con vẫn khuyên Bố chạy `skill-sync` ⇒ sẽ mất 5 rule đã ship.
→ Trước khi hướng dẫn Bố bất kỳ lệnh sync nào: **kiểm mtime, nói rõ chiều, và nếu chiều đúng là NGƯỢC skill-sync thì dừng + báo Bố.** Đừng tự đề xuất lệnh phá dữ liệu.

**🔴 MULTI-SSOT COPY (bài học 2026-09-29):** Nếu Step 1 tìm được >1 path SSOT → copy vào **TẤT CẢ** bản. Chỉ copy 1 bản còn lại bản cũ → version-guard báo DRIFT oan.
```bash
for path in $(find <VAULT_SSOT> -ipath "*<name>*" -name SKILL.md | xargs -I{} dirname {}); do
  cp -r <APP_SKILLS>/<name>/. "$path/"
done
```

### Step 3b — MERGE 2 BÊN (chỉ khi Bố DUYỆT; mặc định vẫn DỪNG)

Khi COLLISION GATE báo "CÓ DIFF CHƯA COMMIT" và Bố chọn *merge* thay vì *giữ nguyên*.
`cp -r` KHÔNG dùng ở đây — nó xoá sạch phần session khác. Thay bằng chèn có kiểm soát.

**B0 — Backup trước khi đụng (bắt buộc):**
```bash
cp <SSOT>/SKILL.md <SSOT>/SKILL.md.merge-backup
```

**B1 — Đo block của mình bằng SỐ DÒNG, không quét regex để tìm điểm cuối.**
⚠️ Bài học ACV 26/09: regex dừng ở heading kế tiếp quét **quá xa → 128 dòng thay vì 5**, nuốt trọn thân tài liệu của session khác. Anchor chỉ dùng để **tìm điểm đầu**.
```python
i = next(k for k,l in enumerate(your_lines) if "MARKER_RIENG_CUA_BAN" in l)
block = your_lines[i:i+N]        # N = bạn TỰ ĐẾM, assert len(block) <= 10
assert len(block) <= 10, f"quá dài: {len(block)} — lỗi giống ACV, DỪNG"
```

**B2 — Chèn vào đúng vị trí, giữ nguyên phần session khác:**
- patch đầu file → chèn ngay sau dòng anchor tương ứng trong SSOT
- patch cuối file → chèn sau dòng cuối của mục liên quan
- Viết bằng `newline="\n"`, `encoding="utf-8"` (git cảnh báo CRLF nếu không)

**B3 — Verify 2 CHIỀU (bắt buộc, bằng set, không đọc mắt):**
```python
lost = set(l.strip() for l in old if l.strip()) - set(l.strip() for l in new if l.strip())
assert not lost, f"mất {len(lost)} dòng của session khác: {list(lost)[:3]}"
```
`lost == 0` là điều kiện **chặn commit**. `added` chỉ nên bằng đúng số dòng bạn thêm.

**B4 — Chạy self-test của skill trước khi commit** (vd `stock-verify-gate/references/self_test.py`).
Script con chạy được thì skill còn sống — `ls` KHÔNG chứng minh gì.

**B5 — Xoá backup** SAU KHI verify xong. Giữ lại = rác trong git.

**Token trung thực:** khi Step 3/4/5 bị chặn, **KHÔNG in `sync✓`/`archive✓` cho bước đó** và đừng ghi token tương ứng vào commit message — token giả vi phạm `gate-token-integrity`. Báo rõ bước nào đã chạy, bước nào dừng vì lý do gì.

`cp -r APP_SKILLS/<name>/. VAULT_SSOT/<name>/`
**Completion:** `diff -rq APP_SKILLS/<name> VAULT_SSOT/<name>` → IDENTICAL. Không identical → DỪNG, báo lỗi.

**🔴 COLLATERAL GATE — `cp -r` GHI ĐÈ MỌI THỨ TRONG THƯ MỤC, KHÔNG CHỈ `SKILL.md`.**
`cp -r APP/. SSOT/` thay **từng file** trong đích bằng bản AppData, không hỏi — kể cả `references/`, `plans/`, `specs/` bạn không định sửa. COLLISION GATE ở trên chỉ kiểm tra trạng thái **trước** copy, nên nó không chặn được trường hợp chính bản `cp` vừa gây hại.
Cơ chế: bản SSOT trong vault có thể đã drift khỏi AppData (vault giữ file riêng, hoặc bản support file cũ hơn). `cp -r` thay không hỏi → rồi `git add <dir>` quét cả thư mục → commit 13 file trong khi bạn chỉ sửa 1.
**BẮT BUỘC sau mỗi `cp -r`, TRƯỚC khi `git add`:**
```bash
git -C <VAULT_ROOT> status --porcelain <SSOT path>   # file nao BI DUOC
git -C <VAULT_ROOT> diff --stat <SSOT path>
```
- **Chỉ đúng file bạn định sửa** → copy sạch, đi tiếp.
- **Nhiều file hơn dự kiến** → copy đã đụng collateral. **DỪNG, chưa `git add`.** Khôi phục phần ngoài phạm vi:
  ```bash
  git -C <VAULT_ROOT> reset -q                        # bỏ staged nếu đã add
  git -C <VAULT_ROOT> checkout -- <SSOT>/references/ <SSOT>/plans/ <SSOT>/specs/
  git -C <VAULT_ROOT> status --porcelain <SSOT path>  # phải chỉ còn file cua ban
  ```
  Rồi hỏi Bố: đồng bộ luôn support file, hay giữ bản vault.

**🔴 NORMALIZE CRLF TRƯỚC KHI SO CONTENT (git-bash + Windows).**
`git show HEAD:<path>` xuất LF, còn file trên đĩa là CRLF. `diff` không normalize sẽ báo khác **toàn bộ file** (hàng chục KB diff giả) và rất dễ bị đọc thành mất dữ liệu. So identity phải chuẩn hoá:
```python
norm = lambda s: s.replace("\r\n", "\n").strip()
assert norm(committed) == norm(working_copy)
```
`diff -rq` giữa hai file **trên đĩa** thì OK; chỉ so output của `git show` với file đĩa là cần normalize.

### Step 4 — Archive backup
`cp APP_SKILLS/<name>/SKILL.md VAULT_ARCHIVE/<name>_SKILL_backup_YYYY-MM-DD.md`
(Dùng ngày hiện tại YYYY-MM-DD.)
**Completion:** File archive tồn tại trong VAULT_ARCHIVE.

### Step 5 — Git commit + push (repo của profile)
```
cd <REPO_ROOT> && git add <đường dẫn root-relative của tất cả path SSOT của <name>> VAULT_ARCHIVE/<name>_SKILL_backup_*.md
git commit -m "backup: <name> SSOT synced + archive YYYY-MM-DD"
git push origin <branch>
```
**Resolve branch, đừng đoán:** `git -C <REPO_ROOT> branch --show-current`. Các vault khác nhau dùng branch khác nhau (một repo `master`, repo kia `main`). Đoán sai → `git push origin master` fail với `src refspec master does not match any`, dễ bị đọc nhầm thành "chưa commit xong".
**Git root không phải luôn là vault:** porcelain output là root-relative (thường `vault/...`), nên `git add .scripts/...` khi đang đứng trong vault là **sai path**. Chạy git từ root bằng `git -C <REPO_ROOT>`, hoặc `git rev-parse --show-toplevel` để xác nhận trước.
**Completion:** `git ls-files <tất cả path SSOT>/<name>/SKILL.md` trả về path (đã tracked remote). Push không lỗi.

### Step 6 — Print token + report
In dòng: `📦 ARCHIVE: ✅ <name>` + tóm tắt (profile, repo, commit hash ngắn).
In `✅ GATES: sync✓ archive✓` vào cuối.

## Inbound direction — install a skill from a SOURCE ARCHIVE (reverse of Step 3)

Trigger: Bố drops a zip/skill bundle in chat or hands over an external skill file, and it must
land in vault SSOT + the AppData pool. Steps 1-2 still apply (resolve paths, mkdir). From there:

1. **Extract flat into scratch.** `mkdir scratch/x && cd scratch/x && unzip` double-nests when the
   archive already contains its own top-level dir — the output then looks like a defect in the
   source when it is only an artifact of extracting into a pre-named folder. `find` for the real
   `SKILL.md` depth, then copy the inner dir.
2. **Run the taxonomy gate BEFORE creating** (`skill-taxonomy-gate`): pick a domain prefix, list
   that domain, measure overlap. ≥70% → EXTEND the existing skill instead of adding a twin.
3. **Add YAML frontmatter to every `.md` the commit will stage.** The repo's `pre-commit` hook runs
   `validate-yaml.ps1 -StagedOnly` and FAILS the commit on any staged `.md` without frontmatter —
   including `references/*.md` that shipped bare. Match the convention already used by sibling
   reference files in the same tree. Frontmatter is metadata; never rewrite the body to satisfy it.
4. **Vietnamese prose in a skill is fine.** `english_code_check.py` rates any `.md` under
   `.scripts/skills/` as WARN, not FAIL — only `.py/.js/.ts/.sh/.ps1` style files hard-block on
   non-English. Read the severity before translating a body to satisfy A53.
5. **Run git from the REPO ROOT, which sits one level ABOVE the vault.** Porcelain output is
   root-relative (`vault/...`), so paths passed to `git add` from inside the vault are wrong.
   `.scripts/` is not gitignored here, so SSOT skill files are tracked from that path.
6. **Scoped add only** — see the `git add` pitfall below; a repo-wide add sweeps in unrelated dirty
   case files.
7. **Copy SSOT → AppData profile skills dir**, then `diff -r` the two trees.
8. **Verify by loading, not by listing.** `skill_view(<name>)` returning the body plus
   `linked_files` proves the runtime can actually discover the skill; a successful `ls` only proves
   bytes exist. Diff SSOT against `git show HEAD:<path>` to prove the body survived the frontmatter
   edit unchanged.

**A gate rejection is not a content defect.** When a hook rejects the commit, read the hook's own
check before concluding the payload is wrong — it is usually a repo-level convention the payload
predates. Fix the convention, and say so explicitly rather than quietly editing the substance.

## Bulk Mirror Sync (multiple skills)
Khi cần sync toàn bộ skill library → xem `references/bulk-mirror-sync.md` (script `vault/scripts/sync_skills_to_vault.sh`, weekly cron).

## Bulk DRIFT reconciliation (guard báo N skill lệch)
Khi một guard/scan báo **N skill lệch giữa SSOT và mirror** và Bố bảo xử lý: KHÔNG `cp` theo danh sách. Phần lớn `MISSING` là skill **đã bị archive/purge ở mirror** (số lệch đó là trạng thái ĐÚNG), và phần lệch thật phải chia theo bằng chứng máy quyết được — version/subset quyết chiều, "lệch 2 chiều" thì bỏ vào tay người.
Quy trình đầy đủ (triage → classify → apply → verify → regenerate scan): `references/bulk-drift-reconciliation.md`.

## Pitfalls
- **Gate từ chối = kiểm tra quy ước repo, ĐỪNG tưởng payload sai:** pre-commit chặn vì thiếu YAML frontmatter trong `references/*.md` là quy ước **mà payload chưa kịp theo kịp**, không phải nội dung hỏng. Trước khi vá, **đếm chuẩn đang được giữ**: nếu hàng trăm file `references/*.md` đã tracked đều có frontmatter ⇒ file mới của bạn là ngoại lệ, sửa theo chuẩn chứ đừng `--no-verify`. Tương tự, hook A53 chỉ chặn **dòng bạn thêm** — quét `git diff` phần `+` của bạn để biết vi phạm nào là của bạn, đừng đi sửa hàng loạt comment cũ (WARN trong `.md` cũng không chặn, chỉ `.py/.js/.ts/.sh/.ps1` mới FAIL).
- **Commit KHÔNG đồng nghĩa chưa push — post-commit hook có thể tự push:** vault này có post-commit hook `[Sync] Auto-syncing to remote...`. Sau `git commit` phải `git fetch` rồi verify **nội dung file của bạn trên remote** (`git show origin/<branch>:<path> | grep -c "<marker>"`), KHÔNG dựa vào `HEAD == origin` (xem COLLATERAL GATE + Q4 note: khi nhiều session cùng repo, HEAD dịch không liên quan tới bạn). Nếu chưa verify, báo "xong" trong khi code còn nằm local là lỗi. Và **token chỉ ghi bước bạn tự chạy**: commit xong mà chưa verify remote thì message chỉ ghi `Q0✓ Q0a✓ Q1✓`, đừng điền `Q2✓ Q3✓`.
- **Q4 mirror là HARD, không phải tuỳ chọn** (bài học 26/09): patch skill ở profile này mà không mirror sang vault của profile khác ⇒ skill đó ở đó vẫn là bản cũ, thiếu Step 3b/COLLISION GATE. ACV: warren vault còn 6.352B/89 dòng vs stock 14.137B/182 dòng. Fix: sau khi commit, copy sang `.scripts/skills/<name>/` của TẤT CẢ vault liên quan + `references/` + commit/push riêng (repo khác, gate token riêng, hook riêng). **Hai vault có thể lệch version cả năm** (warren v3.12 vs stock v3.13 cùng một skill) → mtime check ở trên là bắt buộc, đừng giả định nguồn nào mới hơn.
- **Q4: bản support file có thể vi phạm YAML gate ở vault đích:** copy xong chạy YAML check trên **đích** trước khi `git add`, vì mỗi repo có hook riêng — vault đích có thể chạy `validate-yaml.ps1 -StagedOnly` trong khi repo nguồn không có. Gate fail = dừng, không `--no-verify`.
- **`pre-commit` hook chỉ có ở MỘT số vault** (ACV 26/09): warren vault chạy `validate-yaml.ps1 -StagedOnly` và chặn `references/*.md` thiếu frontmatter; stock vault **không có hook nào**. Đừng khẳng định "repo này cũng vậy" — check `.git/hooks/` từng repo. Frontmatter là metadata, thêm vào đầu file, KHÔNG sửa body.
- **SSOT có thể tồn tại 2 path — `find` TRƯỚC khi cp, `diff` MỌI bản** (bài học 2026-09-26): Cùng 1 skill có thể nằm ở CẢ `.scripts/skills/<name>/` lẫn `.scripts/skills/<cat>/<name>/` (ACV: `roster-labor-planning` có 2 bản, 618 vs 642 dòng, đều v1.0.0, trong khi mirror là v1.1.0 737 dòng). Cả COLLISION GATE lẫn verify `diff -rq` ở Step 3/Verify đều chỉ chạy trên MỘT path → copy xong báo "synced" trong khi bản thứ hai vẫn cũ, và version-guard chỉ so một path nên báo DRIFT theo bản chưa dùng tới. Fix: `find <VAULT_SSOT> -ipath "*<name>*" -name SKILL.md` → copy vào **TẤT CẢ** bản tìm được, `diff -rq` từng bản, và hỏi Bố xem bỏ `ops/` hay bỏ path phẳng để dọn còn 1 SSOT.
- **Kết luận "đã sync" phải grep trên đĩa, không tin cờ success của `cp`** (2026-09-26): `cp`/`skill_manage` báo thành công nhưng file đích vẫn có thể còn bytes cũ. Luôn `grep -c "<marker-vừa-thêm>" <đích>` sau khi copy, rồi mới nói đã đồng bộ.
- **Symlink stock** → tưởng stock có skills riêng. Fix: stock-profile = warren vật lý, SSOT luôn về warren.
- **personal chưa có .scripts** → cp fail. Fix: Step 2 tự mkdir.
- **Bố patch chưa xong đã sync** → copy bản dở. Fix: Bố chỉ gọi sync khi đã sửa xong.
- **AppData không phải SSOT** → nếu sau này sửa trực tiếp SSOT quên sync ngược, AppData cũ. Fix: luôn coi AppData là "bản làm việc", SSOT vault là "bản thật".
- **Đích SSOT đang có diff chưa commit của session khác** → `cp -r` xoá mất. Fix: chạy COLLISION GATE ở Step 3, dừng và hỏi Bố. Đừng "cứ copy vì file cùng tên" — marker grep mới chứng minh được bản đó là của bạn.
- **Diff to khong bao gio nghia nuot viec nguoi khac:** ACV 26/09 commit `+79/−38` trông như xoá 45 dòng của session khác, nhung 45 dòng do la ban 7-bot cu bi thay bang 9-analyst — **co chu dich**. Fix: khi merge xong so sanh TINH CHAT (`version`, so bot/role, tung pitfall D1-D5, cac marker cua ca 2 ben), KHONG dem dong. So dong chi la tin hieu, khong phai bang chung.
- **Dung bao dong "mat du lieu" roi revert bang mau:** ACV 26/09 con rollback 2 lan (mot lan that su, mot lan do phong doan) truoc khi doc ky diff. Fix: doc toan van `diff` TRUOC khi hanh dong; rollback la hanh dong phan huy nen phai co bang chung, khong phai do nghi.
- **Backup merge phai `rm` truocc `git add`:** neu giu file `.merge-backup` thi no lot vao commit nhu rac. Fix: xoa backup ngay sau B3/B4 PASS, truocc khi stage.
- **git add <dir> TRƯỚC khi patch file → commit thiếu file (bài học 2026-08-07):** nếu `git add meme-text-overlay/` chạy trước khi patch SKILL.md, commit sẽ KHÔNG chứa SKILL.md (lúc add file chưa đổi). FIX: patch xong MỚI `git add <file_cụ_thể>`, rồi `git show HEAD --name-only` verify file nằm trong commit trước khi push. Scoped commit (chỉ add file đổi) cũng tránh kéo theo đổi lạ của Bố/cron chưa duyệt.
- **Archive backup phải là PRE-fix rollback point:** Step 4 cp SKILL.md HIỆN TẠI — nếu skill đã patch xong mới archive, backup chứa post-fix content, vô dụng làm rollback. FIX: khi archive quanh 1 lần patch, lấy bản PRE-change từ git (`git show <commit-trước-patch>:<path> > archive`) và verify archive KHÔNG chứa lesson/version marker mới. Tại sao: rollback point đã chứa fix thì không rollback được gì. **Verify bắt buộc:** `archive == SKILL.md sau patch` ⇒ archive vô hiệu, phải xoá và nói rõ không có pre-fix point thay vì để lại. (ACV 26/09: archive 14.137B trùng khít SKILL.md hậu-patch, tự chứa pitfall "Archive backup phải là PRE-fix" — tự vô hiệu.)

## Verify (bắt buộc trước báo xong)
- `diff -rq` AppData vs **TẤT CẢ** SSOT path = IDENTICAL.
- `git ls-files` **TẤT CẢ** SSOT path/SKILL.md có trên remote.
- Archive file tồn tại.
Thiếu 1 trong 3 → chưa xong, báo Bố.
