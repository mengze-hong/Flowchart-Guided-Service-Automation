```mermaid
flowchart TD
    A["Start Node: Initialize credit card limit increase task with scenario context and agent role"] --> B["Decision Node: Check if customer is an active online banking or Connect App user"]

    B -->|No| C["Action Node: Provide direct assistance for limit increase request"]
    C --> D["Decision Node: Determine if increase is Permanent or Temporary"]
    D -->|Permanent| E["Action Node: Process permanent limit increase"]
    D -->|Temporary| F["Action Node: Process temporary limit increase"]

    B -->|Yes| H["Decision Node: Offer guidance or direct assistance"]
    H -->|Assistance| C
    H -->|Guidance| I["Decision Node: Choose guidance type (App or Online Banking)"]
    I -->|App| J["Output Node: Provide app guidance for limit increase"]
    I -->|Online Banking| K["Output Node: Provide online banking guidance for limit increase"]

    E --> L["Output Node: Inform customer same limit applies to supplementary card"]
    F --> L
    J --> L
    K --> L

    L --> M["End Node: Close request and confirm completion with customer"]
```