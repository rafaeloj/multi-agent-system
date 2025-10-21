from .state import AgentState
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers.json import JsonOutputParser
from langchain_ollama.chat_models import ChatOllama
from dotenv import load_dotenv
from .prompts import CRITIC_PROMPT_TEMPLATE
import os

load_dotenv()

def node_critic(state: AgentState):
    print("Node Critic activated")

    json_llm = ChatOllama(
        model = os.environ["CRITIC_LLM"],
        temperature=0,
        format='json',
    )
    prompt = ChatPromptTemplate.from_template(CRITIC_PROMPT_TEMPLATE)

    chain = prompt | json_llm | JsonOutputParser()

    if 'enriched_venues' not in state:
        print("Enriching venues for the first time")
        state['enriched_venues'] = state['raw_venues']

    result = chain.invoke({
        "summary": state['summary'],
        "enriched_venues": state['enriched_venues'],
        "K": 3, # numero de keywords
    })
    print(result)
    return {"selected_venues": result['selected_venues']}