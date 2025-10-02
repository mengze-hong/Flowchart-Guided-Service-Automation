#!/usr/bin/env python
# -*- coding: utf-8 -*-
################################################################################
#
# File: try.py
# Author: chaotaochen@webank.com
#
################################################################################

from datetime import datetime
from openai import OpenAI

scenario_template = """<scenario id="{scenario_id}">
<name>{scenario_name}</name>
<description>{scenario_description}</description>
</scenario>"""


def scenarios2xml(scenarios):
    return "\n".join(scenario_template.format(scenario_id=scenario_id,
                                              scenario_name=scenario["name"],
                                              scenario_description=scenario["description"])
                     for scenario_id, scenario in enumerate(scenarios))


user_prompt = """
Given following scenarios (inside <scenarios> XML tag), customer-assistant conversation (inside <conversation> XML tag)
and the previous scenario (inside <previous_scenario> XML tag) (if existed), identity which scenario is the last customer message requesting.

<scenarios>
{{#scenarios#}}
</scenarios>

<conversation>
{{#history#}}
</conversation>

<previous_scenario>
{{#previous_scenario#}}
</previous_scenario>

## Instructions
- Avoid to choose **human sevice** except the customer explicitly claiming transferring to human service.
- Choose **recommend product** (if exists) if customer need no more assistance.
- DO NOT include anything other than the scenario id in your response.
"""


class IntentClassifer(object):
    def __init__(self, model, client, scenarios):
        self.model = model
        self.client = client
        self.scenarios = scenarios
        self.user_prompt = user_prompt.replace(
            "{{#scenarios#}}", scenarios2xml(scenarios)).strip()

    def predict(self, messages, previous_scenarios=[]):
        history = "\n".join(
            f"[{msg['role']}]: {msg['content']}" for msg in messages)
        previous_scenario = previous_scenarios[-1] if previous_scenarios else ""
        prompt = self.user_prompt.replace("{{#history#}}", history).replace(
                "{{#previous_scenario#}}", previous_scenario)
        # print(prompt)
        messages = [{"role": "user", "content": prompt}]
        # print(messages[-1]["content"])
        res = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.01,
            stream=False,
        )
        answer = res.choices[0].message.content
        try:
            scenario_id = int(answer.strip())
        except:
            scenario_id = len(self.scenarios) - 1
        return scenario_id

