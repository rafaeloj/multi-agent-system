from typing import Dict, List, Optional, TypedDict

class Vanue(TypedDict):
    name: str
    link: str
    date: str
    location: str
    conference_topics: Optional[List[str]]
    additional_info: Optional[Dict[str, str]]

class AgentState(TypedDict):
    summary: str
    NK: int
    keywords: List[str]
    search_tries: int
    raw_venues: Optional[List[Vanue]]
    enriched_venues: Optional[List[Vanue]]
    selected_venues: Optional[List[Vanue]]
    final_decision: Optional[str]
    agent_logs: Optional[Dict[str, Dict[str, str]]]

class AnalystState(TypedDict, total=False):
    summary: str
    iteration: int
    max_iterations: int
    plan: str
    plan_log: List[str]
    reasoning: str
    reasoning_log: List[str]
    keywords: List[str]
    satisfied: bool

class CriticState(TypedDict):
    summary: str
    enriched_venues: List[Vanue]
    NK: int
    selected_venues: Optional[List[Vanue]]