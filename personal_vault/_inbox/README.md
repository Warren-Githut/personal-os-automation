---
domain: meta
type: guide
status: active
last_updated: 2026-06-14
---

# _inbox — Decision Tree

> **Quy tắc vàng:** Drop file vào đúng subfolder dưới đây. Hermes tự route khi bạn chạy command.
> Không nhớ command nào? → Drop vào `_inbox/_unsorted/`, mỗi sáng Hermes sẽ route hộ.

---

## 📋 Decision Tree

### Bạn có cái gì?

| Loại input | Drop vào | Command chạy | Output tới |
|---|---|---|---|
| **Audio (voice note)** | `_inbox/voice/` | `/personal-process-voice` | Transcript → `_journal/` |
| **Không biết** | `_inbox/_unsorted/` | (Hermes auto sáng hôm sau) | Tuỳ Hermes decide |

---

## 🎯 80/20 Rule

Bạn không cần nhớ tất cả. Nhớ 2 cái này:

1. **Audio** → `voice/` + `/personal-process-voice`
2. **Mơ hồ** → `_unsorted/` (Hermes sẽ route hộ)

---

## ⚙️ Khi nào dùng prefix `personal-`?

- **CÓ prefix** (`personal-ingest`) → vault Personal_OS (hiện tại)
- **KHÔNG prefix** (`ingest`) → vault Warren_OS_Local (L'Usine)
- **Lưu ý:** Khi mở Hermes Desktop với profile Personal, chỉ cần `/ingest` cũng được — profile sẽ resolve về `personal-ingest`. (Phase P3 sẽ enforce.)

---

## 🚫 KHÔNG drop vào _inbox

- File đã ở vault — đừng duplicate
- File temp/cache — drop vào trash, không phải vault
- File >100MB — hỏi Warren trước

---

*Last review: 2026-06-14 (Phase 0). Update khi command/folder cấu trúc đổi.*
