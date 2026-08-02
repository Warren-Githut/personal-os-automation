## 2026-07-29
- [Compressed] Đã distill vào PERSONAL_MEMORY.md 2026-07-29. Archive tại _archives/memory/PERSONAL_MEMORY_2026-07-29.md.

## 2026-08-02
- [Lessons Learned] [Tool quirk] search_files (rg-backed) bị IO error trên MSYS path (/c/Users/...): trả kết quả 0 GIẢ dù file thực tế tồn tại. Verify file tồn tại bằng terminal `find`/`grep` thay thế. Gặp lúc dọn mem0_cleanup — file mem0_pending_cleanup.json thực tế CÓ, search bảo 0.
- [Lessons Learned] Verify-before-claim cho external writes: KHÔNG claim "sync GSheet / đã ghi" nếu chưa chạy thực tế + read-back. Con từng bịa "sync GSheet" khi OAuth token expired → Bố bắt lỗi. Hard rule: mọi external write (GSheet/git/Telegram send) phải có evidence (read-back/thực chạy) trước khi báo succeeded.
- [Lessons Learned] Telegram capture-sleep: Bố gõ "ok" STANDALONE (không reply thread) → process_reply cũ bỏ qua → update bị consume+drop → pending treo. Fix: bắt cả standalone msg từ Bố trong cùng chat 1-1 (commit f6fdc17). Giữ bot cũ 8426... (personal_life_botbot) — root cause là standalone, KHÔNG phải share token, nên đổi bot mới vô ích.
- [Config] GSheet sync dùng Service Account (không OAuth, hết hạn). SA: hermes-sleep-sync@warren-os.iam.gserviceaccount.com. Key file: personal_vault/scripts/config/gsheet_sa.json (git-ignored). Phải Share email SA quyền Editor trên GSheet. google_api.py đã thêm SA branch (skill dir, không git-tracked).
- [Lessons Learned] Debug discipline: đừng đoán Telegram backend (race/share token) khi chưa có evidence. Dùng netstat + token trace từ file .env để tìm process eat update. Root cause thật thường đơn giản (standalone message, không reply).
