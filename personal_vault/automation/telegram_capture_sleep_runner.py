#!/usr/bin/env python3
"""Wrapper: run telegram_health_poller.py (in Personal_OS vault) once.

Cron requires the script in ~/.hermes/scripts/; the real logic lives in
personal_vault/scripts/telegram_health_poller.py so it can reuse
process_sleep.py / telegram_notify.py imports.
"""
import subprocess
import sys
from pathlib import Path

TARGET = Path(
    r"C:\Users\khoans\Documents\Personal_OS\personal_vault\scripts\telegram_health_poller.py"
)
CWD = Path(r"C:\Users\khoans\Documents\Personal_OS\personal_vault\scripts")

if __name__ == "__main__":
    # --once: single poll cycle (get updates, process reply, process new msg)
    cmd = [sys.executable, str(TARGET), "--once"]
    r = subprocess.run(cmd, cwd=str(CWD), capture_output=True, text=True)
    print(r.stdout)
    if r.stderr:
        print(r.stderr, file=sys.stderr)
    sys.exit(r.returncode)
