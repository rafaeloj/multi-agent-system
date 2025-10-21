# Introdução rápida ao LangGraph

**LangGraph** é uma biblioteca construída sobre o ecossistema do LangChain para criar **fluxos de trabalho baseados em grafos** com LLMs. Em vez de encadear chamadas de maneira linear, você define **nós** (funções/agents/chains) e **arestas** que controlam o fluxo, inclusive com **loops**, **branching** e **memória via estado compartilhado**.

**Por que usar?**
- Modela pipelines de LLMs como um grafo explícito e observável.
- Facilita **orquestração multi‑agente** (cada nó faz uma parte do trabalho).
- Estado tipado/estruturado, o que deixa o debug e a composição mais previsíveis.
- Integra-se ao LangChain (prompts, parsers, tools).

**Como isso aparece neste projeto?**
- Há um **estado** central (`AgentState`) que carrega `summary`, `keywords`, `raw_venues`, etc.
- Os nós representam papéis/etapas: `node_analyst` (extrai keywords), `node_scout` (busca venues), `node_researcher` (enriquece), `node_critic` (seleciona o top‑K) e `node_presenter` (gera o relatório final).
- Um **roteador** simples (`router_scout`) decide o próximo passo conforme o estado.

> Procure pelos pontos onde o estado é atualizado e passado adiante. Isso revela o “fio condutor” do grafo.



# Multi-Agent System - Notebook de Teste

Este notebook demonstra o funcionamento de um sistema multi-agente para análise e seleção de conferências acadêmicas usando LangGraph.

## Visão Geral

O sistema é composto por múltiplos agentes especializados que trabalham em conjunto para:
1. Analisar um resumo científico
2. Extrair palavras-chave relevantes
3. Buscar conferências apropriadas
4. Avaliar as opções encontradas
5. Apresentar uma decisão final fundamentada

## Importação de Dependências

Importamos todos os componentes necessários do sistema:

- **Nós do Grafo**: Cada nó representa um agente especializado
  - `node_analyst`: Analisa o resumo e extrai palavras-chave
  - `node_scout`: Busca conferências relacionadas
  - `node_researcher`: Pesquisa informações detalhadas sobre as conferências
  - `node_critic`: Avalia criticamente as opções encontradas
  - `node_presenter`: Apresenta a decisão final

- **Router**: `router_scout` decide qual caminho seguir após a busca
- **Estado**: `AgentState` mantém o estado compartilhado entre os agentes
- **LangGraph**: Framework para construção do workflow de agentes
- **Utilitários**: Gerenciamento de variáveis de ambiente e formatação

```python
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
from rich.markdown import Markdown
load_dotenv()
```

## Construção do Workflow Multi-Agente

Nesta seção, construímos o grafo de estados que define o fluxo de execução dos agentes:

### Estrutura do Workflow:
1. **analyst** → Ponto de entrada - analisa o resumo científico
2. **scout** → Busca conferências baseadas nas palavras-chave
3. **Decisão condicional**:
   - Se encontrar resultados → **researcher** (pesquisa detalhes)
   - Se não encontrar → **critic** (avalia diretamente)
4. **critic** → Avalia criticamente as opções
5. **presenter** → Apresenta a decisão final

### Fluxo de Dados:
O estado compartilhado (`AgentState`) circula entre os nós, sendo enriquecido a cada etapa:
- Summary → Keywords → Raw Venues → Enriched Venues → Selected Venues → Final Decision

```python
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
    { "researcher": "researcher", "critic": "critic" }
)
app = workflow.compile()
```

## Função de Visualização do Grafo

Esta função auxiliar permite visualizar a estrutura do workflow:

- **Parâmetros**:
  - `graph`: O grafo compilado do LangGraph
  - `xray`: Se True, mostra detalhes internos dos nós
  - `save_path`: Caminho onde salvar a imagem PNG

- **Funcionalidade**:
  - Gera uma representação visual do grafo usando Mermaid
  - Trata exceções aplicando `nest_asyncio` se necessário
  - Salva a imagem no diretório especificado

```python
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
```

## Geração da Visualização (X-Ray)

Salva uma versão detalhada do grafo mostrando a estrutura interna dos nós.

```python
save_graph(app, xray=True, save_path="./figs/agent_graph_xray.png")
```
![GRAPH](https://i.imgur.com/a8lZINj.png)
## Execução do Sistema Multi-Agente

### Estado Inicial:
Definimos o estado inicial com:
- **summary**: Resumo científico sobre Federated Learning e Language Model Agents
- **keywords**: Inicialmente vazio (será preenchido pelo analyst)
- **search_tries**: Contador de tentativas de busca
- **raw_venues**: Conferências brutas encontradas (a preencher)
- **enriched_venues**: Conferências com informações detalhadas (a preencher)
- **selected_venues**: Conferências selecionadas após avaliação (a preencher)
- **final_decision**: Decisão final formatada (a preencher)

### Execução:
O método `app.invoke()` executa todo o workflow, passando o estado por todos os agentes sequencialmente até produzir a decisão final.

```python
initial_state = {
    "summary": "Federated Learning is a powerful machine learning paradigm that enables collaborative training across devices. However, its distributed nature presents problems of systemic and statistical heterogeneity that generate training instability, thus requiring adaptive and dynamic solutions. Therefore, this paper presents the community with a new way to address these problems using language model agents. We demonstrate the reasons why LM agents should be used in FL, their advantages, and research opportunities. We also conduct two experiments to demonstrate the potential of a simple implementation and how it can be enhanced through sophisticated agent techniques.",
    "keywords": "",
    "search_tries": 0,
    "raw_vanues": "",
    "enriched_venues": "",
    "selected_venues": "",
    "final_decision": "",

}
result = app.invoke(initial_state)

```


# Arquivos de código (.py)
Os arquivos que foram utilizados durante a importação

## router_scout.py


```python
from .state import AgentState
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers.json import JsonOutputParser
from langchain_ollama.chat_models import ChatOllama
from dotenv import load_dotenv
import os


def router_scout(state: AgentState):
    print("Router Scout activated")
    raw_venues = state['raw_vanues']
    if raw_venues and raw_venues != "[]":
        print("Decision: Success! Send to Node Researcher")
        return "researcher"
    
    # if state["search_tries"] < len(state["keywords"]):
        # print("Decision: No relevant conferences found. Send to Node Scout")
        # return "scout"
    
    print("Decision: Max search tries reached. Send to Node Presenter")
    return "critic"
```

## prompts.py


```python
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
```

## node_critic.py


```python
from .state import AgentState
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers.json import JsonOutputParser
from langchain_ollama.chat_models import ChatOllama
from dotenv import load_dotenv
from .prompts import CRITIC_PROMPT_TEMPLATE
import os

load_dotenv()

def node_critic(state: AgentState):
    print("Node Critic activated")

    json_llm = ChatOllama(
        model = os.environ["CRITIC_LLM"],
        temperature=0,
        format='json',
    )
    prompt = ChatPromptTemplate.from_template(CRITIC_PROMPT_TEMPLATE)

    chain = prompt | json_llm | JsonOutputParser()

    if 'enriched_venues' not in state:
        print("Enriching venues for the first time")
        state['enriched_venues'] = state['raw_venues']

    result = chain.invoke({
        "summary": state['summary'],
        "enriched_venues": state['enriched_venues'],
        "K": 3, # numero de keywords
    })
    print(result)
    return {"selected_venues": result['selected_venues']}
```

## node_presenter.py


```python
from .state import AgentState
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers.json import JsonOutputParser
from langchain_ollama.chat_models import ChatOllama
from dotenv import load_dotenv
from .prompts import PRESENTATION_PROMPT_TEMPLATE, PRESENTATION_PROMPT_TEMPLATE_FALLBACK
import os

load_dotenv()

def node_presenter(state: AgentState):
    print("Node Presenter activated")

    selected_venues = state['selected_venues']
    text_llm = ChatOllama(
        model = os.environ.get("PRESENTER_LLM"),
        temperature=0.2,
    )
    if not selected_venues or selected_venues == "[]":
        print("No venues were selected.")
        prompt = PRESENTATION_PROMPT_TEMPLATE_FALLBACK
        prompt = ChatPromptTemplate.from_template(prompt)
        chain = prompt | text_llm
        response = chain.invoke({
            "keywords": state['keywords']
        })
        print("Final decision generated.")
        return {"final_decision": response.content}
    
    print("Selected venues:")
    for venue in selected_venues:
        print(f"- {venue}")
    
    prompt = PRESENTATION_PROMPT_TEMPLATE
    prompt = ChatPromptTemplate.from_template(prompt)
    chain = prompt | text_llm
    response = chain.invoke({
        "venues": selected_venues,
    })
    return{"final_decision": response.content}
```

## node_analyst.py


```python
from .state import AgentState
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers.json import JsonOutputParser
from langchain_ollama.chat_models import ChatOllama
from dotenv import load_dotenv
import os
from .prompts import ANALYST_PROMPT_TEMPLATE

load_dotenv()

def node_analyst(state: AgentState):
    print("Node Analyst activated")
    json_llm = ChatOllama(
        model = os.environ.get("ANALYST_LLM"),
        temperature=0.1,
        format='json',
    )
    prompt = ChatPromptTemplate.from_template(ANALYST_PROMPT_TEMPLATE)
    chain = prompt | json_llm | JsonOutputParser()
    result = chain.invoke({
        "summary": state['summary'],
    })
    print("Node Analyst result:", result)
    return {"keywords": result['keywords'], "search_tries": 0}
```

## node_scout.py


```python
from .state import AgentState
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers.json import JsonOutputParser
from langchain_ollama.chat_models import ChatOllama
from tools import search_wikicfp_tool

def node_scout(state: AgentState):
    print("Node Scout activated")

    tries = state['search_tries']
    keywords = state['keywords']
    current_keyword = keywords[tries]

    print(f"Searching conferences with keyword: {current_keyword}")
    venues = []
    for keyword in keywords:
        print(f"- {keyword}")
        venues.extend(search_wikicfp_tool(query=keyword))
    
    return {
        "raw_venues": venues,
        "search_tries": tries + 1
    }

if __name__ == "__main__":
    node_scout({'search_tries': 0, 'keywords': ['machine learning', 'artificial intelligence']})
```

## state.py


```python
from typing import List, TypedDict, Optional

class AgentState(TypedDict):
    summary: str
    keywords: List[str]
    search_tries: int
    raw_vanues: Optional[List[str]]
    enriched_venues: Optional[List[str]]
    selected_venues: Optional[str]
    final_decision: Optional[str]
```

## node_researcher.py


```python
from .state import AgentState
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers.json import JsonOutputParser
from langchain_ollama.chat_models import ChatOllama
from tools import search_wikicfp_tool
from langchain_community.tools import DuckDuckGoSearchResults
import json

def node_researcher(state: AgentState):
    print('Node Researcher activated')
    vanues_list = json.loads(state['raw_vanues'])
    if not vanues_list:
        return {"enriched_venues": []}
    ddg_search_tool = DuckDuckGoSearchResults(output_format="list")
    enriched = []
    for venue in vanues_list:
        query = f"official website and main topics of the conference {venue['full_name']} in {venue['deadline']}"
        search_results = ddg_search_tool.run(query)

        venue['additional_info'] = search_results
        enriched.append(venue)
    print("Enrichment completed.")
    print("Enriched venues:", enriched)
    return {"enriched_venues": enriched}
```
