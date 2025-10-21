from .state import AgentState
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers.json import JsonOutputParser
from langchain_ollama.chat_models import ChatOllama
from dotenv import load_dotenv
import os

load_dotenv()

def node_presenter(state: AgentState):
    print("Node Presenter activated")

    selected_venues = state['selected_venues']
    text_llm = ChatOllama(
        model = os.environ.get("PRESENTER_LLM"),
        temperature=0.2,
    )
    print(selected_venues)
    if not selected_venues or selected_venues == "[]":
        print("No venues were selected.")
        prompt = "You're a helpful research assistant. Write a polite message informing the user that after searching with the keywords {keywords}, no relevant conferences were found."
        prompt = ChatPromptTemplate.from_template(prompt)
        chain = prompt | text_llm
        response = chain.invoke({
            "keywords": state['keywords']
        })
    else:
        print("Selected venues:")
        for venue in selected_venues:
            print(f"- {venue['full_name']} ({venue['acronym']})")
        prompt ="""You are a helpful research assistant. Write a final report for the researcher.
        The report should be in Markdown format and clearly present the recommended conferences,
        including the acronym, full name, deadline, and WikiCFP link.

        Recommended Conferences:
        {venues}
        """
        prompt = ChatPromptTemplate.from_template(prompt)
        chain = prompt | text_llm
        response = chain.invoke({
            "venues": selected_venues,
        })
    print("Final decision generated.")
    return{"final_decision": response.content}