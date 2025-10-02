#!/usr/bin/env python
# -*- coding: utf-8 -*-
################################################################################
#
# File: app.py
# Author: chaotaochen@webank.com
#
################################################################################

import os
import json
import time
import random
import streamlit as st
from datetime import datetime
from openai import OpenAI

import config
from pathlib import Path
from manager import Manager

# 构造 client
client = OpenAI(
    api_key=config.api_key,
    base_url=config.base_url,
)
scenarios = sorted(Path("scenarios").glob("*.json"))

# 页面设置
st.set_page_config(
    page_title="Demo",
    page_icon=":robot:",
    layout='centered',
    initial_sidebar_state='expanded',
)

dials_file = "dials.json"


def reset():
    st.session_state.dials[st.session_state.dial_id] = {
        "messages": []}


def choose_dial(i):
    st.session_state.dial_id = i


# 初始化session状态
if 'dials' not in st.session_state:
    st.session_state.dials = [{"messages": []}]
    st.session_state.dial_id = 0
    if os.path.exists(dials_file):
        with open(dials_file, "r") as f:
            dials = json.load(f)
            for dial in dials:
                if "manager" in dial:
                    manager = Manager(config.model, client, scenarios)
                    manager.load(dial["manager"])
                    dial["manager"] = manager
        if dials:
            st.session_state.dials = dials
            st.session_state.dial_id = len(dials)-1


# 侧边栏：会话管理
with st.sidebar:
    # st.subheader("模型配置")
    # model = st.radio(
    #     '模型名称',
    #     models,
    #     index=0,
    # )
    # temperature = st.slider("temperature", 0.0, 1.0, 0.3)

    st.subheader("Dialogue Management")
    cols = st.columns(3)
    clear_dial = cols[0].button("Clear", use_container_width=True)
    save_dial = cols[1].button("Save", use_container_width=True)
    new_dial = cols[2].button("New", use_container_width=True)

    if clear_dial:
        reset()

    if save_dial:
        saved_dials = [{"manager": dial["manager"].state_dict(),
                       "messages": dial["messages"]}
                       for dial in st.session_state.dials]
        with open("dials.json", "w") as f:
            json.dump(saved_dials, f,
                      ensure_ascii=False, indent=4)
        st.success("Conversation saved!")

    if new_dial:
        manager = Manager(config.model, client, scenarios)
        st.session_state.dials.append({"manager": manager, "messages": []})
        st.session_state.dial_id = len(st.session_state.dials)-1

    # 显示历史会话
    st.subheader("Dialogue")
    for i in reversed(range(len(st.session_state.dials))):
        st.button(f"Dial {i}", use_container_width=True,
                  on_click=choose_dial, args=[i])


def think2markdown(think):
    return "**Think**:\n" + "\n".join(f":gray[{s}]" if s else s for s in think.split("\n"))


def think2html(think):
    return f"""<span style="color:blue">{think}</span>"""


# 用户输入
prompt_text = st.chat_input("Input your question")

dial = st.session_state.dials[st.session_state.dial_id]
history = dial["messages"]
if "manager" not in dial:
    dial["manager"] = Manager(config.model, client, scenarios)
manager = dial["manager"]
chat_container = st.container()
with chat_container.chat_message("assistant"):
    st.markdown("Hi, thank you for calling ABC Bank. Adeline speaking, how can I help you today?")
for msg in history:
    with chat_container.chat_message(msg["role"]):
        if msg["role"] == "assistant":
            st.markdown(msg["full_content"])
        else:
            st.markdown(msg["content"])

if prompt_text:
    # 添加用户消息到当前会话
    history.append(
        {"role": "user", "content": prompt_text, "type": "normal"})

    # 清空输入后显示最新消息
    with chat_container.chat_message("user"):
        st.markdown(prompt_text)

    # 准备助手消息
    with chat_container.chat_message("assistant"):
        response_placeholder = st.empty()
        think = ""
        answer = ""
        # 处理流式响应
        full_content = ""

        stream = manager.chat_stream(history)
        for chunk in stream:
            if chunk["type"] == "thinking":
                think += "\n\n" + chunk["content"]
            elif chunk["type"] == "answer":
                answer += chunk["content"]
            if think:
                if answer:
                    full_content = f"{think2markdown(think)}\n\n**Answer:**\n{answer}"
                else:
                    full_content = think2markdown(think)
            else:
                full_content = answer
            response_placeholder.markdown(full_content + "▌")

        # 最终回答
        response_placeholder.markdown(full_content)
        history.append({
            "role": "assistant",
            "content": answer,
            "full_content": full_content,
        })
