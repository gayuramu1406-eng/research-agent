from dotenv import load_dotenv
load_dotenv()

from app.graph import build_graph

def main():
    # 1. Build the graph
    graph = build_graph()

    # 2. Define the initial state
    initial_state = {
        "question": "What are recent methods to reduce hallucination in LLMs?",
        "retry_count": 0,
        "max_retries": 2,
    }

    print("--- STARTING GRAPH ---")
    
    # 3. Run the graph
    result = graph.invoke(initial_state)

    print("\n--- FINAL STATE ---")
    for key, value in result.items():
        print(f"{key}: {value}")

if __name__ == "__main__":
    main()