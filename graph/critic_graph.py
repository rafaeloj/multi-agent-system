# import .state import AgentState
# from langchain_core.prompts import ChatPromptTemplate
# from langchain_core.output_parsers.json import JsonOutputParser
# from langchain_ollama.chat_models import ChatOllama
# from .prompts import CRITIC_PLAN_TEMPLATE, CRITIC_REASONING_TEMPLATE
# from .state import CriticState
# from .agent import Agent
# from dotenv import load_dotenv
# import os
# load_dotenv()

# def build_critic_agent():
#     critic_mode = 'CRITIC_LLM'
#     critic_llm = ChatOllama(model = os.environ[critic_mode], temperature = 0.2)
#     critic_agent = Agent(
#         name = "Critic",
#         role = "Conference matching critic",
#         llm = critic_llm,
#         plan_template = CRITIC_PLAN_TEMPLATE,
#         reasoning_template = CRITIC_REASONING_TEMPLATE,
#     )

#     json_model = "JSON_LLM"
#     json_llm = ChatOllama(
#         model = os.environ[json_model],
#         temperature = 0,
#         format='json',
#     )
#     def planning_node(state: CriticState) -> CriticState:

