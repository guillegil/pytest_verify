# Diagram Types Reference — beautiful-mermaid

beautiful-mermaid supports **6 diagram types**: Flowcharts, State Diagrams, Sequence Diagrams,
Class Diagrams, ER Diagrams, and XY Charts. This file covers syntax, shapes, and examples for each.

## Table of Contents

1. [Flowcharts](#1-flowcharts)
2. [State Diagrams](#2-state-diagrams)
3. [Sequence Diagrams](#3-sequence-diagrams)
4. [Class Diagrams](#4-class-diagrams)
5. [ER Diagrams](#5-er-diagrams)
6. [XY Charts](#6-xy-charts)
7. [Styling Reference](#7-styling-reference)

---

## 1. Flowcharts

Declare with `graph` or `flowchart` followed by direction: `TD` (top-down), `LR` (left-right),
`BT` (bottom-top), `RL` (right-left).

### Node shapes

```
A[Rectangle]          %% Default box
B(Rounded)            %% Rounded corners
C{Diamond}            %% Decision
D([Stadium])          %% Pill shape — start/end
E((Circle))           %% Circle
F[[Subroutine]]       %% Double-bordered box
G(((Double Circle)))  %% Emphasized circle
H{{Hexagon}}          %% Preparation step
I[(Database)]         %% Cylinder
J>Flag]               %% Asymmetric
K[/Trapezoid\]        %% Wider bottom
L[\Inverse Trap/]     %% Wider top
```

### Edge styles

```
A --> B               %% Solid arrow
A -.-> B              %% Dotted arrow
A ==> B               %% Thick arrow
A --- B               %% Solid line (no arrow)
A -.- B               %% Dotted line (no arrow)
A === B               %% Thick line (no arrow)
A <--> B              %% Bidirectional solid
A <-.-> B             %% Bidirectional dotted
A <==> B              %% Bidirectional thick
```

### Edge labels

```
A -->|label| B        %% Label with pipe syntax
A -- label --> B      %% Label embedded in link
```

### Subgraphs

```
graph TD
  subgraph Frontend
    A[React] --> B[Redux]
  end
  subgraph Backend
    C[API] --> D[(DB)]
  end
  B --> C
```

### Nested subgraphs with direction override

```
graph TD
  subgraph pipeline [Processing Pipeline]
    direction LR
    A[Input] --> B[Parse] --> C[Transform] --> D[Output]
  end
  E[Source] --> A
  D --> F[Sink]
```

### Parallel links

```
A & B --> C           %% Both A and B connect to C
C --> D & E           %% C connects to both D and E
```

### classDef and style

```
graph TD
  A[OK]:::success --> B[Error]:::danger
  classDef success fill:#10b981,stroke:#059669,color:#fff
  classDef danger fill:#ef4444,stroke:#dc2626,color:#fff
```

### linkStyle

Style edges by their 0-based index order:

```
graph TD
  A --> B
  B --> C
  B --> D
  linkStyle 0 stroke:#22c55e,stroke-width:2px
  linkStyle 1 stroke:#3b82f6,stroke-width:2px
  linkStyle 2 stroke:#ef4444,stroke-width:3px
  linkStyle default stroke:#6b7280,stroke-width:1px
```

You can also style multiple links at once: `linkStyle 0,1,2 stroke:#22c55e`

### Full example: CI/CD Pipeline

```
graph TD
  subgraph ci [CI Pipeline]
    A[Push Code] --> B{Tests Pass?}
    B -->|Yes| C[Build Image]
    B -->|No| D[Fix & Retry]
    D -.-> A
  end
  C --> E([Deploy Staging])
  E --> F{QA Approved?}
  F -->|Yes| G((Production))
  F -->|No| D
```

### Full example: System Architecture

```
graph LR
  subgraph clients [Client Layer]
    A([Web App]) --> B[API Gateway]
    C([Mobile App]) --> B
  end
  subgraph services [Service Layer]
    B --> D[Auth Service]
    B --> E[User Service]
    B --> F[Order Service]
  end
  subgraph data [Data Layer]
    D --> G[(Auth DB)]
    E --> H[(User DB)]
    F --> I[(Order DB)]
    F --> J([Message Queue])
  end
```

---

## 2. State Diagrams

Declare with `stateDiagram-v2`.

### Basic syntax

```
stateDiagram-v2
  [*] --> Idle
  Idle --> Active : start
  Active --> Idle : cancel
  Active --> Done : complete
  Done --> [*]
```

- `[*]` is the start/end pseudostate
- `State1 --> State2 : event` defines transitions with labels

### Composite (nested) states

```
stateDiagram-v2
  [*] --> Idle
  Idle --> Processing : submit
  state Processing {
    parse --> validate
    validate --> execute
  }
  Processing --> Complete : done
  Processing --> Error : fail
  Error --> Idle : retry
  Complete --> [*]
```

### Full example: Connection Lifecycle

```
stateDiagram-v2
  [*] --> Closed
  Closed --> Connecting : connect
  Connecting --> Connected : success
  Connecting --> Closed : timeout
  Connected --> Disconnecting : close
  Connected --> Reconnecting : error
  Reconnecting --> Connected : success
  Reconnecting --> Closed : max_retries
  Disconnecting --> Closed : done
  Closed --> [*]
```

---

## 3. Sequence Diagrams

Declare with `sequenceDiagram`.

### Participants and actors

```
sequenceDiagram
  participant A as Alice          %% Box participant
  actor U as User                 %% Stick figure
  participant S as Server
```

### Message types

```
A->>B: Solid arrow (sync call)
B-->>A: Dashed arrow (return)
A-)B: Open arrow (async)
B--)A: Open dashed arrow
```

### Activation boxes

```
C->>+S: Request       %% + activates S
S-->>-C: Response      %% - deactivates S
```

### Blocks

```
%% Loop
loop Every 30s
  C->>S: Heartbeat
  S-->>C: Ack
end

%% Alt/Else (conditional)
alt Valid
  S-->>C: 200 OK
else Invalid
  S-->>C: 401
end

%% Opt (optional)
opt Cache miss
  A->>DB: Query
end

%% Par (parallel)
par Fetch user
  G->>U: Get profile
and Fetch orders
  G->>O: Get orders
end

%% Critical section
critical Transaction
  A->>DB: UPDATE
  A->>DB: INSERT
end
```

### Notes

```
Note left of A: Prepares
Note right of B: Thinks
Note over A,B: Conversation done
```

### Full example: OAuth 2.0

```
sequenceDiagram
  actor U as User
  participant App as Client App
  participant Auth as Auth Server
  participant API as Resource API
  U->>App: Click Login
  App->>Auth: Authorization request
  Auth->>U: Login page
  U->>Auth: Credentials
  Auth-->>App: Authorization code
  App->>Auth: Exchange code for token
  Auth-->>App: Access token
  App->>API: Request + token
  API-->>App: Protected resource
  App-->>U: Display data
```

---

## 4. Class Diagrams

Declare with `classDiagram`.

### Class definition

```
classDiagram
  class Animal {
    +String name
    -int age
    #bool alive
    ~String internal
    +eat() void
    -digest() void
  }
```

Visibility: `+` public, `-` private, `#` protected, `~` package

### Annotations

```
class Serializable {
  <<interface>>
  +serialize() String
}

class Shape {
  <<abstract>>
  +area() double
}

class Status {
  <<enumeration>>
  ACTIVE
  INACTIVE
}
```

### Relationships

```
A <|-- B       %% Inheritance (hollow triangle)
C *-- D        %% Composition (filled diamond)
E o-- F        %% Aggregation (hollow diamond)
G --> H        %% Association (arrow)
I ..> J        %% Dependency (dashed arrow)
K ..|> L       %% Realization (dashed triangle)
```

### Labels and cardinality

```
Teacher --> Course : teaches
Student "1..*" --> "0..*" Course : enrolled in
```

### Full example: MVC Pattern

```
classDiagram
  class Model {
    -data Map
    +getData() Map
    +setData(key, val) void
    +notify() void
  }
  class View {
    -model Model
    +render() void
    +update() void
  }
  class Controller {
    -model Model
    -view View
    +handleInput(event) void
  }
  Controller --> Model : updates
  Controller --> View : refreshes
  View --> Model : reads
  Model ..> View : notifies
```

---

## 5. ER Diagrams

Declare with `erDiagram`.

### Entity with attributes

```
erDiagram
  CUSTOMER {
    int id PK
    string name
    string email UK
    date created_at
  }
```

Key types: `PK` (primary), `FK` (foreign), `UK` (unique)

### Cardinality notation

```
||--||   Exactly one to exactly one
||--o{   Exactly one to zero-or-many
|o--|{   Zero-or-one to one-or-many
}|--o{   One-or-more to zero-or-many
```

### Relationship types

```
A ||--|{ B : contains     %% Solid line = identifying
A ||..o{ B : generates    %% Dashed line = non-identifying
```

### Full example: E-Commerce Schema

```
erDiagram
  CUSTOMER {
    int id PK
    string name
    string email UK
  }
  ORDER {
    int id PK
    date created
    int customer_id FK
  }
  PRODUCT {
    int id PK
    string name
    float price
  }
  LINE_ITEM {
    int id PK
    int order_id FK
    int product_id FK
    int quantity
  }
  CUSTOMER ||--o{ ORDER : places
  ORDER ||--|{ LINE_ITEM : contains
  PRODUCT ||--o{ LINE_ITEM : includes
```

---

## 6. XY Charts

Declare with `xychart-beta`. Supports bar charts, line charts, and combinations.

### Basic bar chart

```
xychart-beta
    title "Product Sales"
    x-axis [Widgets, Gadgets, Gizmos, Doodads]
    bar [150, 230, 180, 95]
```

### Line chart

```
xychart-beta
    title "Revenue Growth"
    x-axis [2020, 2021, 2022, 2023, 2024]
    line [320, 420, 540, 680, 820]
```

### Bar + line overlay with axis labels

```
xychart-beta
    title "Monthly Revenue"
    x-axis "Month" [Jan, Feb, Mar, Apr, May, Jun]
    y-axis "Revenue (USD)" 0 --> 10000
    bar [4200, 5000, 5800, 6200, 5500, 7000]
    line [4200, 5000, 5800, 6200, 5500, 7000]
```

### Horizontal bars

```
xychart-beta horizontal
    title "Language Popularity"
    x-axis [Python, JavaScript, Java, Go, Rust]
    bar [30, 25, 20, 12, 8]
```

### Multiple series

```
xychart-beta
    title "2023 vs 2024"
    x-axis [Q1, Q2, Q3, Q4]
    bar [200, 250, 300, 280]
    bar [230, 280, 320, 350]
```

### Numeric X-axis

```
xychart-beta
    title "Distribution"
    x-axis 0 --> 100
    line [4, 7, 13, 21, 31, 43, 58, 71, 84, 91, 95, 91, 84, 71, 58, 43, 31, 21, 13, 7, 4]
```

---

## 7. Styling Reference

### Node styling (inline)

```
style nodeId fill:#3b82f6,stroke:#1d4ed8,color:#ffffff
```

### Class definitions

```
classDef className fill:#color,stroke:#color,color:#color,stroke-width:2px
A:::className
```

### Link styling

```
linkStyle INDEX stroke:#color,stroke-width:Npx
linkStyle default stroke:#color                    %% all links
linkStyle 0,1,2 stroke:#color                      %% multiple specific links
linkStyle - stroke:#color                           %% previous link (newer Mermaid)
```

Available CSS properties for linkStyle: `stroke`, `stroke-width`, `stroke-dasharray`, `color` (label color).

When using `stroke-dasharray`, escape commas: `stroke-dasharray: 5\, 5`

### Available curve styles

Set via Mermaid config: `basis`, `bump`, `linear`, `monotoneX`, `monotoneY`, `natural`, `step`,
`stepAfter`, `stepBefore`.
