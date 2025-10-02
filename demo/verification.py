#!/usr/bin/env python
# -*- coding: utf-8 -*-
################################################################################
#
# File: verification.py
# Author: chaotaochen@webank.com
#
################################################################################

import random
from collections import Counter
from openai import OpenAI

transactions = [
    {
        "date": "30/12/2024",
        "amount": 50.0,
        "currency": "RM",
        "merchant": "SHELL PETROL STATION"
    },
    {
        "date": "30/12/2024",
        "amount": 10.5,
        "currency": "RM",
        "merchant": "ZUS COFFEE - STARLING"
    },
    {
        "date": "29/12/2024",
        "amount": 10.5,
        "currency": "RM",
        "merchant": "ZUS COFFEE - STARLING"
    },
    {
        "date": "28/12/2024",
        "amount": 29.5,
        "currency": "RM",
        "merchant": "MCDONALDS PETALING JAYA"
    },
    {
        "date": "28/12/2024",
        "amount": 10.5,
        "currency": "RM",
        "merchant": "ZUS COFFEE - STARLING"
    },
    {
        "date": "27/12/2024",
        "amount": 358.9,
        "currency": "RM",
        "merchant": "JAYA GROCER - DC MALL"
    },
    {
        "date": "24/12/2024",
        "amount": 10.5,
        "currency": "RM",
        "merchant": "ZUS COFFEE - STARLING"
    },
    {
        "date": "19/12/2024",
        "amount": 193.5,
        "currency": "RM",
        "merchant": "PASARRAYA HERO - SHAH SLAM"
    },
    {
        "date": "18/12/2024",
        "amount": 54.0,
        "currency": "RM",
        "merchant": "SERAI PAVILION"
    },
    {
        "date": "15/12/2024",
        "amount": 24.9,
        "currency": "RM",
        "merchant": "DISNEY+ HOTSTAR SINGAPORE"
    },
    {
        "date": "14/12/2024",
        "amount": 14.35,
        "currency": "RM",
        "merchant": "FAMILY MART - PLAZA DAMAS"
    },
    {
        "date": "12/12/2024",
        "amount": 3439.14,
        "currency": "RM",
        "merchant": "LAZADA"
    },
    {
        "date": "12/12/2024",
        "amount": 9000.0,
        "currency": "RM",
        "merchant": "DCR MARKETING SDN BHD"
    }
]


def ic_number():
    question = "May I have your IC number?"
    answer = "100908-07-0605"
    out = {
        "question": question,
        "candidates": [answer],
        "is_number": False,
    }
    return out


def static_questions():
    qas = [
        ("May I have the name of the company you are working with?",
         "Bank Malaysia"),
        ("May I have your Supplementary Card Holder’s Full Name?",
         "Tan Sze Mei"),
    ]
    out = [{"question": question,
            "candidates": [answer],
            "is_number": False}
           for question, answer in qas]
    random.shuffle(out)
    return out


def frequent_mechant(transactions):
    candidates = [m for m, c in Counter(
        [t["merchant"].lower() for t in transactions]).most_common(3)]
    question = "Which merchant do you frequently use your credit card for?"
    out = {
        "question": question,
        "candidates": candidates,
        "is_number": False,
    }
    return out


def lastest_amount(transactions, acc_off=0.2):
    amount = transactions[0]["amount"]
    min_amount = max(0, amount * (1-acc_off))
    max_amount = amount * (1+acc_off)
    currency = transactions[0]["currency"]
    answer = f"{min_amount:.3f} ~ {max_amount:.3f} {currency}"
    question = "What was the last payment amount you made with your credit card?"
    out = {
        "question": question,
        "candidates": [answer],
        "is_number": True,
    }
    return out


def lastest_merchant(transactions):
    question = "What was the last merchant you use your credit card for?"
    answer = transactions[0]["merchant"].lower()
    out = {
        "question": question,
        "candidates": [answer],
        "is_number": False,
    }
    return out


def week_mechant(transactions):
    question = "Can you give me the name of one merchant where you used your credit card in the past 7 days?"
    candidates = [t["merchant"].lower() for t in transactions[:7]]
    candidates = sorted(set(candidates))
    out = {
        "question": question,
        "candidates": candidates,
        "is_number": False,
    }
    return out


def dynamic_questions(transactions):
    out = [func(transactions)
           for func in [frequent_mechant, lastest_amount, lastest_merchant, week_mechant]]
    random.shuffle(out)
    return out


# print(ic_number())
# print(static_question())
# print(dynamic_question(transactions))

fail_response = "I’m sorry, some of the information you provided does not match with our records. Therefore, I am unable to assist you on the phone today. To proceed with your request, may I suggest that you use your online banking, either via the Connect App or the website, to have one of our chat agents assist you? Once you’ve logged in, you’ll find a chat icon on the bottom right to start a conversation with our chat agents. Would you like me to guide you through the login process?"

extract_answer_prompt = """Given a user-assistant conversation where the assistant is requesting a question, extract the answer from user's last response to the question.

# Instructions
- If the user cannot answer the question (e.g. forgetting), reply "<fail>".
- If the user give an response unrelated to the question or avoiding to answer the question, reply "<none>".
- If the user give an response related to the question, reply the extracted answer.
- Return one of "<fail>", "<none>" and the extracted answer only, no extra content.

# Example

<conversation>
[assistant]: Tell me your IC number, please.
[user]: My IC number is 101000030406.
</conversation>
Question: May I have your IC number?
Extraction: 101000030406

<conversation>
[assistant]: May I have your IC number for verification?
[user]: My IC number is 101000030406.
[assistant]: Could you tell me what was the last payment amount you made with your credit card?
[user]: about 100
</conversation>
Question: What was the last payment amount you made with your credit card?
Extraction: 100

<conversation>
[assistant]: I need your working company.
[user]: I don't want to say.
</conversation>
Question: May I have the name of the company you are working with?
Extraction: <none>

<conversation>
[assistant]: Can you confirm which merchant do you frequently use your credit card for?
[user]: I remember it was KFC.
</conversation>
Extraction: KFC

<conversation>
[assistant]: What's your IC number?
[user]: I don't remember.
</conversation>
Question: May I have your IC number?
Extraction: <fail>

<conversation>
[assistant]: What's your IC number?
[user]: XXX, i think
</conversation>
Question: May I have your IC number?
Extraction: XXX

# Input
<conversation>
{conversation}
</conversation>
Question: {question}
Extraction: """


ask_prompt = """You are an assistant for verification.
Given user-assistant conversation (inside <conversation> XML tag), latest verification state and verification question to request,  you need to:
- First respond to user's latest message in a polite way.
- Then enquriy the user with respect to the verification question in a concise way.

# Example

<conversation>
[user]: can you help me increase my credit card limit
<conversation>
Verification State: Start.
Verification Question: May I have your Supplementary Card Holder's Full Name?
Response: Sure, to assist with that, may I have your Supplementary Card Holder's Full Name for verification?

<conversation>
[user]: How much balance I have?
[assistant]: Glad to help your. To check your balance, may I have your IC number for verification?
[user]: no, it's secret.
<conversation>
Verification State: User doesn't answer the verification question.
Verification Question: May I have your IC number?
Response: I understood your concern. But to check your balance, your IC number is necessary for verification. Could you provide it?

<conversation>
[user]: I want to check my credit card limit
[assistant]: Certainly, I can assist with checking your credit card limit. For verification purpose, may I have your IC number?
[user]: it's 1230789.
<conversation>
Verification State: User's answer is not matched.
Verification Question: May I have your IC number?
Response: Sorry, the IC number provided doesn't match our records. Could you please verify and provide it again for verification?

<conversation>
[user]: Help me set up oveasea travel alert.
[assistant]: No problem. May I have your IC number for verification?
[user]: 123000300.
<conversation>
Verification State: Success.
Verification Question: May I have the name of the company you are working with?
Response: Thanks for providing your IC number. Could you tell me the company you are working with?

<conversation>
[user]: How to change my credit card limit?
[assistant]: To assist with changing your credit card limit, may I have your IC number for verification?
[user]: Sorry, i don't remember.
<conversation>
Verification State: User cannot answer the verification question.
Verification Question: May I have the name of the company you are working with?
Response: All right. For further verification, would you tell me the company you are working with?

# Input

<conversation>
{conversation}
</conversation>
Verification State: {verification_state}
Verification Question: {question}
Response: """


verify_qa_prompt = """Given a question seeking information of a customer, and the description of its answer,
determine which case the customer response is:
- **Yes**: The customer response is valid to the question.
- **No**: The customer response is not valid to the question.
Reply only Yes or No.

# Example

Question: May I have your IC number?
Answer Description: One of: ["100000-010", "101000-03-0406"]
Customer Response: 100000010
Valid: Yes

Question: What was the last payment amount you made with your credit card?
Answer Description: Number between: 80.000 ~ 120.000 RM
Customer Response: 100
Valid: Yes

Question: What was the last payment amount you made with your credit card?
Answer Description: Number between: 80.000 ~ 120.000 RM
Customer Response: 150
Valid: No

Question: Which merchant do you frequently use your credit card for?
Answer Description: One of: ["kfc", "coffee shop"]
Customer Response: apple shop
Valid: No

Question: Which merchant do you frequently use your credit card for?
Answer Description: One of: ["kfc", "coffee shop"]
Customer Response: station or coffee shop
Valid: Yes

Question: "May I have your Supplementary Card Holder’s Full Name?"
Answer Description: One of: ["tan hua"]
Customer Response: tan hua, or is it li bin?
Valid: Yes

Question: {question}
Answer Description: {candidates}
Customer Response: {response}
Valid: """




class Verification(object):
    def __init__(self, model, client):
        self.model = model
        self.client = client
        self.step = 0
        self.qa_id = 0
        self.state = [
            [ic_number()],
            static_questions(),
            dynamic_questions(transactions),
        ]
        for qas in self.state:
            for qa in qas:
                qa["candidates"] = [c.lower() for c in qa["candidates"]]
                qa["passed"] = False
                qa["num"] = 0
        # print(self.state)
        self.current_ver_result = None

    def state_dict(self):
        return {"state": self.state, "step": self.step, "qa_id": self.qa_id,
                "current_ver_result": self.current_ver_result}

    def load(self, state_dict):
        self.step = state_dict["step"]
        self.qa_id = state_dict["qa_id"]
        self.current_ver_result = state_dict["current_ver_result"]
        self.state = state_dict["state"]

    def extract_answer(self, messages):
        question = self.state[self.step][self.qa_id]["question"]
        conversation = "\n".join(f"[{msg['role']}]: {msg['content']}" for msg in messages[1:])
        prompt = extract_answer_prompt.format(
            question=question,
            conversation=conversation,
        )
        messages = [{"role": "user", "content": prompt}]
        # print(prompt)
        chat_completion = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            stream=False,
        )
        answer = chat_completion.choices[0].message.content.lower()
        return answer

    def verify_qa(self, question, candidates, is_number, response):
        if is_number:
            candidates = f"Number betweeen: {candidates[0]}"
        else:
            candidates = f"One of: {candidates}"
        prompt = verify_qa_prompt.format(
            question=question,
            candidates=candidates,
            response=response,
        )
        # print(prompt)
        messages = [{"role": "user", "content": prompt}]
        # print(prompt)
        chat_completion = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            stream=False,
        )
        answer = chat_completion.choices[0].message.content
        print("[Valid]:", answer)
        return answer


    def verify(self, messages):
        qas = self.state[self.step]
        qa = qas[self.qa_id]
        response = messages[-1]["content"]
        if response.lower() in qa["candidates"]:
            qa["num"] += 1
            qa["passed"] = True
            self.current_ver_result = "passed"
            self.step += 1
            self.qa_id = 0
        else:
            answer = self.extract_answer(messages)
            print("[Extracted answer]:", answer)
            if answer in qa["candidates"]:
                qa["num"] += 1
                qa["passed"] = True
                self.current_ver_result = "passed"
                self.step += 1
                self.qa_id = 0
            elif answer == "<fail>":
                qa["num"] += 1
                self.current_ver_result = answer
                if self.qa_id + 1 < len(qas):
                    self.qa_id += 1
                else:
                    self.step += 1
                    self.qa_id = 0
            elif answer == "<none>":
                self.current_ver_result = "no answer"
            else:
                qa["num"] += 1
                res = self.verify_qa(question=qa["question"],
                                       candidates=qa["candidates"],
                                       is_number=qa["is_number"],
                                       response=answer)
                if res == "Yes":
                    qa["passed"] = True
                    self.current_ver_result = "passed"
                    self.step += 1
                    self.qa_id = 0
                else:
                    if self.step == 0:
                        self.current_ver_result = "passed"
                        self.step += 1
                        self.qa_id = 0
                    else:
                        self.current_ver_result = "no match"
        # print(self.state)
        # print(self.step)

    def ask(self, messages, question):
        conversation = "\n".join(f"[{msg['role']}]: {msg['content']}" for msg in messages)

        if self.current_ver_result == "<fail>":
            verification_state = "User cannot answer the verification question."
        elif self.current_ver_result == "no answer":
            verification_state = "User doesn't answer the verification question."
        elif self.current_ver_result == "passed":
            verification_state = "Success."
        elif self.current_ver_result == "no match":
            verification_state = "User's answer is not matched."
        else:
            verification_state = "Start."
        prompt = ask_prompt.format(
            conversation=conversation,
            question=question,
            verification_state=verification_state,
       )
        messages = [{"role": "user", "content": prompt}]
        # print(prompt)
        chat_completion = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            stream=False,
        )
        answer = chat_completion.choices[0].message.content
        return answer


    def next(self, messages):
        if self.step >= len(self.state):
            if all(any(qa["passed"] for qa in qas) for qas in self.state):
                return {"code": 0, "content": "Verification succeed."}
            else:
                return {"code": 1, "content": fail_response}
        qa = self.state[self.step][self.qa_id]
        if not qa["passed"] and qa["num"] >= 5:
            return {"code": 1, "content": fail_response}

        question = self.ask(messages, qa["question"])
        if self.current_ver_result == "<fail>":
            return {"code": 5, "content": question}
        elif self.current_ver_result == "no answer":
            return {"code": 4, "content": question}
        elif self.current_ver_result == "no match":
            return {"code": 3, "content": question}
        else:
            return {"code": 2, "content": question}
