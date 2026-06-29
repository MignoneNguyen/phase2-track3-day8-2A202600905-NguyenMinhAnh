import os
import sqlite3
from dotenv import load_dotenv

load_dotenv()
os.environ["LANGGRAPH_INTERRUPT"] = "true"

from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph_agent_lab.graph import build_graph

def run():
    # 1. Setup DB (using an in-memory DB for quick testing, but perfectly valid for persistence)
    conn = sqlite3.connect(":memory:", check_same_thread=False)
    checkpointer = SqliteSaver(conn)
    graph = build_graph(checkpointer=checkpointer)
    
    config = {"configurable": {"thread_id": "test_crash_resume_1"}}
    initial_state = {
        "query": "Cancel my entire account right now", 
        "attempt": 0,
        "events": [], 
        "tool_results": [], 
        "errors": []
    }
    
    print("--- FIRST RUN: Triggering risky action (expects HITL interrupt) ---")
    # This will run until it hits the interrupt in approval_node
    graph.invoke(initial_state, config)
        
    current_state = graph.get_state(config)
    print(f"State paused. Next node to run: {current_state.next}")
    print("Simulating application crash...")
    
    print("\n--- SECOND RUN: Resuming from persisted checkpoint ---")
    # In a real app, this would be a brand new process connecting to the DB
    # Provide the mock approval decision to the interrupted node
    graph.update_state(config, {"approval": {"approved": True, "reviewer": "admin"}}, as_node="approval")
    
    # Resume the graph
    final_state = graph.invoke(None, config)
    
    print("Graph execution resumed and completed successfully!")
    print(f"Final Answer generated: {final_state.get('final_answer')}")

if __name__ == '__main__':
    run()
