---
name: audit-automation
description: "Workflow health check — quét cron jobs, skills, delegation zones cả 3 profiles. Phát hiện silent failures, stale workflows, zone drift."
version: 1.0.0
related_skills: ["cron-silent-failure-scan"]
author: Hermes
trigger: "/audit-automation [--all]"
---

# /audit-automation — Workflow Health Check

> **Định kỳ:** Chủ Nhật 19:00 (cron). Thủ công: `/audit-automation` (profile hiện tại) hoặc `/audit-automation --all` (cả 3).

---

## Khi được trigger

Hermes thực hiện 3 bước sau theo đúng thứ tự.

### Step 1: CHECK CRON JOBS

Dùng `cronjob list` để lấy toàn bộ cron jobs.

Với mỗi job, check:
| Dấu hiệu | Flag | Mức |
|----------|------|-----|
| `last_status = error` | 🔴 **ERROR** — có lỗi, cần xem | Cao |
| `last_status = null` (chưa chạy lần nào) | 🟡 **PENDING** — job mới chưa fire | Thấp |
| `last_delivery_error != null` | 🔴 **DELIVERY ERROR** — output ko đến được | Cao |
| `enabled = false` | 🟡 **PAUSED** — bị tạm dừng | Trung |
| Job no_agent = True + `script` — check script còn tồn tại ko | 🔴 **MISSING SCRIPT** — file script ko còn trên disk | Cao |

**Output mẫu:**
```
─── CRON JOBS ──────────────────────────────
🔴 [job_name] — last_status = error
   → Lần cuối: [datetime]
   → Lỗi: [last_status cụ thể nếu cronjob list cho]
   → Suggest: kiểm tra log / restart

🟡 [job_name] — enabled = false
   → Bị pause từ [date]
```

### Step 2: CHECK SKILLS

Scan skills list của profile hiện tại (nếu `--all` thì scan cả 3).

Với mỗi skill, check:
| Dấu hiệu | Flag | Mức |
|----------|------|-----|
| Skill ko có trong SOUL.md Quick Reference hoặc HERMES_COMMANDS.md | 🟡 **ORPHAN** — tồn tại nhưng ko documented | Trung |
| Skill có lỗi runtime (nếu Hermes có tracking) | 🔴 **ERROR** | Cao |
| Skill rõ ràng là stale (VD: cái cũ đã replaced) | 🟡 **STALE** — đề xuất archive | Trung |

**Không cần kiểm tra từng skill chi tiết** — Hermes tự biết skill nào active hay ko qua interaction history.

### Step 3: CHECK ZONES

Đọc SOUL.md §5.1 (DELEGATION ZONES) của profile hiện tại (nếu `--all` thì cả 3).

Với mỗi zone entry, check:
| Phát hiện | Flag | Mức |
|-----------|------|-----|
| Skill/cron ổn định >4 tuần, ko lỗi, đang ở 🟡 | 🟢 **PROMOTE candidate** → gợi ý lên 🟢 | Thấp (gợi ý) |
| Skill/cron lỗi liên tục, đang ở 🟢 | 🟡 **DEMOTE candidate** → gợi ý xuống 🟡 | Trung |
| Task đang ở zone sai rõ ràng | 🟡 **ZONE DRIFT** | Trung |
| Zone 🔴 trade cho stock-profile | 🔴 **CONFIRMED** — giữ nguyên | Info |

### Step 4: TỔNG HỢP BÁO CÁO

```
═══════════════════════════════════════════
📋 AUDIT AUTOMATION — [Thứ, Ngày] [Giờ]
═══════════════════════════════════════════

🔴 [N] issues cần xử lý
🟡 [N] warnings cần theo dõi
🟢 [N] OK

─── CRON JOBS ──────────────────────────────
...

─── SKILLS ─────────────────────────────────
...

─── ZONES ──────────────────────────────────
...

─── GỢI Ý ─────────────────────────────────
PROMOTE: [skill] → 🟢? (ổn định X tuần)
DEMOTE:  [skill] → 🟡? (lỗi gần đây)
KILL:    [cron/skill] → ko còn dùng

─── NEXT STEP ──────────────────────────────
Anh muốn em fix gì trước?
```

---

## Cron schedule

- Tần suất: Chủ Nhật 19:00
- Scope: `--all` (3 profiles)
- Deliver: origin (chat hiện tại)

---

## Boundaries

| Always | Ask First | Never |
|--------|-----------|-------|
| Scan + flag + suggest | Promote / demote zone | Auto-delete cron hay skill |
| Conclusion-first báo cáo | Kill workflow | Auto-act trên trade zone |
| Include lý do cho mỗi flag | | Modify production data |

---

## Verification checklist (after each deploy)

- [ ] `/audit-automation` chạy dc trong warren-profile
- [ ] `/audit-automation --all` quét dc cả 3 profiles
- [ ] Báo cáo ra đúng format
- [ ] Cron job Chủ Nhật 19:00 active
