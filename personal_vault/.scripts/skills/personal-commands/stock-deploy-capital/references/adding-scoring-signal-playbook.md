# Playbook: Thêm tín hiệu scoring mới vào hệ thống Stock

> Khi Bố muốn thêm 1 tín hiệu định tính/new signal vào hệ thống chấm điểm (vd: insider actual buy, ESG, dividend hike...). Worked example: Insider Actual Buy (2026-08-02).

## Chuỗi file cần chạm (theo thứ tự)
1. **Tạo SSOT vault file** — `030-Companies/100_Compliance/<Signal>.md` (hoặc folder phù hợp). Template: mỗi event = 1 block, fields rõ ràng, có cơ chế update + cross-ref.
2. **Patch `management-quality-checklist.md`** (warren-profile/skills/stock-deploy-capital/references/) — thêm tiêu chí (binary PASS/FAIL hoặc bonus +điểm). Reference SSOT path.
3. **Patch `stock-deploy-capital` SKILL.md check #7** — ghi rõ điểm cộng/bớt + link tiêu chí #.
4. **Patch `stock-ingest` SKILL.md** — thêm bước nhắc Bố update signal khi ingest BCTC (vd step 6.5).
5. **Update `00_WIKI_INDEX.md`** (vault, path `30_KNOWLEDGE_BASE/wiki/00_WIKI_INDEX.md`) — bump `total_files`, thêm dòng nếu tạo folder mới.
6. **Backup + commit** — backup file cũ vào `_archives/skills/` TRƯỚC khi patch; git commit cuối (SOUL §5.4 Commit-Push Self-Gate).

## Pitfalls (bài học 2026-08-02)
- **Cross-profile guard:** `stock-deploy-capital` + `stock-ingest` SKILL.md thuộc **warren-profile** dù execute từ stock-profile. Mọi patch cần `cross_profile=True` + Bố approve. Dùng `skill_manage(action='patch', cross_profile=True)` — KHÔNG dùng `patch` tool thường (bị guard chặn, báo path warren-profile).
- **Verify path bằng terminal, không search_files:** search_files trả về 0 / IO error trên file CÓ THẬT (00_WIKI_INDEX.md, stock-ingest/SKILL.md trong session này). Dùng `terminal: find <path> -iname '*pattern*'` để confirm thực tế trước khi patch. (Không capture là "tool hỏng" — chỉ là fallback.)
- **actual-vs-registered (quan trọng cho insider):** CHỈ tính THỰC MUA (actual settled), KHÔNG tính đăng ký. Ví dụ: TGD ĐK mua 100 tỷ (01/08→31/08), hết window chỉ mua 50 tỷ vì "giá không thích hợp" → ❌ KHÔNG đạt. Luôn chờ Bố báo kết thúc window mới update actual.
- **Ad-hoc trigger:** signal insider là ad-hoc → thiết kế 2 bước: (1) Bố báo đăng ký → tạo block Status=Registered, THỰC MUA=0; (2) Bố báo kết quả → update THỰC MUA + Meets. KHÔNG tự đoán actual = registered.
- **Scoring weight:** bonus signal nên nhỏ (+2/10) để không lật ngược nhóm; KHÔNG penalize khi chưa có event (chỉ không cộng).

## Worked example: Insider Actual Buy
- SSOT: `030-Companies/100_Compliance/Internal_Dealing.md`
- Checklist #9: THỰC MUA ≥100 tỷ → +2/10 vào check #7 (`stock-deploy-capital`).
- `stock-ingest` step 6.5: nhắc Bố mỗi kỳ ingest BCTC.
- Bố duyệt folder `100_Compliance` (không 041) — compliance/meta dùng prefix `100_` tách khỏi company folders (`03X-`).
- SSOT file template có HTML comment ghi rõ cơ chế update 2 bước + actual-only rule.
