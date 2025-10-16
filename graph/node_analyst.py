from .state import AgentState
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers.json import JsonOutputParser
from langchain_ollama.chat_models import ChatOllama
from dotenv import load_dotenv
import os

load_dotenv()

def node_analyst(state: AgentState):
    print("Node Analyst activated")
    json_llm = ChatOllama(
        model = os.environ.get("ANALYST_LLM"),
        temperature=0,
        format='json',
    )
    prompt = ChatPromptTemplate.from_template(
        """You are an experienced researcher. Your task is to analyze an article abstract and extract the 3 most relevant keywords for conference searches.
        Respond ONLY with a valid JSON object with the key "keywords."

        Summary: "{summary}"
        """
    )
    chain = prompt | json_llm | JsonOutputParser()
    result = chain.invoke({
        "summary": state['summary'],
    })

    return {"keywords": result['keywords'], "search_tries": 0}