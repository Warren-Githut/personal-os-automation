# Standard .gitignore — warren-profile (2026-07-17)

Copy block dưới vào `C:/Users/khoans/AppData/Local/hermes/profiles/warren-profile/.gitignore`.

```gitignore
# === Hermes profile system (keep) ===
.git/
skills/
.bundled_manifest
.usage.json
.git_auto_backup.sh
.hub/
.curator_*/
.archive*/
_archive_*/

# === SECRETS — NEVER commit ===
.env
*.env
auth.json
auth.lock
google_token.json
google_client_secret.json
*.token.json
credentials.json
client_secret.json
secrets.json

# === Databases / state ===
*.db
*.db-shm
*.db-wal
state.db
state.db-shm
state.db-wal
projects.db
verification_evidence.db
state-snapshots/

# === Runtime / cache / logs ===
cache/
logs/
lsp/
bin/
storage/
sessions/
cron/
gateway-service/
desktop-build-stamp.json
context_length_cache.yaml
models_dev_cache.json
ollama_cloud_models_cache.json
provider_models_cache.json
qdrant-initialized
.update_check
.update_exit_code
.channel_directory.json
.gateway_state.json
.processes.json

# === Personal memory ===
memories/
MEMORY.md
USER.md
WARREN_MEMORY_SYNC.md
*.bak.*
*.lock

# === Config with secrets (chứa api_key thật) ===
config.yaml
config.yaml.bak.*
channel_directory.json
gateway_state.json
processes.json
scripts/
templates/

# === Leftover flags ===
.qdrant-initialized
.update_check
.update_exit_code

# === Token fix script (chứa token thật) ===
fix_token.py
```

## Verify sau khi ghi
```bash
cd C:/Users/khoans/AppData/Local/hermes/profiles/warren-profile
git check-ignore -v google_token.json .env config.yaml state.db memories/MEMORY.md
# all → ignored
```
