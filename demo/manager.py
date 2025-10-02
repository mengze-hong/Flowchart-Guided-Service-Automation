#!/usr/bin/env python
# -*- coding: utf-8 -*-
################################################################################
#
# File: manager.py
# Author: chaotaochen@webank.com
#
################################################################################

import time
import json
from intent import IntentClassifer
from scenario import Scenario
from verification import Verification
# from chitchat import Chitchat
from rag import Chitchat
from recommend import Recommend

human_answer = "Well, to assist you better, let me transfer you to a human agent. Please hold for a moment. Thank you!"

class Manager(object):
    def __init__(self, model, client, scenarios):
        self.scenario_agents = [Scenario(model, client, scenario)
                                for scenario in scenarios]
        self.scenarios = [a.scenario for a in self.scenario_agents]
        self.scenarios += [
            {"name": "human service", "description": "customer clearly propose to transfer to manual service."},
            {"name": "chitchat", "description": "chitchat scenarios, e.g. greeting, saying goodbye, and other scenarios."},
        ]
        self.name2scenario = {s["name"]: s for s in self.scenarios}
        self.intent_classifier = IntentClassifer(model, client, self.scenarios)
        self.verification_agent = Verification(model, client)
        self.chitchat_agent = Chitchat(model, client)
        # self.recommend_scenario= {"name": "recommend product", "description": "if customer need no more assistance, try to recommend product to customer."}
        self.recommend_scenario= {"name": "recommend product", "description": "customer need no more assistance."}
        self.recommend_agent = Recommend(model, client)
        self.with_recommend_scenarios = self.scenarios + [self.recommend_scenario]
        self.with_recommend_intent_classifier = IntentClassifer(model, client, self.with_recommend_scenarios)
        self.state = "nonverify"
        self.intents = []

    def state_dict(self):
        return {"state": self.state, "intents": self.intents, "verification": self.verification_agent.state_dict()}

    def load(self, state_dict):
        self.state = state_dict["state"]
        self.intents = state_dict["intents"]
        self.verification_agent.load(state_dict["verification"])

    def predict_scenario(self, messages):
        intent_classifier = self.intent_classifier
        scenarios = self.scenarios
        if self.intents:
            pre_intent = self.intents[-1]
            if pre_intent == self.recommend_scenario["name"] or (pre_intent in self.name2scenario and self.name2scenario[pre_intent].get("relevant_products")):
                intent_classifier = self.with_recommend_intent_classifier
                scenarios = self.with_recommend_scenarios
        scenario_id = intent_classifier.predict(messages, self.intents)
        scenario_name = scenarios[scenario_id]["name"]
        return scenario_id, scenario_name

    def clean_query(self, query):
        return query.rstrip("?").rstrip("!").rstrip("！").rstrip("？")

    def chat(self, messages):
        messages[-1]["content"] = self.clean_query(messages[-1]["content"])
        scenario_id, scenario_name = self.predict_scenario(messages)
        print(f"[Intent]: {scenario_name}")
        self.intents.append(scenario_name)
        if scenario_name == "human service":
            answer = human_answer
            print(f"[Assistant]: {answer}")
        elif scenario_name == "chitchat":
            answer = self.chitchat_agent.chat(messages)
        elif scenario_name == "recommend product":
            answer = self.recommend_agent.chat(messages)
        else:
            if self.state == "nonverify":
                res = self.verification_agent.next(messages)
                self.state = "verifying"
                answer = res["content"]
                print(f"[Assistant]: {answer}")
            elif self.state == "verifying":
                self.verification_agent.verify(messages)
                res = self.verification_agent.next(messages)
                if res["code"] == 0:
                    self.state = "verified"
                else:
                    if res["code"] == 1:
                        self.state = "nonverify"
                    answer = res["content"]
                    print(f"[Assistant]: {answer}")

            if self.state == "verified":
                # print("[Wait]: 5 second")
                # time.sleep(5)
                scenario_agent = self.scenario_agents[scenario_id]
                answer = scenario_agent.chat(messages)
        return answer

    def chat_stream(self, messages):
        messages[-1]["content"] = self.clean_query(messages[-1]["content"])
        # print(messages)
        scenario_id, scenario_name = self.predict_scenario(messages)
        print(f"[Intent]: {scenario_name}")
        self.intents.append(scenario_name)
        yield {"type": "thinking", "content": f"[Intent]: {scenario_name}"}
        if scenario_name == "human service":
            yield {"type": "answer", "content": human_answer}
        elif scenario_name == "chitchat":
            for r in self.chitchat_agent.chat_stream(messages):
                yield r
        elif scenario_name == "recommend product":
            for r in self.recommend_agent.chat_stream(messages):
                yield r
        else:
            if self.state == "nonverify":
                res = self.verification_agent.next(messages)
                self.state = "verifying"
                yield {"type": "thinking", "content": "[Verification]: Start"}
                answer = res["content"]
                for char in answer:
                    yield {"type": "answer", "content": char}
            elif self.state == "verifying":
                self.verification_agent.verify(messages)
                res = self.verification_agent.next(messages)
                if res["code"] == 0:
                    self.state = "verified"
                    messages = messages + [{"role": "assistant", "content": "Great. Your provided information is right."}, {"role": "user", "content": "ok"}]
                    yield {"type": "thinking", "content": "[Verification]: Succeed"}
                else:
                    if res["code"] == 1:
                        self.state = "nonverify"
                        yield {"type": "thinking", "content": "[Verification]: Failed"}
                    elif res["code"] == 2:
                        yield {"type": "thinking", "content": "[Verification]: Passed"}
                    elif res["code"] == 3:
                        yield {"type": "thinking", "content": "[Verification]: Not matched"}
                    elif res["code"] == 4:
                        yield {"type": "thinking", "content": "[Verification]: No answer"}
                    elif res["code"] == 5:
                        yield {"type": "thinking", "content": "[Verification]: Skip"}

                    answer = res["content"]
                    for char in answer:
                        yield {"type": "answer", "content": char}

            if self.state == "verified":
                scenario_agent = self.scenario_agents[scenario_id]
                for r in scenario_agent.chat_stream(messages):
                    yield r
