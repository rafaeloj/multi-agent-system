from typing import List, TypedDict, Optional

class AgentState(TypedDict):
    summary: str
    keywords: List[str]
    search_tries: int
    raw_vanues: Optional[List[str]]
    enriched_venues: Optional[List[str]]
    selected_venues: Optional[str]
    final_decision: Optional[str]
