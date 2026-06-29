import os
from langgraph_agent_lab.graph import build_graph

def export_diagram():
    graph = build_graph()
    try:
        mermaid_png = graph.get_graph().draw_mermaid_png()
        os.makedirs("outputs", exist_ok=True)
        with open("outputs/graph_diagram.png", "wb") as f:
            f.write(mermaid_png)
    except Exception as e:
        print(f"Failed to generate PNG (requires some extra deps): {e}")
        
    mermaid_txt = graph.get_graph().draw_mermaid()
    os.makedirs("outputs", exist_ok=True)
    with open("outputs/graph_diagram.md", "w") as f:
        f.write("```mermaid\n" + mermaid_txt + "\n```")
    print("Graph diagram exported to outputs/graph_diagram.md")

if __name__ == "__main__":
    export_diagram()
