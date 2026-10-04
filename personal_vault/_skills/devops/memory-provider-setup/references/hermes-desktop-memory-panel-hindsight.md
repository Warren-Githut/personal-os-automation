# Hermes Desktop Memory Provider Panel — Hindsight (verified source)

Source verified 2026-07-19 on Warren's machine (Hermes v0.18.2, upstream 36f2a966, local e598cef8).
Companion to the "Hermes Desktop Memory Provider Panel" section in SKILL.md.

## File: hermes_cli/memory_providers.py

Declarative schema. Each provider declares configurable fields; a single generic
desktop renderer + generic `GET/PUT /api/memory/providers/{name}/config` endpoint
drive the whole UI. Adding mem0/honcho = pure declaration, zero bespoke UI.

Only HINDSIGHT declares fields (verbatim from source):

```python
HINDSIGHT = MemoryProvider(
    name="hindsight",
    label="Hindsight",
    fields=(
        ProviderField(key="mode", label="Mode", kind=KIND_SELECT, default="cloud",
            options=(
                ProviderFieldOption("cloud","Cloud","Hindsight Cloud API (lightweight, just needs an API key)"),
                ProviderFieldOption("local_external","Local External","Connect to an existing Hindsight instance"),
            )),
        ProviderField(key="api_key", label="API key", kind=KIND_SECRET, env_key="HINDSIGHT_API_KEY",
            description="Used to authenticate with the Hindsight API."),
        ProviderField(key="api_url", label="API URL", kind=KIND_TEXT, default="https://api.hindsight.vectorize.io",
            aliases=("apiUrl",), env_fallbacks=("HINDSIGHT_API_URL",)),
        ProviderField(key="bank_id", label="Bank ID", kind=KIND_TEXT, default="hermes", aliases=("bankId",)),
        ProviderField(key="recall_budget", label="Recall budget", kind=KIND_SELECT, default="mid", aliases=("budget",),
            options=(ProviderFieldOption("low","low"), ProviderFieldOption("mid","mid"), ProviderFieldOption("high","high"))),
    ),
)

# Registry — providers WITHOUT an entry render no config panel:
MEMORY_PROVIDERS: dict[str, MemoryProvider] = { HINDSIGHT.name: HINDSIGHT }
# builtin / mem0 / honcho have NO entry -> desktop shows empty settings area
```

## Commits confirming the panel ships in v0.18.2
- `822c8226d` refactor(desktop): group memory provider config UI under settings/memory
- `03d9a95a7` fix(desktop): show Hindsight memory provider (#37546)
- `5e3e89cc0` feat(hindsight): configurable embedded daemon health grace timeout (#50341)
- `7bc6f1806` fix(hindsight): skip local_embedded daemon when running as root

## External authoritative context (web, 2026-07)
- Hindsight = native memory provider in Hermes (Vectorize AI). Cloud mode = free tier, paste key. Local External = self-host.
- Desktop dropdown lists several providers, but Hindsight is the ONLY one with a real config panel; others render empty.
- API key stored as secret (write-only, never read back into form); rest as profile config. No restart needed on save.

## Warren decision (2026-07-19)
Keep mem0/FAISS local. Do NOT switch to Hindsight:
- cloud = L'Usine ops data leaves machine to a 3rd-party cloud
- local_external = self-host Docker → violates laptop-only / min-RAM / 24-7 constraints
Panel exists for onboarding new users / cloud-sync seekers, not for his optimized local stack.
Cross-device alternative if ever wanted: sync the `mem0_faiss/` folder via OneDrive — NOT Hindsight.
