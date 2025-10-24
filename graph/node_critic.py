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
         Select the {K} conferences that BEST match the article.
            Article Abstract:
            {summary}

            List of Conferences Found (with text search results):
            {enriched_venues}

            JSON format:
            {{
                keywords: [ "keyword1", "keyword2", ... ],
                "selected_venues": [
                    {{
                        "name": "conference name",
                        "acronym": "conference acronym",
                        "link": 'conference link',
                        "date": 'conference deadline',
                        "location": 'conference location',
                        "conference_topics": Optional[List[str]],
                        "additional_info": Optional[Dict[str, str]]
                    }},
                    ...
                ]
            }}
            
            Respond ONLY with a valid JSON object with the key "selected_venues," containing a filtered list.
        """
    )

    chain = prompt | json_llm | JsonOutputParser()

    result = chain.invoke({
        "summary": state['summary'],
        "enriched_venues": state['enriched_venues'],
        "K": state['K'],
    })
    print(result)
    return {"selected_venues": result['selected_venues'], 'insufficient': False}

# from .state import AgentState
# from langchain_core.prompts import ChatPromptTemplate
# from langchain_core.output_parsers.json import JsonOutputParser
# from langchain_ollama.chat_models import ChatOllama
# from dotenv import load_dotenv
# import os

# load_dotenv()

# def node_critic(state: AgentState):
#     print("Node Critic activated")

#     json_llm = ChatOllama(
#         model = os.environ["CRITIC_LLM"],
#         temperature=0,
#         format='json',
#     )
#     prompt = ChatPromptTemplate.from_template(
#          """You are a senior article reviewer. Your task is to analyze an article abstract and a list of conferences. For each conference, a web search was performed, the results of which are listed in "additional_information."
#          Select the {NK} conferences that BEST match the article.
#             Article Abstract:
#             {summary}

#             List of Conferences Found (with text search results):
#             {enriched_venues}

#             Respond ONLY with a valid JSON object with the key "selected_venues," containing a filtered list.
#         """
#     )

#     chain = prompt | json_llm | JsonOutputParser()

#     result = chain.invoke({
#         "summary": state['summary'],
#         "enriched_venues": state['enriched_venues'],
#         "NK": state['NK'],
#     })
#     # print(result)
#     return {"selected_venues": result['selected_venues']}