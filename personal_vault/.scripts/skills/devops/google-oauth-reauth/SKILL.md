---
name: google-oauth-reauth
description: Re-auth Google OAuth on Windows/Py3.14 when token 401.
tags: [google, oauth, reauth, calendar, windows, warren, py3.14]
---

# google-oauth-reauth — Google API OAuth re-auth (Windows / Py3.14)

## When to use
- `google_token.json` returns `401 Invalid Credentials` (stale/expired token).
- Need to create/update a Google API resource via API (e.g. Calendar recurring event, Sheets write).
- `google_reauth.py` (uses `flow.run_local_server`) fails with bind/socket `OSError` on Python 3.14.

## HARD RULES
- **Token OAuth only:** `warren-profile/google_token.json`. NEVER hardcode credential. Client secret at `warren-profile/google_client_secret.json`.
- **PKCE:** Google issues PKCE challenges. MUST exchange via `flow.fetch_token(code=...)` (the `InstalledAppFlow` object holds the `code_verifier`). Using raw `OAuth2Session.fetch_token` → `Missing code verifier` error. Do NOT bypass PKCE manually.
- **Auto-catch redirect:** The script must catch `?code=` itself via an `HTTPServer` on `localhost:8080`. Do NOT roundtrip the code through chat.

## THE BROKEN PATH (do NOT use)
`google_reauth.py` uses `flow.run_local_server(port=8080)`. On Python 3.14 / Windows MSYS this raises `OSError` at `server_bind`. Fails every time. Do not rely on it.

## WORKING PATH (manual HTTPServer catch)
Script that:
1. Builds `flow = InstalledAppFlow.from_client_config(...)` with `SCOPES` (e.g. `https://www.googleapis.com/auth/calendar`).
2. Sets `flow.redirect_uri = "http://localhost:8080/"` (MUST match client secret's authorized redirect URI exactly).
3. Prints `auth_url` (so Warren can open manually if auto-open fails).
4. Opens browser via `os.startfile(auth_url)` (Windows). NOT `webbrowser.open` (silent inside Hermes sandbox).
5. Starts a tiny `HTTPServer(("localhost", 8080), Handler)` that catches `?code=` from the redirect, stores it globally.
6. `flow.fetch_token(code=caught_code)` → writes new `google_token.json`.
7. Uses the refreshed token to call the API (e.g. create Calendar event).

See `scripts/oauth_reauth_catch.py` for a working copy-adapt template.

## PITFALLS (from 2026-07-26 session)

### P1 — OAuth `code` expires in ~60 seconds
Chat roundtrip (print URL → Warren opens → pastes code → run) >60s → `invalid_grant: Bad Request`. Every chat attempt failed for this. FIX: script catches code itself via localhost:8080. If Warren runs manually, run on his real terminal (PowerShell/CMD), not Hermes chat.

### P2 — Hermes "Invalid url" when pasting localhost links (HARMLESS)
Warren pastes `http://localhost:8080/?code=...` → Hermes tries to open it → `{"code":"1-11","msg":"Invalid url."}`. **Harmless noise.** The code text is still in the message. Ignore it.

### P3 — client_id typo → `401 invalid_client`
Con once printed URL with hand-typed wrong `client_id` (dropped a digit: `...184-...` vs `...1484-...`) → "OAuth client not found". Always read `client_id` FROM `google_client_secret.json`, never hand-type into a URL.

### P4 — PKCE verifier mismatch
Raw `OAuth2Session.fetch_token(code=...)` → `Missing code verifier`. Always `flow.fetch_token(code=...)`.

### P5 — Reused/expired code still errors
Each `authorization_code` is single-use + short-lived. If exchange failed once, that code is burned — generate FRESH auth URL (new `state`) + new code. Never retry old code.

### P6 — RECURRING re-auth every 2-3 / 7 days = OAuth app in TESTING mode (DOMINANT CAUSE)
If Warren reports "con kêu bố re-auth mỗi 2-3 ngày" — this is NOT a transient failure (P1-P5). It is **Google's 7-day refresh-token expiry for apps in "Testing" publishing status**.
- **Mechanism:** When the Google Cloud OAuth consent screen is in **Testing** (unverified app), Google force-expires ALL refresh tokens after exactly **7 days** — regardless of use. After expiry, every API call returns `invalid_grant` → agent must re-auth.
- **Symptom vs P1-P5:** P1-P5 = one-time exchange failure (code expired in chat, bind error). P6 = token worked for days then died on schedule. If it dies *repeatedly on a cycle*, it's P6, not P1-P5.
- **Verify:** read `google_token.json` `client_id` (ends `@apps.googleusercontent.com` = a Cloud OAuth app). Check its consent-screen status in Google Cloud Console → OAuth consent screen → Publishing status. If "Testing" → P6 confirmed.
- **THE REAL FIX (not re-auth):** Change Publishing status **Testing → Production** (Google Cloud Console → APIs & Services → OAuth consent screen → PUBLISH APP). Production refresh tokens **do not expire on a timer** (only on password change / manual revoke). One publish = re-auth stops forever.
- **SSOT rule (Warren 2026-07-27):** Do NOT "fix" recurring re-auth by adding a parallel auth path (e.g. installing Google MCP server). MCP Google uses the SAME OAuth client_id/secret + same Testing/Production status → it expires on the same 7-day clock. Switching skill→MCP does NOT solve re-auth. Fix the ONE app's publishing status. See `references/google_oauth_7day_testing.md`.

### P7 — Token missing scopes → partial auth, repeated re-prompts for new capability
`google_token.json` may carry only a subset of scopes (observed: **only `calendar`**, missing Gmail/Drive/Sheets/Docs/Contacts). Each new capability then triggers a re-auth for the missing scope.
- **Fix at re-auth time:** grant ALL needed scopes in ONE consent (Calendar + Gmail + Drive + Sheets + Docs + Contacts) so no future capability needs re-promotion. Matches Warren's SSOT preference — one token, all scopes.
- `setup.py --check` reports `AUTHENTICATED (partial): missing N scopes` — treat as a prompt to re-auth with full scope set, not "good enough".

## ROOT-CAUSE DECISION TREE (recurring re-auth)
1. Dies on a **cycle (every ~7 days)** → P6 (Testing mode). Fix = publish to Production. Do NOT re-auth repeatedly, do NOT add MCP.
2. Dies **once, mid-setup** → P1-P5 (transient). Fix = working-path re-auth (localhost:8080 catch).
3. New **capability fails** (e.g. first Drive call) → P7 (missing scope). Fix = re-auth with full scopes.

## references/warren_env_quirks.md
- **Py3.14 bind failure:** `run_local_server` → `OSError` at `server_bind` (HTTPServer on MSYS). Use manual `HTTPServer` + `os.startfile` instead.
- **Hermes sandbox browser:** `webbrowser.open` silent inside Hermes terminal; `os.startfile` works on Windows host.
- **Token location:** `C:/Users/khoans/AppData/Local/hermes/profiles/warren-profile/google_token.json` (gitignored, NEVER commit).
- **Token refresh:** `Credentials` from google-auth; `if cr.expired and cr.refresh_token: cr.refresh(Request())` before API call.

## Related
- `warren-gcal-reminders` (USER-OWNED) — its `google_reauth.py` is now broken on Py3.14. Recommend `hermes curator adopt warren-gcal-reminders` to point at this skill's script.
