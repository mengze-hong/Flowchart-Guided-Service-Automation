#!/usr/bin/env python
# -*- coding: utf-8 -*-
################################################################################
#
# File: recommend.py
# Author: chaotaochen@webank.com
#
################################################################################

import json
from datetime import datetime

system_prompt = """
You are a product seller at ABC Bank, a Malaysian bank.
You need to subtly recommend all the following Products to customer following the Recommend Procedure. Act naturally, be friendly and professional.

## Products 
Here is the introduction of available products:
{{#products#}}

## Recommend Procedure
If customer has no more request, follow the workflow to recommend products.
Here is the workflow of recommend a product:
```mermaid
flowchart TD
    A{Is any unrecommended products?}
    A -- No --> B[End]
    A -- Yes --> C[Select a relevant product, ask customer whether like to know more about the product} 
    C -- No --> A
    C -- Yes --> D[Only introduce the product advantanges}
    D --> E{Is customer want the product?}
    E --> No --> A
    E -- > Yes --> F[Tell customer how to set up the product]
    F --> A
```

## Instructions
- **Relevance**: Only cross-sell products that are directly relevant to the customer's needs and the current conversation.
- **Timing**: Introduce the cross-sell opportunity naturally within the flow of the conversation.
- **Value Proposition**: Clearly explain the benefits of the product and why it would be useful to the customer.
- **Customer Choice**: Always give the customer the option to decline or learn more.
- **Helpful Approach**: Focus on assisting the customer, not just making a sale.
- **Concise**: Respone in short and concise. Only include a point in a response.
- Recommend all the products one by one.

## Current time
{{#current_time#}}
"""

default_products = """
### Multi Currency Feature
- Description: ABC credit card has a Multi Currency Feature,  which has one of the best foreign exchange rates in the market. The feature allows to hold MYR and twelve (12) foreign currencies in one account. This means user can hold different currencies, like the Euro or Pound Sterling, and convert them with our competitive exchange rates.
- Setup: It's easy to set up via the Connect App: After logging in, click on Menu, then tap on Foreign Currency Deposit, select the currency and amount, and follow the steps.
- Tutorial: A tutorial video on YouTube by searching 'ABC Bank Multi Currency Feature'.

### Travel Insurance 
- Description: Travel innsurance has a special offer with 10% cashback if sign up today.
"""

class Recommend(object):
    def __init__(self, model, client):
        self.model = model
        self.client = client
        self.system_prompt = system_prompt

    def chat_stream(self, messages, products=default_products):
        current_time = str(datetime.now())
        system_prompt = self.system_prompt.replace("{{#current_time#}}", current_time).\
            replace("{{#products#}}", products.strip())
        messages = [{"role": "system", "content": system_prompt}] + messages
        # 流式
        s_value = True
        # 请求
        chat_completion = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.01,
            stream=s_value,
        )
        for chunk in chat_completion:
            if hasattr(chunk.choices[0].delta, 'reasoning_content'):
                if chunk.choices[0].delta.reasoning_content:
                    yield {"type": "thinking", "content": chunk.choices[0].delta.reasoning_content}
            if hasattr(chunk.choices[0].delta, 'content'):
                if chunk.choices[0].delta.content:
                    yield {"type": "answer", "content": chunk.choices[0].delta.content}
    
    def chat(self, messages, products=default_products):
        current_time = str(datetime.now())
        system_prompt = self.system_prompt.replace("{{#current_time#}}", current_time).\
            replace("{{#products#}}", products.strip())
        messages = [{"role": "system", "content": system_prompt}] + messages
        # 流式
        s_value = True
        # 请求
        chat_completion = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.3,
            stream=s_value,
        )
        answer = ""
        if s_value:
            think_start = False
            think = ""
            answer_start = False
            for chunk in chat_completion:
                # 打印思维链内容
                if hasattr(chunk.choices[0].delta, 'reasoning_content'):
                    if not think_start:
                        print("[Think]: ", end="", flush=True)
                        think_start = True
                    think += chunk.choices[0].delta.reasoning_content
                    print(
                        f"{chunk.choices[0].delta.reasoning_content}", end="", flush=True)
                # 打印模型最终返回的content
                if hasattr(chunk.choices[0].delta, 'content'):
                    if chunk.choices[0].delta.content != None and len(chunk.choices[0].delta.content) != 0:
                        if not answer_start:
                            print("[Assistant]: ", end="", flush=True)
                            answer_start = True
                        answer += chunk.choices[0].delta.content
                        print(chunk.choices[0].delta.content, end="", flush=True)
            print()
        else:
            answer = chat_completion.choices[0].message.content
        return answer
