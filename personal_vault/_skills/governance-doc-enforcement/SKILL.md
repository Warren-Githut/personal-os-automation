---
name: governance-doc-enforcement
description: "Khi tạo vault governance doc — gắn cron+bootstrap guard."
version: 1.0.0
author: Hermes
trigger: "Tạo/migrate bất kỳ vault governance doc; hoặc audit xem governance doc có stale không"
category: vault
tags: ['governance', 'schema', 'staleness', 'enforcement', 'warren-preference']
related_skills: ['vault-structure-audit', 'session-start', 'compress-memory']
---

# governance-doc-enforcement

> **Warren FIRST-CLASS preference (2026-07-25):** *"Bố ghét nhất tạo xong rồi ko ai update."*
> Mọi governance artifact PHẢI có **machine-enforced update hook**. Agent tự nhớ "sẽ update" = KHÔNG đủ, sẽ stale.

## Core Rule

Governance doc (VAULT_MAP.md, ONTOLOGY.md, ADR, schema doc, checklist, ANCHORS) mà không có
bot/cron guard = sẽ stale. **Tạo là phải gắn enforcement ngay** — cùng lúc với tạo doc, không để sau.

## Standard Pattern (rút từ VAULT_MAP.md session 2026-07-25)

1. **Tạo doc** ở `00_CORE_LOGIC/` (zone 🔴 — Warren duyệt trước).
2. **Link từ AGENTS.md** — cho AI biết SSOT nằm đâu.
3. **Load ở session-start** (step 3.x) — doc "sống", không thành file chết.
4. **Nightly cron guard** — script quét violation vs doc, báo `CONSISTENCY_LOG.md` + Telegram.
   - VD: `vault_consistency_nightly.py` B4 (schema compliance vs VAULT_MAP §2).
5. **Bootstrap fallback** — `session-start` check `CONSISTENCY_LOG.md` có open `schema-violation`
   → emit ⚠️ đầu session.

## Resilient Design (máy tắt vẫn bắt)

Cron Hermes là **local** (chạy trên máy Warren, không cloud). Tắt máy = miss.
→ KHÔNG chỉ靠 1 lớp:

| Lớp | Cơ chế | Khi nào bắt |
|-----|--------|------------|
| Primary | Cron đêm 10:00 + 13:00 backup slot (`no_agent`, 0 token) | Máy bật ban đêm |
| Fallback | `session-start` check log → ⚠️ đầu session | Sáng Bố mở chat (luôn bật ban ngày) |

→ Dù máy tắt cả ngày, sáng Bố mở Hermes là con bắt stale. Không phụ thuộc cron.

## PITFALL — B4 False-Positive (2026-07-25 thực tế)

**Strict type-name match giữa 2 taxonomy KHÁC NHAU = spam vàng vô dụng.**

- VAULT_MAP §2 viết type **logic** (`tracking`, `index`, `case`...).
- Vault frontmatter dùng type **thật** (`tracker`×17, `tracking`×16, `rolling_log`×2,
  `ssot-cph`×1, `lusine_snapshot`, `anchor_reference`, `daily_ops`... — 49 distinct).
- So 2 cái = **50+ false positive vàng mỗi đêm** → vi phạm "cron tuyệt đối KHÔNG spam".

**FIX (recommend):** B4 chỉ check **folder-drift**:
- Folder/file KHÔNG có trong VAULT_MAP §2 = schema drift thật (vi phạm zone 🔴 create rule) → báo yellow.
- **BỎ strict type-name match** (hoặc whitelist type thật thay vì tên logic).
- Mục đích B4 = bắt stale VAULT_MAP (folder mới chưa khai báo), KHÔNG phải so 2 taxonomy.

**Verify B4 thực tế (bắt buộc trước báo xong):**
```bash
cd /c/Users/khoans/AppData/Local/hermes/profiles/warren-profile/scripts
python3 vault_consistency_nightly.py --dry-run   # đọc output, đếm violations
```
Nếu >5 false positive do type mismatch → sửa B4 bỏ type-check. KHÔNG deploy nếu chưa dry-run sạch.

## Drift Reconcile Triggers

| # | Trigger | Hành động |
|---|---------|-----------|
| 1 | Warren tạo/move/delete vault file/folder (zone 🔴) | Tại bước đó update map §2 + ghi Reconciliation Log |
| 2 | Nightly cron guard bắt violation | Báo CONSISTENCY_LOG → Warren duyệt update map |
| 3 | `session-start` check log thấy open entry | Emit ⚠️ đầu session, nhắc Bố |
| 4 | `/compress-memory` hoặc "ontology check" | Scan `type:` + folder tree vs map → propose diff |

## Enforcement Checklist (trước tạo governance doc)
- [ ] Warren duyệt tạo file (zone 🔴)?
- [ ] Link từ AGENTS.md?
- [ ] Load ở session-start?
- [ ] Có cron guard quét violation?
- [ ] Có bootstrap fallback check log?
- [ ] Guard chạy `--dry-run` sạch (<5 false positive) trước deploy?

## References
- `references/b4_schema_pattern.md` — code template B4 (folder-drift only) + inventory script type thật.
