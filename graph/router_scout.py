from .state import AgentState
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers.json import JsonOutputParser
from langchain_ollama.chat_models import ChatOllama
from dotenv import load_dotenv
import os


def router_scout(state: AgentState):
    print("Router Scout activated")
    raw_venues = state['raw_venues']
    print("Raw venues:", raw_venues)
    if raw_venues and raw_venues == "[]" or raw_venues == []:
        print("Decision: Success! Send to Node Presenter")
        return "presenter"
    
    # if state["search_tries"] < len(state["keywords"]):
        # print("Decision: No relevant conferences found. Send to Node Scout")
        # return "scout"
    
    print("Decision: Send to Node Researcher")
    return "researcher"
