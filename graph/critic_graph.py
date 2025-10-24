from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers.json import JsonOutputParser
from langchain_ollama.chat_models import ChatOllama
from .prompts import CRITIC_PLAN_TEMPLATE, CRITIC_REASONING_TEMPLATE, CRITIC_JSON_TEMPLATE
from .state import CriticState
from .agent import Agent
from dotenv import load_dotenv
from .agent import Agent
from langgraph.graph import END, StateGraph
from .state import CriticState

import os
load_dotenv()

def build_critic_agent():
    critic_mode = 'CRITIC_LLM'
    critic_llm = ChatOllama(model = os.environ[critic_mode], temperature = 0.2)
    critic_agent = Agent(
        name = "Critical Venue Validator",
        role = "Conference matching critic",
        llm = critic_llm,
        plan_template = CRITIC_PLAN_TEMPLATE,
        reasoning_template = CRITIC_REASONING_TEMPLATE,
    )

    json_model = "JSON_LLM"
    json_llm = ChatOllama(
        model = os.environ[json_model],
        temperature = 0,
        format='json',
    )
    prompt = ChatPromptTemplate.from_template(CRITIC_JSON_TEMPLATE)
    chain = prompt | json_llm | JsonOutputParser()

    def planning_node(state: CriticState) -> CriticState:
        iteration = state["iteration"]
        print(f"--- Critic Planning ---")
        plan = critic_agent.plan({
            "summary": state["summary"],
            "enriched_venues": state["enriched_venues"],
            "K": state["K"],
        })

        print(f"Plan: {plan[:200]}\n...")
        plan_log = state["plan_log"]

        if plan:
            plan_log.append(plan)
        return {
            "iteration": iteration,
            "plan": plan,
            "plan_log": plan_log,
            "insufficient": False,
        }
    
    def reasoning_node(state: CriticState) -> CriticState:
        iteration = state['iteration']
        print(f"--- Critic Reasoning ---")
        reasoning = critic_agent.reason({
            "summary": state["summary"],
            "enriched_venues": state["enriched_venues"],
            "K": state["K"],
            "plan": state["plan"],
        })

        print(f"Reasoning: {reasoning}\n...")

        reasoning_log = state["reasoning_log"]
        reasoning_log.append(reasoning)
        return {
            "iteration": iteration,
            "reasoning": reasoning,
            "reasoning_log": reasoning_log,
            "insufficient": False,
        }
    
    def selection_node(state: CriticState) -> CriticState:
        print(f"--- Critic Selection ---")
        iteration = state['iteration']
        response = chain.invoke({
            "K": state["K"],
            "reasoning": state["reasoning"],
        })
        selected_venues = []
        insufficient = False

        if len(response.keys()) > 1:
            selected_venues = response["selected_venues"]
            insufficient = response["insufficient"]

        return {
            "iteration": iteration,
            "selected_venues": selected_venues,
            "insufficient": insufficient,
            "keywords": response["keywords"] if "keywords" in response else state["keywords"],
        }

    def routing(state: CriticState) -> str:
        if state["iteration"] >= state["max_iterations"]:
            print("Max iterations reached.")
            return END

        if len(state['selected_venues']):
            return 'plan'
        return END
            
    graph = StateGraph(CriticState)
    graph.add_node("plan", planning_node)
    graph.add_node("reason", reasoning_node)
    graph.add_node("select", selection_node)

    graph.add_edge("plan", "reason")
    graph.add_edge("reason", "select")
    graph.add_conditional_edges(
        "select",
        routing,
        {
            "plan": "plan",
            END: END,
        },
    )
    graph.set_entry_point("plan")
    app = graph.compile()
    return app, critic_agent