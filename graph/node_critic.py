from .state import AgentState
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers.json import JsonOutputParser
from langchain_ollama.chat_models import ChatOllama
from dotenv import load_dotenv
import os

load_dotenv()

def node_critic(state: AgentState):
    print("Node Critic activated")

    json_llm = ChatOllama(
        model = os.environ["CRITIC_LLM"],
        temperature=0,
        format='json',
    )
    prompt = ChatPromptTemplate.from_template(
         """You are a senior article reviewer. Your task is to analyze an article abstract and a list of conferences. For each conference, a web search was performed, the results of which are listed in "additional_information."
         Select the 3 conferences that BEST match the article.

            Respond ONLY with a valid JSON object with the key "selected_venues," containing a filtered list.

            Article Abstract:
            {summary}

            List of Conferences Found (with text search results):
            {enriched_venues}
        """
    )

    chain = prompt | json_llm | JsonOutputParser()

    if 'enriched_venues' not in state:
        print("Enriching venues for the first time")
        state['enriched_venues'] = state['raw_venues']

    result = chain.invoke({
        "summary": state['summary'],
        "enriched_venues": state['enriched_venues']
    })
    print(result)
    return {"selected_venues": result['selected_venues']}