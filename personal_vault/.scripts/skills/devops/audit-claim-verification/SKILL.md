---
name: audit-claim-verification
description: "Use when challenging audit findings. Re-verify on disk."
version: 1.0.0
category: devops
tags: [audit, verification, adversarial, reviewer, skills, windows]
related_skills: [reviewer-node, skill-bundle-audit, hermes-skill-audit, skill-dedup, skill-audit-pitfalls]
---

# audit-claim-verification — Re-verify audit findings on disk

> **Class:** Bất kỳ khi nào con nhận một audit report (skill audit, duplicate list, "safe to delete" list, cron health check) và phải đóng vai adversarial reviewer — KHÔNG tin claim nào, mọi verdict phải backed bằng lệnh thật trên disk.
> **Mode:** Read-only. Không sửa gì trong lúc verify. Output = per-claim CONFIRMED / DISPUTED / MIXED + evidence.

## Khi nào dùng
- Warren yêu cầu "challenge audit findings" / reviewer-node mode cho một audit report.
- Trước khi thực thi bất kỳ delete/archive list nào do audit khác đề xuất.
- Khi audit claim nghe "quá gọn" (vd: "16 duplicates", "all symlinks") — các claim gộp hàng loạt thường sai một phần.

## Probe playbook (đã E2E 2026-07-26 trên warren-profile skill audit)

### P1 — Windows symlink/junction: dùng fsutil, KHÔNG dùng find -xtype l
`find -xtype l` chỉ bắt POSIX symlink, bỏ sót Windows junction/reparse point → false negative.
```bash
fsutil reparsepoint query "C:\\path\\to\\dir" >/dev/null 2>&1 && echo REPARSE || echo "real dir"
```
Bẫy đã gặp: audit claim "16 dirs là symlink nên duplicate là false positive" → cả 16 là real dir, lý do audit sai hoàn toàn.

### P2 — Duplicate claim: md5sum + diff -rq, đừng tin tên trùng
```bash
md5sum "$A/SKILL.md" "$B/SKILL.md"          # single skill
diff -rq "$A" "$B" | wc -l                   # 0 = byte-identical dir
```
Bẫy: 16 category dirs trùng tên → chỉ 6 byte-identical; 10 cái diverged, bên profile chứa skill riêng (lusine-*, cron-job-ops...). Xóa theo tên = mất data thật. Luôn phân loại identical vs diverged trước khi phán "duplicate".

### P3 — Tên directory ≠ frontmatter `name:`
Live dir `skills/agent-skills/` chứa SKILL.md có `name: apply-agent-skills` (ACTIVE), còn `.archive/agent-skills/` mới là bản archived. Trước khi confirm "safe to delete": đọc frontmatter `name:`, tra `.usage.json` theo NAME đó (state/use_count/archived_at), không tra theo tên folder.

### P4 — .usage.json validate HAI CHIỀU
- Entry tồn tại ≠ skill tồn tại (đã gặp 3 entry use=0 không có dir — stale record, không phải "zero-use skill deletable").
- Dir tồn tại ≠ có entry. Cross-check cả hai chiều trước khi tin bảng "zero-use".

### P5 — Cron-referenced skills/scripts
`cron/jobs.json` = `{"jobs": [...], "updated_at": ...}` (dict wrapper — đừng iterate values() trực tiếp). Mỗi job check: `enabled`, `skills[]`, `skill`, `script`, workdir, `last_run_at`, `last_status`.
- Skill ref → find dir (exclude *archive*) + confirm SKILL.md tồn tại.
- Script ref → tìm lần lượt: workdir của job → `Warren_OS_Local/vault/.scripts/` → `profiles/warren-profile/scripts/`.
- Đếm đủ job `last_run_at=None` (never-run) — audit gốc đếm sót 1 job.

### P6 — Broken internal refs sweep
Python quét mọi SKILL.md (skip `.archive`, `_archive*`, `__pycache__`), regex `(?:scripts|references|templates|assets)/[\w\-.]+\.(py|md|json|yaml|yml|sh|html|txt)`, check `os.path.exists` relative to skill dir. Baseline 2026-07-26: 167 broken / 269 skills. CAVEAT: lọc prose placeholder (`scripts/foo.py`, `scripts/X.py`, `references/X.md`) và refs cố ý trỏ ra vault `.scripts/` — không phải broken thật.

### P7 — Archived-but-still-referenced
```bash
for a in .archive/*/; do grep -rl "$(basename $a)" skills/ --include=SKILL.md | grep -v .archive | wc -l; done
```
Dangling pointer vào `.archive/` = new finding audit thường bỏ sót. Baseline 2026-07-26: deep-research-stock (2), ops-pl-13_Monthly_PL_Breakdown (2), pdf-parse (4), personal-stock-ingest (4).

### P8 — Overlap-group claims: đọc description từng thành viên
`grep -m1 '^description:' <skill>/SKILL.md` cho TỪNG skill trong group trước khi công nhận redundancy. Bẫy đã gặp: pre-flight gate (`restate`) bị gộp nhầm vào nhóm review; category folder (`vault`) bị đếm như skill; 2 skill cùng domain nhưng khác mode (promo-eval = eval 1 promo, promo-comparison = so sánh 2) — related ≠ redundant.

## Pitfalls môi trường
- `execute_code` bị BLOCK dưới cron approval mode → fallback `terminal` + heredoc `python - <<'EOF'`.
- `search_files` với path `C:/Users/...` có thể lỗi MSYS mount → dùng terminal grep/python trực tiếp.
- jobs.json: job list nằm trong key `"jobs"`, top-level là dict.

## Output format
Per-claim: **CONFIRMED / DISPUTED / MIXED** + lệnh & kết quả làm evidence. Bắt buộc thêm 2 section: "New findings the audit missed" và "Bottom line". Nêu rõ cả false-positive lẫn false-negative (đếm sót cũng là lỗi).
