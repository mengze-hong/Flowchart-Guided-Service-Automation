#!/usr/bin/env python
# -*- coding: utf-8 -*-
################################################################################
#
# Copyright (c) 2025 WeBank Inc. Ltd. All Rights Reserved.
#
# File: kb_search.py
# Author: chaotaochen@webank.com
#
################################################################################

import json
from pathlib import Path


class KBClient(object):
    def __init__(
        self,
        kb_dir="./kb/",
    ):
        self.docs = []
        for doc_file in Path(kb_dir).rglob("*.json"):
            with open(doc_file, "r") as f:
                self.docs += json.load(f)

    def search(self, queries, top_k=3):
        return self.docs[:top_k]

    # def search(self, queries, top_k=3, score=0.3):
    #     url = f"{self.url}/kb/search"
    #     headers = {
    #         "jwt": self.jwt,
    #     }
    #     docs = []
    #     for query in queries:
    #         data = {
    #             "kb_id": kb_id,
    #             "query": query,
    #             "top_k": top_k,
    #             "score": score,
    #         }
    #         res = requests.post(url, json=data, headers=headers)
    #         res = res.json()
    #         res = res["data"]["result"]
    #         for seg in res["segments"]:
    #             seg["category"] = "Document"
    #             docs.append(seg)
    #         for qa in res["qas"]:
    #             qa["category"] = "FAQ"
    #             qa["content"] = f"Question: {qa['question']}\nAnswer: {qa['answer']}"
    #             docs.append(qa)
    #     docs = sorted(docs, key=lambda d: d["score"], reverse=True)
    #     return docs
