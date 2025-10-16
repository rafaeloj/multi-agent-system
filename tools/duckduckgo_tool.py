from ddgs import DDGS
from langchain_community.tools import DuckDuckGoSearchResults
import json

def search_duckduckgo_tool(query: str, max_results: int = 5) -> str:
    try:
        results = None
        with DDGS() as ddgs:
            results = list(
                ddgs.text(
                    query=query,
                    region='pt-br',
                    safesearch='off',
                    max_results=max_results,
                )
            )
        if not results:
            return "No results found."
        # print(results[0])
        formatted_results = [
            {
                'link': res.get("href"),
                "snippet": res.get("body"),
                "title": res.get("title"),
            } for res in results
        ]
        return json.dumps(formatted_results, indent=2)
    except Exception as e:
        return f"Error occurred while searching DuckDuckGo: {str(e)}"


if __name__ == "__main__":
    resultados = search_duckduckgo_tool("What is the capital of France?", max_results=3)
    print("\n--- Search Results ---")
    print(resultados)


    ddg_search_tool = DuckDuckGoSearchResults(output_format="list")
    # ddg_search_tool = DuckDuckGoSearchRun()

    print("\n--- DuckDuckGoSearchRun Tool ---")
    tool_result = ddg_search_tool.run("What is the capital of France?")
    print(tool_result)
