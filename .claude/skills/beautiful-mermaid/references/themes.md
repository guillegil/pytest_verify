# Themes Reference — beautiful-mermaid

beautiful-mermaid ships with **16 built-in themes** (15 from the library + the default). Every theme
is built on a two-color foundation: **background** (`bg`) and **foreground** (`fg`). Optional
"enrichment" colors override specific derivations for richer palettes.

## Table of Contents

1. [Theme List](#theme-list)
2. [Theme Details](#theme-details)
3. [Mono Mode (Two-Color)](#mono-mode)
4. [Enriched Mode](#enriched-mode)
5. [Custom Themes](#custom-themes)
6. [CSS Variable Live Switching](#css-variable-live-switching)
7. [Shiki Theme Compatibility](#shiki-compatibility)

---

## Theme List

| # | Theme Key | Type | Background | Foreground | Accent | Best For |
|---|---|---|---|---|---|---|
| 1 | `default` | Light | `#FFFFFF` | `#27272A` | Derived | General use |
| 2 | `zinc-light` | Light | `#FFFFFF` | `#27272A` | Derived | Professional, clean |
| 3 | `zinc-dark` | Dark | `#18181B` | `#A1A1AA` | Derived | Professional, dark mode |
| 4 | `tokyo-night` | Dark | `#1a1b26` | `#a9b1d6` | `#7aa2f7` | Developer, modern |
| 5 | `tokyo-night-storm` | Dark | `#24283b` | `#a9b1d6` | `#7aa2f7` | Developer, muted |
| 6 | `tokyo-night-light` | Light | `#d5d6db` | `#343b58` | `#34548a` | Light dev theme |
| 7 | `catppuccin-mocha` | Dark | `#1e1e2e` | `#cdd6f4` | `#cba6f7` | Trendy, warm dark |
| 8 | `catppuccin-latte` | Light | `#eff1f5` | `#4c4f69` | `#8839ef` | Presentations, warm |
| 9 | `nord` | Dark | `#2e3440` | `#d8dee9` | `#88c0d0` | Scandinavian, muted |
| 10 | `nord-light` | Light | `#eceff4` | `#2e3440` | `#5e81ac` | Scandinavian, light |
| 11 | `dracula` | Dark | `#282a36` | `#f8f8f2` | `#bd93f9` | Vibrant, popular |
| 12 | `github-light` | Light | `#ffffff` | `#1f2328` | `#0969da` | GitHub-style, docs |
| 13 | `github-dark` | Dark | `#0d1117` | `#e6edf3` | `#4493f8` | GitHub dark mode |
| 14 | `solarized-light` | Light | `#fdf6e3` | `#657b83` | `#268bd2` | Academic, warm |
| 15 | `solarized-dark` | Dark | `#002b36` | `#839496` | `#268bd2` | Classic dark |
| 16 | `one-dark` | Dark | `#282c34` | `#abb2bf` | `#c678dd` | Atom-style, cozy |

---

## Theme Details

### Using a built-in theme

```javascript
import { renderMermaidSVG, THEMES } from 'beautiful-mermaid'

// Use any built-in theme by key
const svg = renderMermaidSVG(diagram, THEMES['tokyo-night'])
```

### Theme color roles

Every theme derives up to 10 visual roles from the base colors:

| Role | CSS Variable | Purpose | Derivation (Mono Mode) |
|---|---|---|---|
| Text | `--fg` | Primary labels | `fg` at 100% |
| Secondary text | `--fg-secondary` | Subtitle, metadata | `fg` at 60% into `bg` |
| Edge labels | `--fg-edge-label` | Arrow text | `fg` at 40% into `bg` |
| Faint text | `--fg-faint` | Watermarks | `fg` at 25% into `bg` |
| Connectors | `--line` | Edge lines | `fg` at 50% into `bg` |
| Arrow heads | `--accent` | Arrowheads, highlights | `fg` at 85% into `bg` |
| Node fill | `--surface` | Node background | `fg` at 3% into `bg` |
| Group header | `--surface-header` | Subgraph header | `fg` at 5% into `bg` |
| Inner strokes | `--border-inner` | Dividers | `fg` at 12% into `bg` |
| Node stroke | `--border` | Node outline | `fg` at 20% into `bg` |

---

## Mono Mode

Provide just `bg` and `fg` to get a coherent, monochromatic diagram:

```javascript
const svg = renderMermaidSVG(diagram, {
  bg: '#1a1b26',
  fg: '#a9b1d6',
})
```

All 10 visual roles are automatically derived using `color-mix()`. This produces
professional, consistent results with minimal effort.

---

## Enriched Mode

Override specific roles for richer color palettes:

```javascript
const svg = renderMermaidSVG(diagram, {
  bg: '#1a1b26',
  fg: '#a9b1d6',
  // Optional enrichments:
  line: '#3d59a1',     // Edge/connector color
  accent: '#7aa2f7',   // Arrow heads, highlights
  muted: '#565f89',    // Secondary text, labels
  surface: '#292e42',  // Node fill tint
  border: '#3d59a1',   // Node stroke
})
```

Any enrichment you omit falls back to its `color-mix()` derivation.

---

## Custom Themes

### Minimal custom theme (just 2 colors)

```javascript
const myTheme = {
  bg: '#0f0f0f',
  fg: '#e0e0e0',
}
```

### Rich custom theme

```javascript
const brandTheme = {
  bg: '#0a1628',
  fg: '#e2e8f0',
  accent: '#3b82f6',
  muted: '#64748b',
  surface: '#1e293b',
  border: '#334155',
  line: '#475569',
}
```

### Theme for presentations (light, high contrast)

```javascript
const presentationTheme = {
  bg: '#ffffff',
  fg: '#111827',
  accent: '#2563eb',
  surface: '#f0f9ff',
  border: '#bfdbfe',
}
```

---

## CSS Variable Live Switching

All colors are CSS custom properties on the `<svg>` element. Switch themes instantly:

```javascript
// Get the SVG element
const svgEl = document.querySelector('svg')

// Switch to a new theme without re-rendering
svgEl.style.setProperty('--bg', '#282a36')
svgEl.style.setProperty('--fg', '#f8f8f2')
```

For React apps, pass CSS variable references instead of hex values:

```javascript
const svg = renderMermaidSVG(diagram, {
  bg: 'var(--background)',
  fg: 'var(--foreground)',
  accent: 'var(--accent)',
  transparent: true,
})
```

---

## Shiki Compatibility

Use any VS Code theme with the `fromShikiTheme()` function:

```javascript
import { getSingletonHighlighter } from 'shiki'
import { renderMermaidSVG, fromShikiTheme } from 'beautiful-mermaid'

const highlighter = await getSingletonHighlighter({
  themes: ['vitesse-dark', 'rose-pine', 'material-theme-darker']
})

const colors = fromShikiTheme(highlighter.getTheme('vitesse-dark'))
const svg = renderMermaidSVG(diagram, colors)
```

The mapping from editor colors to diagram roles:

| Editor Color | Diagram Role |
|---|---|
| `editor.background` | `bg` |
| `editor.foreground` | `fg` |
| `editorLineNumber.foreground` | `line` |
| `focusBorder` / keyword token | `accent` |
| comment token | `muted` |
| `editor.selectionBackground` | `surface` |
| `editorWidget.border` | `border` |
