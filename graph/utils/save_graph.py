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