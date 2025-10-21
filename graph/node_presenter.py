from .state import AgentState
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers.json import JsonOutputParser
from langchain_ollama.chat_models import ChatOllama
from dotenv import load_dotenv
from .prompts import PRESENTATION_PROMPT_TEMPLATE, PRESENTATION_PROMPT_TEMPLATE_FALLBACK
import os

load_dotenv()

def node_presenter(state: AgentState):
    print("Node Presenter activated")

    selected_venues = state['selected_venues']
    text_llm = ChatOllama(
        model = os.environ.get("PRESENTER_LLM"),
        temperature=0.2,
    )
    if not selected_venues or selected_venues == "[]":
        print("No venues were selected.")
        prompt = PRESENTATION_PROMPT_TEMPLATE_FALLBACK
        prompt = ChatPromptTemplate.from_template(prompt)
        chain = prompt | text_llm
        response = chain.invoke({
            "keywords": state['keywords']
        })
        print("Final decision generated.")
        return {"final_decision": response.content}
    
    print("Selected venues:")
    for venue in selected_venues:
        print(f"- {venue}")
    
    prompt = PRESENTATION_PROMPT_TEMPLATE
    prompt = ChatPromptTemplate.from_template(prompt)
    chain = prompt | text_llm
    response = chain.invoke({
        "venues": selected_venues,
    })
    return{"final_decision": response.content}