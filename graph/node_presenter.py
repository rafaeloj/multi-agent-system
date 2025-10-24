from .state import AgentState
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers.json import JsonOutputParser
from langchain_ollama.chat_models import ChatOllama
from .prompts import PRESENTER_TEMPLATE_FIND, PRESENTER_TEMPLATE_NOT_FIND
from dotenv import load_dotenv
import os

load_dotenv()

def node_presenter(state: AgentState):
    print("---- Node Presenter activated ----")

    selected_venues = state['selected_venues']
    text_llm = ChatOllama(
        model = os.environ.get("PRESENTER_LLM"),
        temperature=0.2,
    )
    # print(selected_venues)
    if not selected_venues or selected_venues == "[]":
        print("No venues were selected.")
        prompt = ChatPromptTemplate.from_template(PRESENTER_TEMPLATE_NOT_FIND)
        chain = prompt | text_llm
        response = chain.invoke({
            "keywords": state['keywords']
        })
    else:
        print("Selected venues:")
        for venue in selected_venues:
            print(f"- {venue['name']} ({venue['acronym']})")
        prompt = ChatPromptTemplate.from_template(PRESENTER_TEMPLATE_FIND)
        chain = prompt | text_llm
        response = chain.invoke({
            "venues": selected_venues,
        })
    return{"final_decision": response.content}