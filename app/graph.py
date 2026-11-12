from langgraph.graph import StateGraph, START, END
from app.state import AgentState
from app.nodes import (
    plan_node, 
    search_node, 
    write_node, 
    critic_node, 
    bump_retry_node
)

# 1. Define a routing function
def should_continue(state: AgentState) -> str:
    critique = state.get("critique", {})
    retry_count = state.get("retry_count", 0)
    max_retries = state.get("max_retries", 2)
    
    passed = critique.get("pass", False)
    
    # If it passed, we are done
    if passed:
        print("[graph] Critic passed. Finishing.")
        return "end"
        
    # If it failed but we hit the max retries, give up and finish
    if retry_count >= max_retries:
        print("[graph] Max retries reached. Finishing anyway.")
        return "end"
        
    # Otherwise, we need to retry
    print(f"[graph] Critic failed. Retrying (Attempt {retry_count + 1}/{max_retries})...")
    return "retry"

def build_graph():
    builder = StateGraph(AgentState)

    # 2. Add all nodes
    builder.add_node("plan", plan_node)
    builder.add_node("search", search_node)
    builder.add_node("write", write_node)
    builder.add_node("critic", critic_node)
    builder.add_node("bump_retry", bump_retry_node) 

    # 3. Add the edges
    builder.add_edge(START, "plan")
    builder.add_edge("plan", "search")
    builder.add_edge("search", "write")
    builder.add_edge("write", "critic")
    
    # 4. Add the conditional edge
    builder.add_conditional_edges(
        "critic",
        should_continue,  # <--- This is where the error was happening
        {
            "end": END,
            "retry": "bump_retry"
        }
    )
    
    # 5. Add the edge from bump_retry back to plan
    builder.add_edge("bump_retry", "plan") 

    return builder.compile()