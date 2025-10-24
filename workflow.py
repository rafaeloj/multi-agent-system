from graph.router_critic import router_critic
from graph.node_analyst import node_analyst
from graph.node_critic import node_critic
from graph.node_presenter import node_presenter
from graph.node_researcher import node_researcher
from graph.node_scout import node_scout
from graph.router_scout import router_scout
from graph.state import AgentState
from langgraph.graph import END, StateGraph
from dotenv import load_dotenv
from graph.utils import save_graph
import argparse
import json
import pandas as pd
load_dotenv()

workflow = StateGraph(AgentState)
workflow.add_node("analyst", node_analyst)
workflow.add_node("scout", node_scout)
workflow.add_node("researcher", node_researcher)
workflow.add_node("critic", node_critic)
workflow.add_node("presenter", node_presenter)
workflow.set_entry_point("analyst")
workflow.add_edge("analyst", "scout")
workflow.add_edge("researcher", "critic")
# workflow.add_edge("critic", "presenter")
workflow.add_edge("presenter", END)
workflow.add_conditional_edges(
    "scout",
    router_scout,
    { "researcher": "researcher", "presenter": "presenter" }
)
workflow.add_conditional_edges(
    "critic",
    router_critic,
    { "scout": "scout", 'presenter': 'presenter' }
)

app = workflow.compile()

def argparser():
    parser = argparse.ArgumentParser(description="Multi-Agent Conference Finder")
    parser.add_argument("--filename", "-f", help="Output filename", type=str, default="output.txt")
    return parser

def read_data(filename):
    df = pd.read_csv(filename)
    return df

if __name__ == "__main__":
    BASE_PATH= "./output"
    args = argparser().parse_args()
    df = read_data("summaries.csv")
    # df = df.iloc[[0]]
    fails = 0
    papers_fails = []
    for i, row in enumerate(df.itertuples()):
        # if i == 2:
        #     break
        print("Processing summary:", row.summary)
        print("-----")
        print(row.Index)
        print()
        initial_state = {
            "summary": row.summary,
            "keywords": "",
            "search_tries": 0,
            "raw_venues": "",
            "enriched_venues": "",
            "selected_venues": "",
            "final_decision": "",
            "K": 10,
        }
        try:
            result = app.invoke(initial_state)
        except Exception as e:
            print("Error processing summary:", e)
            papers_fails.append(row.Index)
            fails += 1
            continue
        paperName = row.paperName.replace(' ', '_')
        with open(f"{BASE_PATH}/output_{paperName}.json", "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"Saved result to output_{paperName}.json")
        print("Final Decision:", result['final_decision'])
    print(f"Processing completed with {fails} failures.")
    with open(f"{BASE_PATH}/fails.txt", "w") as f:
        for item in papers_fails:
            f.write(f"{item}\n")

    # initial_state = {
    #     "summary": args.summary,
    #     "keywords": "",
    #     "search_tries": 0,
    #     "raw_venues": "",
    #     "enriched_venues": "",
    #     "selected_venues": "",
    #     "final_decision": "",

    # }
    # save_graph(app, xray=True, save_path="./figs/agent_graph_xray.png")
    # result = app.invoke(initial_state)
    # with open(args.filename, "w", encoding="utf-8") as f:
    #     json.dump(result, f, ensure_ascii=False, indent=2)
    # print(f"Saved result to {args.filename}")
    # # pritty print the final decision
    # print("Final Decision:", result['final_decision'])
    
