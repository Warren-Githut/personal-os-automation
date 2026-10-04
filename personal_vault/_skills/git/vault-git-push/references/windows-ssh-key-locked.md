# Windows SSH Private-Key ACL Lock — Diagnostic + Fix

Captured 2026-07-20 (vault push failure, Warren_OS_Local → GitHub SSH).

## Symptom
`git push` fails:
```
Load key "/c/Users/khoans/.ssh/id_ed25519": Permission denied
git@github.com: Permission denied (publickey).
fatal: Could not read from remote repository.
```
Switching remote to SSH, adding host key, still fails. Looks like "auth rejected" but it is NOT.

## Diagnostic (the key step — distinguishes local lock vs GitHub rejection)
```bash
ssh -v -o BatchMode=yes -o IdentitiesOnly=yes -i ~/.ssh/id_ed25519 -T git@github.com 2>&1 | grep -iE "publickey|denied|offering|accept"
```
Output that proves a LOCAL file lock (NOT a GitHub auth problem):
```
debug1: Server accepts key: /c/Users/khoans/.ssh/id_ed25519 ED25519 SHA256:... explicit
Load key "/c/Users/khoans/.ssh/id_ed25519": Permission denied
git@github.com: Permission denied (publickey).
```
- "Server accepts key" = GitHub has this pub key and would let you in.
- "Load key ... Permission denied" = the SSH client on THIS machine cannot READ the private-key file (Windows ACL blocks it).
- If instead you saw ONLY "Permission denied (publickey)" with no "Server accepts key", then the key is genuinely not registered on GitHub → add it there.

## Why `chmod` does not fix it
```bash
chmod 600 ~/.ssh/id_ed25519
chmod: changing permissions of '/c/Users/khoans/.ssh/id_ed25519': Permission denied
```
On this Windows/MSYS setup the file is locked at the **ACL layer** (likely OneDrive/sync or owner mismatch), not the POSIX mode bit. `chmod` cannot override it. Do NOT try to hand-edit Windows ACL (zone 🔴 — system config, needs Warren).

## Fix — generate a FRESH key (fresh file gets correct perms)
```bash
# backup old (do not delete)
cp ~/.ssh/id_ed25519 ~/.ssh/id_ed25519.bak 2>/dev/null

# fresh key — no passphrase, correct perms by creation
ssh-keygen -t ed25519 -f ~/.ssh/id_ed25519_new -N "" -C "warren-laptop"

# show the NEW public key — give this to Warren to paste into GitHub
cat ~/.ssh/id_ed25519_new.pub
# -> ssh-ed25519 AAAA... warren-laptop
```
Then Warren (non-IT, copy-paste only):
1. Open https://github.com/settings/ssh/new
2. Title: `warren-laptop`
3. Key: paste the `ssh-ed25519 ... warren-laptop` line
4. Click "Add SSH key"

Back in terminal — point git at the new key permanently for this repo:
```bash
git config core.sshCommand "ssh -i ~/.ssh/id_ed25519_new -o IdentitiesOnly=yes"
ssh -o BatchMode=yes -i ~/.ssh/id_ed25519_new -T git@github.com
# -> Hi Warren-Githut! You've successfully authenticated...
git push origin master   # SUCCESS
```

## Notes
- The OLD key's pub key had already been added to GitHub (that's why "Server accepts key" appeared) — but the local private file was unreadable. Re-adding won't help; a fresh key file is the fix.
- `git config core.sshCommand` is repo-local (no `--global`) — safe, scoped to Warren_OS_Local.
- After this, future pushes are zero-friction (key-based, no password/TTY).
- Host key: first SSH push may need `ssh-keyscan -t ed25519,rsa github.com >> ~/.ssh/known_hosts` if "Host key verification failed".
