ANALYST_PROMPT_TEMPLATE = """You are an experienced researcher. Your task is to analyze an article abstract and extract the 3 most relevant keywords for conference searches.
Respond ONLY with a valid JSON object with the key \"keywords\"

Summary: "{summary}"
"""

PRESENTATION_PROMPT_TEMPLATE_FALLBACK = "You're a helpful research assistant. Write a polite message informing the user that after searching with the keywords {keywords}, no relevant conferences were found."

PRESENTATION_PROMPT_TEMPLATE = """You are a helpful research assistant. Write a final report for the researcher.
The report should be in Markdown format and clearly present the recommended conferences,
including the acronym, full name, deadline, and WikiCFP link.

Recommended Conferences:
{venues}
"""
CRITIC_PROMPT_TEMPLATE = """You are a senior article reviewer. Your task is to analyze an article abstract and a list of conferences. For each conference, a web search was performed, the results of which are listed in "additional_information."
Select the {K} conferences that BEST match the article.

Respond ONLY with a valid JSON object with the key "selected_venues," containing a filtered list.

Article Abstract:
{summary}

List of Conferences Found (with text search results):
{enriched_venues}
"""