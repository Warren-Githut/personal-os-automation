# Google OAuth 7-Day Testing Expiry — Knowledge Bank

Condensed from web research (2026-07-27 session) on why Warren's `google_token.json` kept demanding re-auth.

## The rule (Google official)
- OAuth consent screen in **Testing** status → **all refresh tokens expire after exactly 7 days**, regardless of use.
- After expiry: API calls return `invalid_grant` / `401 Invalid Credentials` → agent must re-auth.
- This is by design — Google protects users from unverified apps.

## The fix
- Google Cloud Console → APIs & Services → **OAuth consent screen** → change Publishing status **Testing → Production** (button "PUBLISH APP").
- Production refresh tokens do NOT expire on a timer. They only die if Warren:
  - changes Google account password,
  - manually revokes the app (Security → Third-party apps),
  - Google suspends the app (rare).
- One publish = re-auth prompts stop permanently.

## MCP Google does NOT bypass this
- Google's official Workspace MCP servers (`*.mcp.googleapis.com/mcp/v1`) require their OWN OAuth `clientId` + `clientSecret` in the MCP client config (`hermes mcp add ... --url ... --oauth clientId=... clientSecret=...`).
- That OAuth client is ALSO a Google Cloud app. If it's in Testing mode → same 7-day expiry.
- Therefore: installing Google MCP to "fix re-auth" is futile unless that app is also published to Production. The correct, minimal fix is to publish the EXISTING `google_token.json` app — keep SSOT, one auth path.

## Verify current token state (Windows / warren-profile)
```bash
# read scopes actually granted
python -c "import json;d=json.load(open(r'C:/Users/khoans/AppData/Local/hermes/profiles/warren-profile/google_token.json'));print(d.get('scopes'))"
# check auth + missing scopes
GSETUP="python C:/Users/khoans/AppData/Local/hermes/profiles/warren-profile/skills/productivity/google-workspace/scripts/setup.py"
$GSETUP --check
```
- Observed 2026-07-27: token had ONLY `calendar` scope; `--check` reported `AUTHENTICATED (partial): missing 7 scopes`.

## Sources
- developers.google.com/identity/protocols/oauth2#expiration (7-day testing limit)
- unipile.com/google-oauth-refresh-token/ (7-day testing trap, fixes)
- developers.google.com/workspace/guides/configure-mcp-servers (official Workspace MCP, requires OAuth clientId/secret)
