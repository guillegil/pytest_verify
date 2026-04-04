---
name: beautiful-mermaid
description: >
  Create, render, and export beautiful Mermaid diagrams using the `beautiful-mermaid` library.
  Use this skill whenever the user asks for diagrams, flowcharts, sequence diagrams, state machines,
  class diagrams, ER diagrams, XY charts, architecture diagrams, data flow visualizations, or any
  visual representation that can be expressed as a Mermaid diagram. Also trigger when the user
  mentions "mermaid", "diagram", "flowchart", "sequence diagram", "state diagram", "class diagram",
  "ER diagram", "entity relationship", "chart", "graph TD", "graph LR", or asks to "visualize",
  "map out", "diagram", or "illustrate" a process, system, or architecture. Covers rendering to
  SVG, PNG, PDF, and ASCII, with 16 built-in themes. Even if the user just says "make me a diagram
  of X", use this skill.
---

# Beautiful Mermaid — Diagram Creation Skill

Create professional, beautiful Mermaid diagrams rendered via the `beautiful-mermaid` npm library.
Outputs SVG, PNG, PDF, or ASCII art with 16 built-in themes.

**GitHub**: https://github.com/lukilabs/beautiful-mermaid
**Live samples**: https://agents.craft.do/mermaid

## Quick Start Workflow

1. **Write the Mermaid code** following the design guidelines below
2. **Choose a theme** (or let the agent pick the best one for the context)
3. **Read `scripts/render.mjs`** and execute it to render and export
4. **Present the output file(s)** to the user

## Step-by-Step

### Step 1 — Write the Mermaid Diagram

Read `references/diagram-types.md` for comprehensive syntax for all 6 supported diagram types:
flowcharts, state diagrams, sequence diagrams, class diagrams, ER diagrams, and XY charts.

Read `references/design-guidelines.md` for principles on making diagrams beautiful and readable.

### Step 2 — Choose a Theme

Read `references/themes.md` for the full list of 16 built-in themes plus instructions for custom themes.

**Theme selection heuristic** — when the user doesn't specify a theme:

| Context | Recommended Theme |
|---|---|
| General / professional | `zinc-light` (light) or `zinc-dark` (dark) |
| Developer / technical docs | `github-light` or `github-dark` |
| Trendy / modern UI | `tokyo-night` or `catppuccin-mocha` |
| Warm / academic | `solarized-light` or `solarized-dark` |
| Scandinavian / muted | `nord` or `nord-light` |
| Fun / vibrant | `dracula` or `one-dark` |
| Presentation slides (light bg) | `catppuccin-latte` or `tokyo-night-light` |
| Terminal / CLI output | Use ASCII rendering instead |

If unclear, default to `zinc-light` for light contexts, `tokyo-night` for dark.

### Step 3 — Render and Export

Read and execute the rendering script:

```bash
cat /path/to/skill/scripts/render.mjs   # read the script first
```

The render script supports these output formats:

| Format | How |
|---|---|
| **SVG** | Default output. Direct `renderMermaidSVG()` result. |
| **PNG** | Uses `sharp` to convert SVG → PNG at configurable DPI. |
| **PDF** | Uses `puppeteer` to wrap SVG in HTML and print to PDF. |
| **ASCII** | Uses `renderMermaidASCII()` for terminal output. |

**Basic usage:**

```bash
# Install dependencies
npm install beautiful-mermaid sharp

# Render to SVG (default)
node render.mjs --input diagram.mmd --output diagram.svg --theme tokyo-night

# Render to PNG
node render.mjs --input diagram.mmd --output diagram.png --theme github-light --scale 2

# Render to ASCII
node render.mjs --input diagram.mmd --output diagram.txt --format ascii

# Render to PDF
node render.mjs --input diagram.mmd --output diagram.pdf --theme zinc-light
```

### Step 4 — Present Output

Copy the rendered file to `/mnt/user-data/outputs/` and use `present_files` to share with the user.

---

## Design Principles (Summary)

These are expanded in `references/design-guidelines.md`. The key rules:

1. **Keep it simple** — 5–15 nodes is ideal. Split larger diagrams.
2. **Use descriptive labels** — `Auth Service` not `AS`. Short but meaningful.
3. **Choose direction wisely** — `TD` for hierarchies, `LR` for flows/timelines.
4. **Group with subgraphs** — organize related nodes into named containers.
5. **Use shapes semantically** — diamonds for decisions, cylinders for databases, stadiums for start/end.
6. **Color with purpose** — use `classDef` and `style` for emphasis, not decoration. Use `linkStyle` to highlight critical paths.
7. **Whitespace matters** — use spacing options (`nodeSpacing`, `layerSpacing`) for breathing room.
8. **Label edges** — arrows without labels are ambiguous. Always label decision branches.

---

## Reference Files

| File | When to read |
|---|---|
| `references/themes.md` | When choosing or customizing a theme |
| `references/diagram-types.md` | When writing diagram syntax for any of the 6 types |
| `references/design-guidelines.md` | When crafting a diagram for quality/readability |
| `scripts/render.mjs` | When rendering and exporting to any format |

---

## Common Patterns

### Inline rendering (quick, no file)

For a quick ASCII preview you can show in-conversation without creating a file:

```javascript
import { renderMermaidASCII } from 'beautiful-mermaid'
console.log(renderMermaidASCII(`graph LR; A --> B --> C`))
```

### Multiple diagrams in one session

Write each diagram to a separate `.mmd` file, render each one, then present them all.

### Iterating on a diagram

Save the Mermaid source as a `.mmd` file alongside the rendered output so the user can iterate.
Always save the `.mmd` source file to `/mnt/user-data/outputs/` alongside the rendered output.
