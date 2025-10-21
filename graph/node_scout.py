from .state import AgentState
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers.json import JsonOutputParser
from langchain_ollama.chat_models import ChatOllama
from tools import search_wikicfp_tool

def node_scout(state: AgentState):
    print("Node Scout activated")

    tries = state['search_tries']
    keywords = state['keywords']
    current_keyword = keywords[tries]

    print(f"Searching conferences with keyword: {current_keyword}")
    venues = []
    for keyword in keywords:
        print(f"- {keyword}")
        result = search_wikicfp_tool(keyword, max_results=10)
        print(f"Results: {result}")
        venues.extend(result)

    print(f"Found {len(venues)} venues")
    return {
        "raw_venues": venues,
        "search_tries": tries + 1
    }

if __name__ == "__main__":
    node_scout({'search_tries': 0, 'keywords': ['machine learning', 'artificial intelligence']})
