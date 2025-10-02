flowchart TD
    v_s["Start Node: Initialize taxi booking task with scenario context and agent role"]
    v_1["Action Node: Request trip detail slots (pickup location, drop-off location, departure time) from customer"]
    v_2["Decision Node: Validate completeness and correctness of trip detail slots"]
    v_3["Output Node: Confirm taxi booking and provide service details (car type, color, contact, fare, travel time)"]
    v_4["Reflection Node: Assess if all required slots are filled and task objectives met"]
    v_m["End Node: Finalize taxi task and confirm completion with customer"]

    v_s --> v_1
    v_1 --> v_2
    v_2 -->|Valid| v_3
    v_2 -->|Invalid or Incomplete| v_1
    v_3 --> v_4
    v_4 -->|Complete| v_m
    v_4 -->|Incomplete| v_1
