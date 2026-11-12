import json
from app.graph import build_graph
from app.state import AgentState
from dotenv import load_dotenv
load_dotenv()

import json
from app.graph import build_graph
# 1. Our "Golden Dataset"
# We define a few questions and what a successful run should look like.
EVAL_QUESTIONS = [
    {
        "question": "What are recent methods to reduce hallucination in LLMs?",
        "expected_keywords": ["RAG", "fine-tuning", "hallucination"] # The draft should mention these
    },
    {
        "question": "How does Retrieval-Augmented Generation work?",
        "expected_keywords": ["retrieval", "generation", "external", "context"]
    },
    {
        "question": "What is the purpose of the THaMES framework?",
        "expected_keywords": ["evaluation", "mitigation", "pipeline", "THaMES"]
    }
]

def run_evaluation():
    graph = build_graph()
    results = []
    
    print("="*50)
    print("STARTING EVALUATION HARNESS")
    print("="*50)
    
    for i, item in enumerate(EVAL_QUESTIONS):
        print(f"\n--- Test Case {i+1}: {item['question']} ---")
        
        initial_state = {
            "question": item["question"],
            "retry_count": 0,
            "max_retries": 1, # Keep it fast for evaluation
        }
        
        # Run the graph
        final_state = graph.invoke(initial_state)
        draft = final_state.get("draft", "").lower()
        
        # 2. Programmatic Scoring
        # Check if the expected keywords actually appear in the final draft
        passed_keywords = []
        failed_keywords = []
        for kw in item["expected_keywords"]:
            if kw.lower() in draft:
                passed_keywords.append(kw)
            else:
                failed_keywords.append(kw)
                
        # 3. Determine Test Pass/Fail
        # Let's say a test passes if it hits at least 2 of the expected keywords
        keyword_score = len(passed_keywords) / len(item["expected_keywords"])
        test_passed = keyword_score >= 0.5 
        
        results.append({
            "question": item["question"],
            "test_passed": test_passed,
            "keyword_score": f"{keyword_score * 100:.0f}%",
            "missing_keywords": failed_keywords
        })
        
    # 4. Print the Report
    print("\n" + "="*50)
    print("EVALUATION REPORT")
    print("="*50)
    
    total_passed = sum(1 for r in results if r["test_passed"])
    print(f"Total Score: {total_passed}/{len(EVAL_QUESTIONS)} tests passed.\n")
    
    for r in results:
        status = "✅ PASS" if r["test_passed"] else "❌ FAIL"
        print(f"{status} | {r['question']}")
        print(f"      Keyword Coverage: {r['keyword_score']}")
        if r["missing_keywords"]:
            print(f"      Missing expected concepts: {r['missing_keywords']}")
        print()

if __name__ == "__main__":
    run_evaluation()