import os
from .state import AgentState
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers.json import JsonOutputParser
from langchain_ollama.chat_models import ChatOllama
from tools import get_url_content
from .agent import Agent
from .prompts import RESEARCHER_JSON_TEMPLATE, RESEARCHER_PLAN_TEMPLATE, RESEARCHER_REASONING_TEMPLATE
from langchain_community.tools import DuckDuckGoSearchResults
import json

def node_researcher(state: AgentState):
    print('Node Researcher activated')
    venues_list = state['raw_venues']
    if not venues_list:
        return {"enriched_venues": []}
    ddg_search_tool = DuckDuckGoSearchResults(output_format="list")
    enriched = []
    for venue in venues_list:
        query = f"official website and main topics of the conference {venue['full_name']} in {venue['deadline']}"
        try:
            search_results = ddg_search_tool.run(query)
        except Exception as e:
            search_results = f"No additional information found for {venue['full_name']}"
        venue['additional_info'] = search_results
        enriched.append(venue)
    
    planner_llm = ChatOllama(
        model=os.environ["RESEARCHER_LLM"],
        temperature=0.2,
    )

    researcher_agent = Agent(
        name="Researcher",
        role="Conference Matching Researcher",
        llm=planner_llm,
        plan_template=RESEARCHER_PLAN_TEMPLATE,
        reasoning_template=RESEARCHER_REASONING_TEMPLATE,
    )

    json_llm = ChatOllama(
        model=os.environ.get("RESEARCHER_LLM"),
        temperature=0,
        format='json',
    )

    prompt = ChatPromptTemplate.from_template(RESEARCHER_JSON_TEMPLATE)

    chain = prompt | json_llm | JsonOutputParser()

    links = [venue['link'] for venue in enriched]

    print("Fetching contents from conference links...")
    contents = get_url_content(links)

    print("Processing each venue for enrichment...")
    for i, venue in enumerate(enriched[:5]):
        print(f"Enriching venue: {venue['full_name']}")
        content = contents[i]
        print("Researcher planning...")
        _ = researcher_agent.plan({"content": content})
        print("Researcher reasoning...")
        _ = researcher_agent.reason({"content": content, "additional_info": venue['additional_info']})

        result = chain.invoke({
            "content": content,
            "plan": researcher_agent._last_plan,
            "reasoning": researcher_agent._last_reasoning,
        })
        print(result)
        venue['conference_topics'] = result.get('conference_topics', {})

    logs = state['agent_logs']
    logs["researcher"] = researcher_agent.snapshot()

    print("Enrichment completed.")
    print("Enriched venues:", enriched)
    return {
        "enriched_venues": enriched,
        "agent_logs": logs
    }