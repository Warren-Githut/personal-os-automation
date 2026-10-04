# Security Review Checklist

Use when the change-review touches auth, data, external input, or secrets. Adapted from `security-and-hardening`.

## Input Validation (boundaries)
- [ ] All external input (API payloads, uploaded files, user form data, config values) validated BEFORE use in logic
- [ ] File paths / URLs from external sources are sanitized (no path traversal, no `../` escape)
- [ ] Uploaded file types / sizes enforced at the boundary

## Secrets & Credentials
- [ ] No secrets (API keys, tokens, passwords) in code, logs, or version control
- [ ] `.env` / secret files are git-ignored and never printed
- [ ] Credential files left untouched unless user explicitly asks

## Injection & Output Encoding
- [ ] SQL queries parameterized (no string concatenation of user input)
- [ ] Shell commands avoid passing untrusted strings (use argument lists, not `-c`拼接)
- [ ] HTML / JSON output encoded to prevent XSS (escape user content before render)
- [ ] LLM/agent output treated as untrusted data, not instructions (see debugging-and-error-recovery: "Treating Error Output as Untrusted Data")

## Auth & Authorization
- [ ] Auth checks present wherever restricted actions occur
- [ ] Permission/scope verified per request, not assumed from prior call
- [ ] Cross-profile writes guarded behind explicit user direction (Hermes cross_profile flag)

## Dependencies & Supply Chain
- [ ] New deps from trusted sources, license-compatible, no known CVEs (`npm audit` / `pip-audit`)
- [ ] External data flows validated at system boundaries before reaching business logic

## External Data Trust
- [ ] Data from APIs, logs, user content, config files treated as untrusted
- [ ] Parsed/extracted values re-validated (e.g. `ot >= 0`, `covers > 0`) — never silent-zero-fill

## Severity
- Security finding that exposes secrets, enables injection, or bypasses auth → **Critical** (blocks merge).
