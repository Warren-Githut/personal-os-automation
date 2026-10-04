---
name: hermes-desktop-theming
description: "Theme the Hermes Desktop (Electron) GUI surface. The desktop app uses a SEPARATE theme system (DashboardTheme) from the CLI/TUI skins/*.yaml — this skill covers the GUI, which the bundled hermes-themes skill does NOT."
version: 1.0.0
platforms: [windows, macos, linux]
tags: [theme, skin, desktop, gui, electron, appearance, self-config]
metadata:
  hermes:
    tags: [theme, skin, desktop, gui, electron, appearance, self-config]
    related_skills: [hermes-themes]
---

# Hermes Desktop Theming (Electron GUI)

Author colors for the **Hermes Desktop app** specifically. This skill exists
because the bundled `hermes-themes` skill targets `skins/*.yaml`, which themes
ONLY the CLI/TUI/terminal — **it does NOT touch the desktop GUI.** If you edit a
skin YAML and the user says "the app text is still white", you edited the wrong
system. Use this skill.

## Two independent theme systems

| Surface | Theme system | Source | Activate |
|---------|--------------|--------|----------|
| CLI / TUI / terminal | `skins/*.yaml` (`skin_engine.py`) | `~/.hermes/skins/<name>.yaml` | `hermes config set display.skin <name>` |
| **Desktop GUI** (Electron) | `DashboardTheme` (web/src/themes) compiled to CSS vars | `apps/desktop/dist/assets/index-*.css` | App header ThemeSwitcher, OR CSS override (below) |

The desktop app is a **pre-built bundle**. At build time `web/src/themes/presets.ts`
produces `DashboardTheme` objects applied as CSS custom properties on `:root`
(`--dt-foreground`, `--ui-text-primary`, `--dt-background`, …). The runtime
`skins/*.yaml` system is ignored by this surface.

## How to change the desktop GUI look

### A. Built-in / user DashboardTheme (no rebuild)
Built-ins: `default` (Hermes Teal), `midnight`, `ember`, `mono`, `cyberpunk`,
`rose`, `nous-blue`, `default-large`. Switch from the palette icon in the app
header (ThemeSwitcher). User themes also load from
`~/.hermes/dashboard-themes/*.yaml` (API-shaped `DashboardTheme` defs) and appear
in the ThemeSwitcher automatically.

### B. CSS override — surgical, no rebuild, fully reversible (preferred)
1. Find the built CSS: read `apps/desktop/dist/index.html`, take the
   `<link rel="stylesheet" href="./assets/index-<hash>.css">` path.
   Default: `apps/desktop/dist/assets/index-<hash>.css`.
2. Backup: `cp index-<hash>.css index-<hash>.css.bak`
3. Append override (see recipe below).
4. Restart the app (close fully, reopen) to reload CSS.

Chat text selectors (observed in the shipped build — the wrapper is `.aui-md`,
NOT the old `.prose` from `Markdown.tsx`):
- Assistant: `[data-slot=aui_assistant-message-content] .aui-md`
- User: `[data-slot=aui_user-inline-text]`

Working example (banana green, Warren 2026-07-23):
```css
/* CHAT TEXT OVERRIDE */
[data-slot=aui_assistant-message-content] .aui-md,
[data-slot=aui_assistant-message-content] .aui-md :where(p,li,blockquote,td,th,strong,b){color:#7CFC00 !important}
[data-slot=aui_assistant-message-content] .aui-md :where(h1,h2,h3,h4){color:#a8ff60 !important}
[data-slot=aui_assistant-message-content] .aui-md :where(a){color:#a8ff60 !important}
[data-slot=aui_user-inline-text]{color:#7CFC00 !important}
```

### C. Full custom theme via source (heavy)
Edit `web/src/themes/presets.ts` (`palette.foreground.hex`, `palette.background.hex`,
`palette.warmGlow`, optional `colorOverrides: {success,warning,destructive}`) then
rebuild `web/` and repackage the desktop app. Keep `BUILTIN_THEMES` keys in sync
with `_BUILTIN_DASHBOARD_THEMES` in `hermes_cli/web_server.py`. Only if A+B
cannot achieve the look.

## Pitfalls

- **`skins/*.yaml` does NOT theme the desktop GUI.** #1 mistake. The Electron app
  reads `DashboardTheme` (built from `web/src/themes/presets.ts`), not skin YAML.
- **The built chat wrapper is `.aui-md`, not `.prose`.** The SHIPPED app renders
  assistant content inside `[data-slot=aui_assistant-message-content] .aui-md`.
  A `.prose{color:...}` override does nothing in the desktop build. Target
  `aui-md` (and `aui_user-inline-text` for the user's own messages).
- **Resolve real home before editing paths.** When a profile is active, use
  `$HERMES_HOME` (falls back to `~/.hermes`). The desktop dist lives under
  `<hermes-agent>/apps/desktop/dist/`, NOT under the profile dir.
- **Don't hand-edit the source `presets.ts` for a one-color tweak.** Use the CSS
  override (B) — no rebuild, reversible, survives app updates until the bundle is
  replaced.

## References

- `references/desktop-gui-theming.md` — exact machine paths, full selector table,
  and the verified banana-green override transcript.
