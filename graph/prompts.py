ANALYST_PLAN_TEMPLATE = """
# Name: {agent_name}
# Role: {agent_role}

# Task: Develop Keyword Extraction Plan

## Plan Objective
Your goal is to devise a step-by-step plan for extracting conceptual keywords from a given academic text.

## Core Strategy
The central principle of this plan is to differentiate between two levels of abstraction for keywords:
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

Paper abstract for Analysis:
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

