# Windows Path Resolution Workaround

Reproduced 2026-06-13 on Hermes Agent + Windows host.

## Symptom
- `patch` / `write_file` with `path="/c/Users/khoans/..."` resolves to `C:\c\Users\khoans\...` and fails.
- `read_file` with `/c/Users/...` works.

## Workarounds (pick one per call)
1. Use native Windows style for patch/write_file:
   `path="C:\\Users\\khoans\\..."`
2. Use terminal + python heredoc for bulk/binary writes.
3. Use `read_file` for reads; avoid full-vault greps when an index exists.

## Rationale
Tool path resolution fumbles the `/c/` drive prefix on this host. Not a
filesystem issue — it’s the editor’s normalization pass. Stay on one style
per file to avoid double-resolution.
