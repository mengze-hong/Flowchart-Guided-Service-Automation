flowchart TD
    v_s["Start Node: Initialize restaurant inquiry task with scenario context and agent role"]
    v_1["Action Node: Request core preference slots (cuisine, price range, location) from customer"]
    v_2["Decision Node: Validate completeness and correctness of preference slots"]
    v_3["Output Node: Provide restaurant options based on filled slots"]
    v_4["Action Node: Request booking detail slots (party size, date, time)"]
    v_5["Decision Node: Check table availability based on booking slots"]
    v_6["Output Node: Confirm table booking and provide reference number"]
    v_7["Reflection Node: Assess if all required slots are filled and task objectives met"]
    v_m["End Node: Finalize task and confirm completion with customer"]

    v_s --> v_1
    v_1 --> v_2
    v_2 -->|Valid| v_3
    v_2 -->|Invalid or Incomplete| v_1
    v_3 --> v_4
    v_4 --> v_5
    v_5 -->|Available| v_6
    v_5 -->|Unavailable| v_4
    v_6 --> v_7
    v_7 -->|Complete| v_m
    v_7 -->|Incomplete| v_1
