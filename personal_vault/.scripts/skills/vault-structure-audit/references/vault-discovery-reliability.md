# Vault Discovery Reliability — Windows/MSYS Pitfall

**Phát hiện:** 2026-07-17, stock-profile session. Warren gửi PDF báo cáo GD TCBS (PNJ) và hỏi thesis PNJ ở đâu. Hermes chạy `search_files(target='files', pattern='*')` qua nhiều cấp (`03_Investing`, `VN_Equities`, `030-Companies`, `040-PNJ`) → tất cả trả `total_count: 0`. Hermes 2 lần kết luận "vault không có PNJ thesis". Warren bực: "sao con ko biết gì hết vả", "con check toàn bộ trong này, ko có của PNJ thesis à?".

**Sự thật:** folder `040-PNJ` có thật và chứa 4 file:
```
040-PNJ/
├── Thesis.md          (10.7KB)
├── Anti-thesis.md    (5.8KB)
├── BCTC - Rolling.md (5.7KB)
└── Catalyst-watch.md (3.8KB)
```
`search_files` miss hoàn toàn. `terminal` + `ls`/`find` reveal ngay lập tức.

## Nguyên nhân (giả thuyết)
- `search_files` dùng ripgrep backend, có thể bỏ qua subfolder sâu hoặc folder có `.smart-env/` indexing sidecar trên Windows/MSYS git-bash.
- Không phải permission error (Hermes vẫn đọc được file cùng gốc qua `read_file`).

## Quy tắc vàng
1. **User nói file có ở path X > kết quả search_files âm. Tin user.**
2. **Trước khi kết luận "không tồn tại", luôn verify bằng terminal:**
   ```bash
   # List trực tiếp folder user chỉ định
   ls -la "C:/Users/khoans/Documents/Stock_OS/stock_vault/30_KNOWLEDGE_BASE/wiki/03_Investing/VN_Equities/030-Companies/040-PNJ/"
   # Tìm theo tên trong toàn bộ vault (bỏ qua search_files)
   find "C:/Users/khoans/Documents/Personal_OS" -iname "*PNJ*" 2>/dev/null
   ```
3. `ls` / `find` qua terminal là **source of truth** trên setup này. `search_files` chỉ là heuristic nhanh, không dùng để xác nhận sự vắng mặt.

## Command mẫu tái sử dụng
```bash
# Verify 1 folder cụ thể
ls -la "<native_windows_path>"

# Tìm file theo substring trong toàn vault
find "<vault_root>" -iname "*<keyword>*" 2>/dev/null
```

## Impact
Sai kết luận "file không có" làm Hermes (a) bỏ qua thesis hiện có, (b) đề xuất tạo file trùng lặp, (c) làm user mất niềm tin. Verify bằng `ls` trước khi nói "không có" — tốn 1 tool call, cứu 1 round-trip bực mình.
