# Design Guidelines — Beautiful & Readable Mermaid Diagrams

This guide covers principles for crafting diagrams that are clear, professional, and visually
appealing when rendered with beautiful-mermaid.

## Table of Contents

1. [Sizing and Scope](#1-sizing-and-scope)
2. [Direction and Layout](#2-direction-and-layout)
3. [Node Labels](#3-node-labels)
4. [Shape Semantics](#4-shape-semantics)
5. [Edge Best Practices](#5-edge-best-practices)
6. [Color and Emphasis](#6-color-and-emphasis)
7. [Subgraphs and Grouping](#7-subgraphs-and-grouping)
8. [Spacing and Layout Options](#8-spacing-and-layout-options)
9. [Diagram-Type-Specific Tips](#9-diagram-type-specific-tips)
10. [Anti-Patterns to Avoid](#10-anti-patterns-to-avoid)

---

## 1. Sizing and Scope

**The golden zone is 5–15 nodes.** Diagrams with fewer than 5 nodes are trivial; more than 20
become hard to parse visually. If a system needs more nodes, split into multiple focused diagrams:
an overview diagram + detail diagrams for each subsystem.

**One idea per diagram.** A diagram should answer one question: "How does the deploy pipeline
work?" or "What's the database schema?" Not both at once.

**Progressive disclosure.** Start with a high-level overview (3–7 nodes), then offer drill-down
diagrams for complex subsystems.

---

## 2. Direction and Layout

Choose direction based on the diagram's semantic meaning:

| Direction | Best for |
|---|---|
| `TD` (top-down) | Hierarchies, org charts, decision trees, state machines |
| `LR` (left-right) | Timelines, pipelines, data flows, process sequences |
| `BT` (bottom-up) | Layer stacks (foundation → top), dependency trees |
| `RL` (right-left) | Rarely used — only for RTL reading or reverse flows |

**Rule of thumb:** if the process has a clear "start" and "end", use `LR`. If it has levels or
layers, use `TD`.

---

## 3. Node Labels

- **Be descriptive but concise.** `Auth Service` is better than `AS` or `Authentication and Authorization Service`.
- **Use 2–4 words per label.** Longer labels make nodes too wide and crowd the layout.
- **Use Title Case** for important nodes, sentence case for secondary ones.
- **Avoid redundancy.** Don't put "Node" or "Step" in every label. The shape conveys that.
- **Use consistent naming.** If you call it "User Service" in one place, don't call it "Users API" elsewhere.

---

## 4. Shape Semantics

Use shapes to convey meaning at a glance:

| Shape | Syntax | Semantic Meaning |
|---|---|---|
| Rectangle `[text]` | Default process/action step |
| Rounded `(text)` | General-purpose, softer |
| Diamond `{text}` | Decision / condition |
| Stadium `([text])` | Start/end terminal, external event |
| Circle `((text))` | Critical milestone, checkpoint |
| Cylinder `[(text)]` | Database, data store |
| Subroutine `[[text]]` | Subprocess, function call |
| Hexagon `{{text}}` | Preparation, setup step |
| Double circle `(((text)))` | Highlighted endpoint, emitter |
| Flag `>text]` | Trigger, signal |
| Trapezoid `[/text\]` | Manual operation, input |
| Inv. Trapezoid `[\text/]` | Manual output, display |

**Don't use exotic shapes just because they exist.** Stick to rectangles for most nodes, and use
special shapes only when they add semantic value.

---

## 5. Edge Best Practices

### Always label decision branches

```
%% BAD — ambiguous
B{Check} --> C
B --> D

%% GOOD — clear
B{Check} -->|Pass| C[Continue]
B -->|Fail| D[Retry]
```

### Use edge types meaningfully

| Edge | Meaning |
|---|---|
| `-->` Solid arrow | Primary flow, synchronous call |
| `-.->` Dotted arrow | Optional, async, or alternative path |
| `==>` Thick arrow | Critical path, high-volume flow |
| `---` Solid line | Association, relationship (no direction) |
| `<-->` Bidirectional | Two-way communication, sync |

### Highlight critical paths with linkStyle

```
graph LR
  A --> B --> C --> D
  A --> E --> F
  %% Highlight the happy path
  linkStyle 0,1,2 stroke:#22c55e,stroke-width:3px
  %% De-emphasize the alternate path
  linkStyle 3,4 stroke:#94a3b8,stroke-width:1px
```

### Avoid excessive crossings

If edges cross frequently, consider:
- Changing direction (`TD` → `LR` or vice versa)
- Reordering node declarations (Mermaid assigns rank by declaration order)
- Using subgraphs to group tightly-coupled nodes
- Increasing the `thoroughness` render option (1–7) for better crossing minimization

---

## 6. Color and Emphasis

### Less is more

Use color for **emphasis**, not decoration. A diagram with 8 different colors is harder to read
than one with 2 colors and 1 accent.

### Recommended approach

1. Let the theme handle base colors (nodes, edges, text).
2. Add `classDef` for at most 2–3 semantic classes: success, danger, highlight.
3. Use `linkStyle` to emphasize 1 critical path.

### Accessible color example

```
classDef success fill:#dcfce7,stroke:#16a34a,color:#15803d
classDef danger fill:#fef2f2,stroke:#dc2626,color:#b91c1c
classDef highlight fill:#dbeafe,stroke:#2563eb,color:#1d4ed8
```

### Don't fight the theme

beautiful-mermaid themes are carefully designed with color-mix() derivations. Adding lots of
inline `style` overrides can clash. Trust the theme and only override when semantically necessary.

---

## 7. Subgraphs and Grouping

### When to use subgraphs

- **System boundaries**: Frontend / Backend / Database layers
- **Deployment zones**: Cloud regions, Kubernetes namespaces
- **Logical grouping**: Related services, processing stages
- **Responsibility boundaries**: Teams, ownership domains

### Naming subgraphs

```
%% Give subgraphs both an ID and a display name
subgraph frontend [Client Layer]
  ...
end
```

### Nesting depth

Keep nesting to **2 levels maximum**. Deeper nesting makes diagrams confusing.

```
%% GOOD: 2 levels
subgraph Cloud
  subgraph us-east [US East]
    A --> B
  end
end

%% BAD: 3+ levels
subgraph Cloud
  subgraph Region
    subgraph AZ
      subgraph Pod
        ...
      end
    end
  end
end
```

---

## 8. Spacing and Layout Options

beautiful-mermaid provides render options to control whitespace:

| Option | Default | Purpose |
|---|---|---|
| `nodeSpacing` | `24` | Horizontal space between sibling nodes |
| `layerSpacing` | `40` | Vertical space between layers |
| `componentSpacing` | `24` | Space between disconnected components |
| `padding` | `40` | Canvas padding around the diagram |
| `thoroughness` | `3` | Layout quality (1–7, higher = fewer crossings but slower) |

### When to adjust

- **Dense diagrams (15+ nodes)**: Increase `nodeSpacing` to 32–48 and `layerSpacing` to 56–72.
- **Presentation/export**: Increase `padding` to 60–80 for breathing room.
- **Complex graphs with many crossings**: Increase `thoroughness` to 5–7.
- **Simple linear flows**: Default spacing is fine.

---

## 9. Diagram-Type-Specific Tips

### Flowcharts
- Start with the happy path, then add error/alternate paths
- Put decisions (diamonds) at branching points, never at leaf nodes
- Use subgraphs to separate concerns (CI vs CD, Frontend vs Backend)

### Sequence Diagrams
- Order participants left-to-right by their role in the primary flow
- Use `participant ... as ...` aliases for long names
- Use `actor` for human users, `participant` for systems
- Group related exchanges in `loop`, `alt`, `par` blocks
- Don't exceed 6–8 participants; split into multiple diagrams if needed

### State Diagrams
- Always include `[*]` start and end states
- Label every transition with its trigger event
- Use composite states for complex sub-processes
- Keep the total state count under 12

### Class Diagrams
- Show the most important attributes and methods, not all of them
- Group related classes visually (interfaces together, implementations together)
- Use annotations (`<<interface>>`, `<<abstract>>`, `<<enumeration>>`) consistently

### ER Diagrams
- Include PK/FK/UK annotations on every entity
- Use identifying (solid) relationships for strong dependencies
- Use non-identifying (dashed) for loose coupling
- Put the "parent" entity on the left side of the relationship

### XY Charts
- Always include a `title`
- Use axis labels (`x-axis "Label"`, `y-axis "Label"`) for clarity
- Combine bar + line for actual vs trend comparisons
- Use `horizontal` for categorical data with long labels

---

## 10. Anti-Patterns to Avoid

| Anti-Pattern | Why it's bad | Fix |
|---|---|---|
| Spaghetti edges | Too many crossing lines | Reorder nodes, use subgraphs, increase thoroughness |
| Wall of nodes | 20+ nodes in a flat graph | Split into overview + detail diagrams |
| Cryptic abbreviations | `SVC_A → LB → SVC_B` | Use readable names: `Auth Service → Load Balancer → User Service` |
| Rainbow coloring | Every node a different color | Use theme defaults + 2–3 semantic classes max |
| Unlabeled decisions | Diamond with no `Yes`/`No` labels | Always label decision branches |
| Deep nesting | 3+ subgraph levels | Flatten to max 2 levels |
| Mixed directions | TD subgraph inside LR graph without clear purpose | Pick one primary direction, override only in subgraphs |
| Orphan nodes | Nodes not connected to anything | Remove or connect them |
| Information overload | Class diagrams showing every field and method | Show key members only |
