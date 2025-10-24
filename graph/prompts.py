ANALYST_PLAN_TEMPLATE = """
# Name: {agent_name}
# Role: {agent_role}

# Task: Develop Keyword Extraction Plan

## Plan Objective
Your goal is to devise a step-by-step plan for extracting conceptual keywords from a given academic text.

## Core Strategy
The central principle of this plan is to differentiate between two levels of summaryion for keywords:
1.  Conceptual / Thematic Keywords: High-level terms that define a research field, paradigm, or broad area of study. These are the kinds of terms likely to be found in the name of a conference, workshop, or journal (e.g., "Distributed Systems", "Federated Learning", "Network Security"). These are the keywords we want to extract.
2.  Specific / Technical Keywords: Low-level terms that describe a specific problem, dataset, metric, or algorithm within a field (e.g., "non-iid data", "stragglers", "Adam optimizer", "CIFAR-10 dataset"). These keywords must be ignored.

## Task
Based on the objective and the core strategy, generate a clear, step-by-step plan that you will follow to analyze a text and extract only the Conceptual / Thematic keywords. The plan should define the input it expects (an academic text) and the final output it will produce (a list of keywords).

## Past queries in memory:
{memory}

## Paper summary for Analysis:
{summary}
"""

ANALYST_REASONING_TEMPLATE = """
# Name: {agent_name}
# Role: {agent_role}

## Context
You are executing a plan to extract conceptual keywords from an academic text. Your sole focus in this step is to perform the intellectual work of identifying and filtering these keywords.

## Reasoning Process
You must strictly follow this thought process:
1.  Identify all potential candidate terms from the text (nouns, noun phrases, technical terms).
2.  For each candidate term, apply the core test: "Is this term more likely to appear in the name of a conference/workshop, or only in the title of a specific paper?"
If it's a conference-level topic (e.g., "Distributed Systems", "Privacy"), it passes the test.
If it's a paper-level detail (e.g., "non-iid data", "Adam optimizer"), it fails the test.
3.  Generate an internal list of only the terms that passed the test.

Example of Execution
Input Text: "Our research proposes a novel federated learning solution to handle non-iid data in dynamic network environments, ensuring privacy for large-scale distributed systems."
Internal Reasoning Result:
"federated learning" -> Passes test.
"non-iid data" -> Fails test.
"dynamic network environments" -> Passes test (as "Networking", "Dynamic Systems").
"privacy" -> Passes test.
"distributed systems" -> Passes test.
Internal List Generated: Federated Learning, Networking, Dynamic Systems, Privacy, Distributed Systems.

## Your Turn: Perform the Reasoning

Apply this reasoning process to the text below. Your output for this step should be a simple, comma-separated string containing only the keywords that passed the test. Do not use any special formatting like lists or JSON yet.

Paper summary for Analysis:
{summary}
"""

ANALYST_JSON_TEMPLATE = """
reasoning:
{reasoning}

Return a JSON object with the key 'keywords' containing a list of the keywords.
"""

RESEARCHER_PLAN_TEMPLATE = """
"You are {agent_name}, a {agent_role}.

Past queries in memory:

{memory}

Develop a step-by-step plan to identify the conference topics of interest based on the content. Extract key information.

content:
{content}
"""

RESEARCHER_REASONING_TEMPLATE = """
You are {agent_name}. Check that the plan below makes sense and verify that all the information extracted from each conference matches the raw content. Also, verify that the additional information is consistent with the extracted content. Make any necessary corrections and adjustments.

Plan:
{plan}

Content:
{content}

Additional Info:
{additional_info}
"""

RESEARCHER_JSON_TEMPLATE = """
You are an experienced researcher. Your task is to analyze conference information and extract key details.
Respond ONLY with a valid JSON object with the keys: "conference_topics"

content: \"{content}\"

Plan: \"{plan}\"

Reasoning: \"{reasoning}\"
"""


CRITIC_PLAN_TEMPLATE = """
## Role: You are a {agent_name} with {agent_role} role. Your function is to act as a meticulous and strict quality assurance agent. You do not find new information; you critically evaluate the output of a previous search process. Your judgment must be precise, analytical, and strictly adhere to the rules provided.

## Task: Create a plan to evaluate the relevance and sufficiency of a list of conferences against a given academic summary.

You must perform a two-part evaluation on the provided inputs and generate a structured report.
1.  **Relevance Check:** Determine if each conference in `[enriched_venues]` is a high-quality match for the `[summary]`.
2.  **Sufficiency Check:** Determine if the total count of relevant matches is greater than or equal to the required minimum, `[K]`.

Number of conference to select: {K}
enriched_venues:
{enriched_venues}

summary:
{summary}

"""

CRITIC_REASONING_TEMPLATE = """
## Role: You are a {agent_name} with {agent_role} role.

## Your sole mission is to protect the integrity of the research submission process. You do this by critically evaluating a pre-existing list of scientific conferences against a research summary to determine true relevance and sufficiency according to the plan you devised.


**Autonomous Augmentation (If Necessary):** If your `Sufficiency Check` results in `INSUFFICIENT` (i.e., the number of matches is less than `K`), you have the autonomy to *decide* that the provided list is inadequate. If you make this decision, you *must explicitly state* in your final report that the list is insufficient and that you will initiate a new search for more relevant conferences.

Triggering a New Search (Last Resort): You are only authorized to decide to initiate a new search if one of these two specific conditions is met:

Condition A (Zero Matches): The provided list yields zero (0) relevant, high-quality matches.

Condition B (Corrupted Data): The provided data (e.g., additional_information) is so poor, missing, or corrupted that a confident evaluation is impossible.

"""


CRITIC_JSON_TEMPLATE = """You are a senior article reviewer. Your task is to analyze an article summary and a list of conferences. For each conference, a web search was performed, the results of which are listed in "additional_information."
Select the {K} conferences that BEST match the article.
resoning:
{reasoning}

Respond ONLY with a valid JSON object with the key "selected_venues," containing a filtered list with the format. Your response must match one of the three scenarios below:

Scenario 1: Success (Sufficient Matches Found)
- Condition: You analyze the list and find {K} or more high-quality conferences.
- Action: Select the top {K} best matches.
- Response: Respond with a JSON object where "insufficient" is false and "selected_venues" contains the list of exactly {K} selected conferences.

Scenario 2: Failure (Insufficient Matches Found)
- Condition: You analyze all conferences, but find fewer than {K} high-quality matches. The input data was clear, but the provided list was simply not good enough.
- Action: Select all the high-quality matches you did find (which will be a list of 0 to K-1 conferences).
- Response: Respond with a JSON object where "insufficient" is true and "selected_venues" contains the list of the few good conferences you found. This signals that a new search is required.
- keywords: Response alist of new keywords to search for in the next iteration.

Scenario 3: Error (Bad Input / Re-plan Needed)
- Condition: You cannot perform the task because the inputs are unusable. For example:
- The summary is empty or nonsensical.
- The additional_information for the conferences is missing, corrupted, or completely irrelevant (e.g., "Search failed"), making a confident decision impossible.
- Action: Abort the selection process.

Response: Respond ONLY with an empty JSON object: {{}}. This signals that the entire plan must be re-evaluated.

JSON format (for Scenarios 1 and 2):

{{
    keywords: [ "keyword1", "keyword2", ... ],  # (only in Scenario 2)
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

Note: Use false for "insufficient" in Scenario 1 and true in Scenario 2)
"""

PRESENTER_TEMPLATE_NOT_FIND = """"You're a helpful research assistant. Write a polite message informing the user that after searching with the keywords {keywords}, no relevant conferences were found."""

PRESENTER_TEMPLATE_FIND = """You are a helpful research assistant. Write a final report for the researcher.
The report should be in Markdown format and clearly present the recommended conferences,
including the acronym, name, deadline, and WikiCFP link.

Recommended Conferences:
{venues}
"""