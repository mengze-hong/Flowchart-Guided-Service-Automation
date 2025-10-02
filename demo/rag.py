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
from kb_search import KBClient

system_prompt = """
You are a customer service call agent at ABC Bank, a Malaysian bank.

## Personal information
- Name: Khairul Ahmad
- Job Title: Customer Relationship Officer at ABC Bank

## Search results
{{#search_result#}}

## Instructions
- Answer the user's question based on personal information and current search results only.
- If the personal information and search results do not contain any information to answer the user's question, directly reply: "Sorry, I cannot answer this question, I'd recommend speaking with a human agent. Is it okay if I transfer you?", no extra comments.
- If user's question is not clear, ask for clarification.
- Do not mention the search results, as this may confuse the user.
- Reply in English.

## Current time
{{#current_time#}}
"""

search_user_prompt = """你是一名搜索任务规划师，负责根据用户对话内容，规划清晰合理的搜索任务，以解决用户的最新问题。

# 以下是用户与客服助手的对话记录
{{#history#}}

在回答时，请注意以下几点：
- 搜索Query的语言需要和用户消息的语言保持一致。
- 可以回答1~2个Query，一行一个Query。
- 如果不需要进行搜索(如咨询个人信息，打招呼等)，请回答“None”。
- 只用回答搜索Query。
"""


class Chitchat(object):
    def __init__(self, model, client):
        self.model = model
        self.client = client
        self.kb_client = KBClient()
        self.search_user_prompt = search_user_prompt
        self.system_prompt = system_prompt

    def search(self, messages):
        history = "\n".join(
            f"[{msg['role']}]: {msg['content']}" for msg in messages)
        prompt = self.search_user_prompt.replace("{{#history#}}", history)
        messages = [{"role": "user", "content": prompt}]
        res = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.01,
            stream=False,
        )
        queries = res.choices[0].message.content
        if queries == "None":
            return ""

        queries = [q.strip() for q in queries.split("\n")]
        print(f"[Search]: {queries}")
        docs = self.kb_client.search(queries, top_k=2)
        text = "\n\n".join(doc["content"] for doc in docs)
        return text

    def chat_stream(self, messages):
        search_result = self.search(messages)
        current_time = str(datetime.now())
        system_prompt = self.system_prompt.replace("{{#current_time#}}", current_time).\
            replace("{{#search_result#}}", search_result)
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

    def chat(self, messages):
        search_result = self.search(messages)
        current_time = str(datetime.now())
        system_prompt = self.system_prompt.replace("{{#current_time#}}", current_time).\
            replace("{{#search_result#}}", search_result)
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
                        print(chunk.choices[0].delta.content,
                              end="", flush=True)
            print()
        else:
            answer = chat_completion.choices[0].message.content
        return answer
