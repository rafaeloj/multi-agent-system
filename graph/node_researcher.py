from .state import AgentState
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers.json import JsonOutputParser
from langchain_ollama.chat_models import ChatOllama
from tools import search_wikicfp_tool
from langchain_community.tools import DuckDuckGoSearchResults
import json

def node_researcher(state: AgentState):
    print('Node Researcher activated')
    vanues_list = json.loads(state['raw_vanues'])
    if not vanues_list:
        return {"enriched_venues": []}
    ddg_search_tool = DuckDuckGoSearchResults(output_format="list")
    enriched = []
    for venue in vanues_list:
        query = f"official website and main topics of the conference {venue['full_name']} in {venue['deadline']}"
        search_results = ddg_search_tool.run(query)

        venue['additional_info'] = search_results
        enriched.append(venue)
    print("Enrichment completed.")
    print("Enriched venues:", enriched)
    return {"enriched_venues": enriched}