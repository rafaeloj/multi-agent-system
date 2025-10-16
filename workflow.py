from graph.node_analyst import node_analyst
from graph.node_critic import node_critic
from graph.node_presenter import node_presenter
from graph.node_researcher import node_researcher
from graph.node_scout import node_scout
from graph.router_scout import router_scout
from graph.state import AgentState
from langgraph.graph import END, StateGraph
from dotenv import load_dotenv
import os

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
workflow.add_edge("critic", "presenter")
workflow.add_edge("presenter", END)
workflow.add_conditional_edges(
    "scout",
    router_scout,
    { "researcher": "researcher", "scout": "scout", "presenter": "presenter" }
)

app = workflow.compile()

def save_graph(graph, xray=False, save_path="./figs/agent_graph.png"):
    try:
        graph_png = graph.get_graph(xray=xray).draw_mermaid_png()
        with open(save_path, "wb") as f:
            f.write(graph_png)
    except Exception as e:
        import nest_asyncio
        nest_asyncio.apply()
        from langchain_core.runnables.graph import MermaidDrawMethod
        graph_png = graph.get_graph().draw_mermaid_png(draw_method=MermaidDrawMethod.PYPPETEER)
        with open(save_path, "wb") as f:
            f.write(graph_png)

if __name__ == "__main__":
    
    initial_state = {
        "summary": "O aprendizado federado (Federated Learning – FL) é uma aborda- gem distribuída para o treinamento colaborativo de modelos de aprendizado de máquina. O FL requer um alto nível de comunicação entre os dispositivos e um servidor central, assim gerando diversos desafios, incluindo gargalos de co- municação e escalabilidade na rede. Neste trabalho, introduzimos DEEV, uma solução para diminuir os custos gerais de comunicação e computação para trei- nar um modelo no ambiente FL. DEEV emprega uma estratégia de seleção de clientes que adapta dinamicamente o número de dispositivos que treinam o mo- delo e o número de rodadas necessárias para atingir a convergência. Um caso de uso no conjunto de dados de reconhecimento de atividades humanas é rea- lizado para avaliar DEEV e compará-lo com outras abordagens do estado da arte. Avaliações experimentais mostram que DEEV reduz eficientemente a so- brecarga geral de comunicação e computação para treinar um modelo e promo- ver sua convergência. Em particular, o DEEV reduz em até 60% a comunicação e em até 90% a sobrecarga de computação em comparação com as abordagens da literatura, ao mesmo tempo em que fornece boa convergência mesmo em ce- nários em que os dados são distribuídos de forma não independente e idêntica entre os dispositivos clientes",
        "keywords": "",
        "search_tries": 0,
        "raw_vanues": "",
        "enriched_venues": "",
        "selected_venues": "",
        "final_decision": "",

    }
    save_graph(app, xray=True, save_path="./figs/agent_graph_xray.png")
    result = app.invoke(initial_state)
    print("Final Result:", result)
    # pritty print the final decision
    print("Final Decision:", result['final_decision'])
    
