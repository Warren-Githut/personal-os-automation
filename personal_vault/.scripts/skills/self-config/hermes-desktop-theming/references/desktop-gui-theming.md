# Desktop GUI theming — Hermes Desktop (Electron)

> Companion to hermes-desktop-theming SKILL.md. Captured 2026-07-23 while
> recoloring chat text to banana green for Warren (stock-profile). The bundled
> `hermes-themes` skill was consulted but it only covers `skins/*.yaml` (CLI/TUI),
> which does NOT theme the desktop GUI — hence this dedicated skill.

## Why skins/*.yaml didn't work

The desktop app is a pre-built bundle. At build time `web/src/themes/presets.ts`
produces `DashboardTheme` objects that the renderer applies as CSS custom
properties on `:root` (e.g. `--dt-foreground: var(--ui-text-primary)`,
`--color-foreground: var(--dt-foreground)`). The runtime `skins/*.yaml` system
(`skin_engine.py`) only drives the CLI/TUI/terminal surfaces. Editing a skin
YAML changes terminal colors; the desktop GUI ignores it. Symptom: user says
"text still white" after you set `display.skin`.

## Path layout (Warren machine, stock-profile)

- Source themes: `C:/Users/khoans/AppData/Local/hermes/hermes-agent/web/src/themes/`
  - `presets.ts` — built-in `DashboardTheme` objects (foreground/background/warmGlow)
  - `context.tsx` — `applyTheme()` writes `--dt-*` vars; `useTheme()` hook
  - `types.ts` — `DashboardTheme` shape
- Built app: `C:/Users/khoans/AppData/Local/hermes/hermes-agent/apps/desktop/dist/`
  - `index.html` — points to `./assets/index-<hash>.css` (hash varies per build)
  - `assets/index-<hash>.css` — the only file you edit for a CSS override
- `skins/` (CLI/TUI only): `C:/Users/khoans/AppData/Local/hermes/profiles/stock-profile/skins/`

## Chat text selectors (shipped build)

Grep of the built CSS confirmed the chat content wrapper is `.aui-md`, NOT the
old `.prose` from `Markdown.tsx`. Correct targets:

| Element | Selector |
|---------|----------|
| Assistant paragraph/body | `[data-slot=aui_assistant-message-content] .aui-md` |
| Assistant headings | same `:where(h1,h2,h3,h4)` |
| Assistant links | same `:where(a)` |
| User message text | `[data-slot=aui_user-inline-text]` |

`.prose{color:var(--tw-prose-body)}` exists in the CSS but is NOT used by the
shipped chat renderer — do not target it.

## Working override (banana green, 2026-07-23)

Append to `assets/index-<hash>.css` (after backing up):

```css
/* CHAT TEXT OVERRIDE — banana green per Warren 2026-07-23 */
[data-slot=aui_assistant-message-content] .aui-md,
[data-slot=aui_assistant-message-content] .aui-md :where(p,li,blockquote,td,th,strong,b){color:#7CFC00 !important}
[data-slot=aui_assistant-message-content] .aui-md :where(h1,h2,h3,h4){color:#a8ff60 !important}
[data-slot=aui_assistant-message-content] .aui-md :where(a){color:#a8ff60 !important}
[data-slot=aui_user-inline-text]{color:#7CFC00 !important}
```

Then restart the app. To revert: delete the appended block (or restore `.bak`).

## Source-edit path (full theme, heavy)

Edit `web/src/themes/presets.ts`, change `foreground.hex` (and `background.hex`,
`warmGlow`, optional `colorOverrides: {success,warning,destructive}`). Rebuild
`web/` and repackage the desktop app. Keep `BUILTIN_THEMES` keys in sync with
`_BUILTIN_DASHBOARD_THEMES` in `hermes_cli/web_server.py`. Not needed for a
single-color chat tweak.
