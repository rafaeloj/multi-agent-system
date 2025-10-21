from __future__ import annotations

import os
from typing import List

from dotenv import load_dotenv
from graph.utils import save_graph

from .analyst_graph import build_analyst_loop
from .state import AgentState

load_dotenv()

def node_analyst(state: AgentState):
    print("Node Analyst activated")
    max_iterations = int(os.environ["ANALYST_MAX_ITERATIONS"])
    analyst_app, analyst_agent = build_analyst_loop()
    save_graph(analyst_app, save_path="./figs/analyst_graph.png")
    initial_loop_state = {
        "summary": state["summary"],
        "iteration": 0,
        "max_iterations": max_iterations,
        "plan_log": [],
        "reasoning_log": [],
        "keywords": [],
        "satisfied": False,
    }

    analyst_result = analyst_app.invoke(initial_loop_state)
    keywords = analyst_result["keywords"]
    print(f"Analyst keywords: {keywords}")
    
    logs = dict(state.get("agent_logs") or {})
    logs["analyst"] = {
        **analyst_agent.snapshot(),
        "iterations": analyst_result["iteration"],
        "plan_log": analyst_result["plan_log"],
        "reasoning_log": analyst_result["reasoning_log"],
        "keywords": keywords,
    }

    return {"keywords": keywords, "agent_logs": logs}
