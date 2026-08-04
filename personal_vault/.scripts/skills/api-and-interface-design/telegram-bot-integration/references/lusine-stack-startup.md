# L'Usine Stack Startup Procedure

> Created 2026-06-26. Script: `C:\Users\khoans\Desktop\Khoi Dong LUsine Stack.bat`

## Dependency Order

Mem0 cần **cả** Qdrant (vector DB) và Ollama (embeddings) để hoạt động. Không đúng thứ tự → Mem0 báo `No connection (10061)`.

```
Ollama (embeddings)          → cần 30s load models
    ↓
Qdrant (vector DB, port 6333) → cần 5s listen
    ↓
Hermes Gateway (API service)  → cần 3s init
    ↓
L'Usine Work Bot (Telegram @lusine_work_bot)
```

## Chi tiết từng bước

| Bước | Service | Script | Thời gian chờ |
|------|---------|--------|---------------|
| 1 | **Ollama** | `C:\Users\khoans\AppData\Local\Programs\Ollama\ollama app.exe` | 30s (load models) |
| 2 | **Qdrant** | `C:\Users\khoans\AppData\Local\qdrant\start_qdrant.bat` → `localhost:6333` | 5s (listen) |
| 3 | **Hermes Gateway** | `C:\Users\khoans\AppData\Local\hermes\gateway-service\Hermes_Gateway.cmd` | 3s |
| 4 | **L'Usine Work Bot** | `C:\Users\khoans\Desktop\Start L'Usine Work Bot.bat` | — |

## Kiểm tra

```batch
tasklist | findstr "ollama qdrant python"
```

Mem0 chỉ hoạt động khi Qdrant + Ollama cùng chạy.

## Script tự động

`C:\Users\khoans\Desktop\Khoi Dong LUsine Stack.bat` — double-click start toàn bộ.

## Auto-start với Windows

```
%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\
├── Ollama_AutoStart.bat
├── Qdrant_Server.lnk
├── Hermes_Gateway.cmd
├── start_lusine_bot.bat       # → pythonw.exe launch_bot.py (preferred, no console)
└── start_lusine_bot.bat       # → .bat with :loop (legacy, has orphan window risk)
```

**Preferred:** `start_lusine_bot.bat` calls `pythonw.exe launch_bot.py` — no console window, no `:loop`, watchdog handles restarts.

**Legacy:** .bat with `:loop` and `python -m lusine_ops.telegram_bot` — creates a visible cmd window. Use only when watchdog is not deployed.

> **Corporate laptop note:** `schtasks /create` is often blocked. Startup folder is the zero-friction alternative (no admin required).
