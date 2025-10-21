from .state import AgentState
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers.json import JsonOutputParser
from langchain_ollama.chat_models import ChatOllama
from dotenv import load_dotenv
import os
from .prompts import ANALYST_PROMPT_TEMPLATE

load_dotenv()

def node_analyst(state: AgentState):
    print("Node Analyst activated")
    json_llm = ChatOllama(
        model = os.environ.get("ANALYST_LLM"),
        temperature=0.1,
        format='json',
    )
    prompt = ChatPromptTemplate.from_template(ANALYST_PROMPT_TEMPLATE)
    chain = prompt | json_llm | JsonOutputParser()
    result = chain.invoke({
        "summary": state['summary'],
    })
    print("Node Analyst result:", result)
    return {"keywords": result['keywords'], "search_tries": 0}