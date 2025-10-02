```mermaid
flowchart TD
    A["Start Node: Initialize overseas travel notification task with scenario context and agent role"] --> B["Decision Node: Check if customer is an active Connect App user"]

    B -->|No| C["Action Node: Provide direct assistance with overseas travel notification setup"]
    C --> D["Action Node: Complete overseas travel notification setup"]

    B -->|Yes| E["Decision Node: Confirm customer still has Connect App downloaded"]
    E -->|No| C
    E -->|Yes| F["Decision Node: Offer assistance or guidance for setting overseas travel notification"]
    F -->|Assistance| C
    F -->|Guidance| G["Output Node: Provide app guidance for overseas travel notification setup"]

    D --> H["End Node: Close request and confirm completion with customer"]
    G --> H
```