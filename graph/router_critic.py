from .state import AgentState
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers.json import JsonOutputParser
from langchain_ollama.chat_models import ChatOllama
from dotenv import load_dotenv
import os


def router_critic(state: AgentState):
    print("Router Critic activated")
    insufficient = state['insufficient']
    if not insufficient:
        print("Decision: Success! Send to Node Presenter")
        return 'presenter'
    
    return "scout"
