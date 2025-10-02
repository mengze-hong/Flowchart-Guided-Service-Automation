```mermaid
flowchart TD
    A["Start Node: Initialize account inquiry task with scenario context and agent role"] --> B["Action Node: Determine type of enquiry (Balance/Credit Limit, Transaction, Unrecognized Charges)"]

    B --> |Account Balance/Credit Limit| C["Decision Node: Check if customer is an active online banking or Connect App user"]
    C -->|No| D["Action Node: Provide direct assistance for balance/credit limit enquiry"]
    D --> E["Output Node: Deliver balance/credit limit information"]
    C -->|Yes| F["Decision Node: Offer guidance or direct assistance for balance/credit limit enquiry"]
    F -->|Assistance| D
    F -->|Guidance| G["Decision Node: Choose guidance type (App or Online Banking)"]
    G -->|App| H["Output Node: Provide app guidance for balance/credit limit enquiry"]
    G -->|Online Banking| I["Output Node: Provide online banking guidance for balance/credit limit enquiry"]

    E --> J["Reflection Node: Assess if enquiry is fully resolved"]
    H --> J
    I --> J

    B -->|Transaction| K["Decision Node: Choose guidance type for transaction enquiry (App or Online Banking)"]
    K -->|App| L["Output Node: Provide app guidance for transaction enquiry"]
    K -->|Online Banking| M["Output Node: Provide online banking guidance for transaction enquiry"]
    L --> J
    M --> J

    B -->|Unrecognized Charges| N["Action Node: Perform charge check and gather relevant details"]
    N --> O["Output Node: Provide charge check results and possible resolution steps"]
    O --> J

    J -->|Complete| P["End Node: Close enquiry and confirm resolution with customer"]
    J -->|Incomplete| B
```