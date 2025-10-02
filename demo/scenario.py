#!/usr/bin/env python
# -*- coding: utf-8 -*-
################################################################################
#
# File: try.py
# Author: chaotaochen@webank.com
#
################################################################################

import json
from datetime import datetime

system_prompt = """
You are a customer service call agent at ABC Bank, a Malaysian bank.

Your goals are to provide excellent customer service, follow all bank procedures, and provide accurate information. Act naturally, be friendly and professional.

Given customer account details, answer customer query following the bank procedures and instructions, and recommend the relevant products after assistant.

## Customer Account
{{#customer_account#}}


## Bank Procedures
Here is the flowchart of {{#scenario_name#}} procedure:
{{#workflow#}}

Here is the detail of diffrent processes in the flowchart:
{{#processes#}}


## Instructions
- Reply in the language of the latest customer query.
- Strictly follow the Bank Procedures.
- If you are not able to discern request info, ask customer to clarify! Do not attempt to wildly guess.
- Do not overwhelm the customer with over two questions at once; ask for the information you need in a way that they do not have to write much in each response.

## Current time
{{#current_time#}}
"""


default_customer_account = """- Account Holder Name: Quah Xin Li
- Gender: Female
- IC Number: 100908-07-0605
- Employer: Bank Malaysia
- Products with ABC Bank: Swipe Right Credit Card
- Supplementary Cardholder Full Name: Tan Sze Mei
- Most Recent Transactions:
    - 30/12/2024: RM50 - SHELL PETROL STATION
    - 30/12/2024: RM10.50 - ZUS COFFEE - STARLING
    - 29/12/2024: RM10.50 - ZUS COFFEE - STARLING
    - 28/12/2024: RM29.50 - MCDONALDS PETALING JAYA
    - 28/12/2024: RM10.50 - ZUS COFFEE - STARLING
    - 27/12/2024: RM358.90 -  JAYA GROCER - DC MALL
    - 24/12/2024: RM10.50 - ZUS COFFEE - STARLING
    - 19/12/2024: RM193.50 - PASARRAYA HERO - SHAH SLAM
    - 18/12/2024: RM54 - SERAI PAVILION
    - 15/12/2024 - RM24.90 - DISNEY+ HOTSTAR SINGAPORE
    - 14/12/2024 - RM14.35 - FAMILY MART - PLAZA DAMAS
    - 12/12/2024 - RM3439.14 - LAZADA
    - 12/12/2024: RM9,000 - DCR MARKETING SDN BHD
- Credit Card Details:
    - Credit Limit: RM35,000
    - Outstanding Balance: RM17,259.20
    - Payment Due Date: 15 Jan 2025
- Online Banking and Connect App (ABC Bank’s Online Banking App) User: Yes, active since 2019
- IVR Verified?: Yes"""


class Scenario(object):
    def __init__(self, model, client, scenario):
        self.model = model
        self.client = client
        if not isinstance(scenario, dict):
            scenario = str(scenario)
            with open(scenario, 'r', encoding='utf-8') as f:
                self.scenario = json.load(f)
            workflow_file = scenario.replace(".json", ".workflow")
            with open(workflow_file, 'r', encoding='utf-8') as f:
                self.scenario["workflow"] = f.read().strip()
        else:
            self.scenario = scenario

        processes = []
        for process in self.scenario["processes"]:
            text = ""
            text += f"### {process['name']}\n"
            if process["required_info"]:
                text += "- Required infos:\n"
                for info in process["required_info"]:
                    text += f"    - {info['name']}: {info['description']}\n"
            text += "- Process:\n"
            for i, step in enumerate(process["process"], 1):
                text += f"    {i}. {step}\n"
            processes.append(text)
        processes = "\n".join(processes).strip()

        self.system_prompt = system_prompt.replace("{{#scenario_name#}}", self.scenario["name"]).\
            replace("{{#workflow#}}", self.scenario["workflow"]).\
            replace("{{#processes#}}", processes).strip()
        # print(self.system_prompt)

    def chat_stream(self, messages, customer_account=default_customer_account):
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%s (%A)")
        system_prompt = self.system_prompt.replace("{{#current_time#}}", current_time).\
            replace("{{#customer_account#}}", customer_account)
        # print(system_prompt)
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
        for chunk in chat_completion:
            if hasattr(chunk.choices[0].delta, 'reasoning_content'):
                if chunk.choices[0].delta.reasoning_content:
                    yield {"type": "thinking", "content": chunk.choices[0].delta.reasoning_content}
            if hasattr(chunk.choices[0].delta, 'content'):
                if chunk.choices[0].delta.content:
                    yield {"type": "answer", "content": chunk.choices[0].delta.content}

    def chat(self, messages, customer_account=default_customer_account):
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%s (%A)")
        system_prompt = self.system_prompt.replace("{{#current_time#}}", current_time).\
            replace("{{#customer_account#}}", customer_account)
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
                        print(chunk.choices[0].delta.content,
                              end="", flush=True)
            print()
        else:
            answer = chat_completion.choices[0].message.content
        return answer
