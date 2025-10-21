from __future__ import annotations
from typing import List

from langchain_core.output_parsers.json import JsonOutputParser
from langchain_ollama.chat_models import ChatOllama
from langgraph.graph import END, StateGraph
from langchain_core.prompts import ChatPromptTemplate
from .prompts import ANALYST_PLAN_TEMPLATE, ANALYST_REASONING_TEMPLATE, ANALYST_JSON_TEMPLATE
from .agent import Agent
import os
from .state import AnalystState

def build_analyst_loop():
    analyst_model = 'ANALYST_LLM'
    analyst_llm = ChatOllama(model = os.environ[analyst_model], temperature = 0.2)
    analyst_agent = Agent(
        name="Analyst",
        role="Conference keyword analyst",
        llm = analyst_llm,
        plan_template=ANALYST_PLAN_TEMPLATE,
        reasoning_template=ANALYST_REASONING_TEMPLATE,
    )

    graph = StateGraph(AnalystState)
    json_model = "JSON_LLM"
    json_llm = ChatOllama(
        model = os.environ[json_model],
        temperature = 0,
        format='json',
    )

    json_chain = ChatPromptTemplate.from_template(ANALYST_JSON_TEMPLATE) | json_llm | JsonOutputParser()

    def planning_node(state: AnalystState) -> AnalystState:
        iteration = state["iteration"] + 1
        print(f"--- Analyst Planning Iteration {iteration} ---")
        plan_text = analyst_agent.plan({
            "summary": state["summary"],
            "iteration": iteration,
        })
        print(f"Plan: {plan_text[:200]}\n...")
        plan_log = state["plan_log"]
        if plan_text:
            plan_log.append(plan_text)
        
        return {
            "iteration": iteration,
            "plan": plan_text,
            "plan_log": plan_log,
            "satisfied": False,
        }

    def reasoning_node(state: AnalystState) -> AnalystState:
        iteration = state["iteration"]
        print(f"--- Analyst Reasoning Iteration {iteration} ---")
        response = analyst_agent.reason({
            "summary": state["summary"],
            "plan": state["plan"],
            "iteration": iteration,
        })

        print(f"Reasoning: {response}\n...")

        reasoning_log = state["reasoning_log"]
        reasoning_log.append(response)

        return {
            "reasoning": response,
            "reasoning_log": reasoning_log,
        }

    def extract_keywords(state: AnalystState) -> List[str]:
        print("--- Extracting Keywords ---")
        reasoning = state['reasoning']
        response = json_chain.invoke({
            "reasoning": reasoning,
        })

        keywords = response.get("keywords", [])

        if len(keywords) == 0:
            print("No keywords extracted.")
            return {"keywords": [], "satisfied": False}
        print(f"Extracted Keywords: {keywords}")
        return {"keywords": keywords, "satisfied": True}

    def routing_node(state: AnalystState) -> str:
        if state['satisfied']:
            return "finish"
        if state["iteration"] >= state["max_iterations"]:
            print("Max iterations reached.")
            return "finish"
        return "plan"

    graph.add_node("plan", planning_node)
    graph.add_node("reason", reasoning_node)
    graph.add_node("extract", extract_keywords)

    graph.set_entry_point("plan")
    graph.add_edge("plan", "reason")
    graph.add_edge("reason", "extract")
    graph.add_conditional_edges(
        "extract",
        routing_node,
        {
            "plan": "plan",
            "finish": END,
        },
    )

    app = graph.compile()
    return app, analyst_agent
