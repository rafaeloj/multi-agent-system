from .state import AgentState
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers.json import JsonOutputParser
from langchain_ollama.chat_models import ChatOllama
from dotenv import load_dotenv
import os


def router_scout(state: AgentState):
    print("Router Scout activated")
    raw_venues = state['raw_vanues']
    if raw_venues and raw_venues != "[]":
        print("Decision: Success! Send to Node Researcher")
        return "researcher"
    
    # if state["search_tries"] < len(state["keywords"]):
        # print("Decision: No relevant conferences found. Send to Node Scout")
        # return "scout"
    
    print("Decision: Max search tries reached. Send to Node Presenter")
    return "critic"
