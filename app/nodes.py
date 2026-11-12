# from app.state import AgentState

# def plan_node(state: AgentState) -> dict:
#     print("[plan] received question:", state["question"])
#     # Fake sub-questions for now
#     return {
#         "sub_questions": [
#             "fake sub-question 1",
#             "fake sub-question 2",
#         ]
#     }

# def search_node(state: AgentState) -> dict:
#     print("[search] sub-questions:", state["sub_questions"])
#     # Fake evidence for now
#     return {
#         "evidence": [
#             {"title": "Fake Paper 1", "abstract": "Fake abstract 1.", "url": "http://x/1"},
#             {"title": "Fake Paper 2", "abstract": "Fake abstract 2.", "url": "http://x/2"},
#         ]
#     }

# def write_node(state: AgentState) -> dict:
#     print("[write] evidence count:", len(state["evidence"]))
#     return {
#         "draft": "This is a fake draft referencing [1] and [2]."
#     }

import json
from groq import Groq
from app.state import AgentState
from app.tools.arxiv_tool import search_arxiv
from dotenv import load_dotenv
load_dotenv()



# 1. Initialize the Groq client globally so we don't recreate it every time
client = Groq()
MODEL = "openai/gpt-oss-120b"

def plan_node(state: AgentState) -> dict:
    print("\n[plan] Thinking...")
    question = state["question"]
    feedback = state.get("critique_feedback", "")
    
    # If we have feedback from a previous failure, inject it into the prompt
    feedback_text = f"\nPrevious attempt failed for these reasons: {feedback}\nAdjust your sub-questions to fix this." if feedback else ""

    prompt = f"""
    You are a research planning assistant. 
    Break the following research question into 2 to 3 specific sub-questions that can be searched on arXiv.
    {feedback_text}
    
    Question: {question}
    
    Return ONLY a valid JSON object with a single key "sub_questions" containing a list of strings.
    Example format:
    {{"sub_questions": ["sub-question 1", "sub-question 2"]}}
    """

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0,
            response_format={"type": "json_object"}
        )
        
        content = response.choices[0].message.content
        data = json.loads(content)
        sub_questions = data.get("sub_questions", [])
        
        print(f"[plan] Generated sub-questions: {sub_questions}")
        return {"sub_questions": sub_questions}

    except Exception as e:
        print(f"[plan] ERROR: {e}")
        return {"sub_questions": [question]}
def search_node(state: AgentState) -> dict:
    print("\n[search] Searching arXiv...")
    sub_questions = state.get("sub_questions", [])
    all_evidence = []

    # 4. Loop through the sub-questions and call the tool
    for sq in sub_questions:
        papers = search_arxiv(sq, max_results=2) # Get top 2 papers per sub-question
        all_evidence.extend(papers)

    # 5. Deduplicate papers based on URL (since multiple searches might return the same paper)
    unique_evidence = []
    seen_urls = set()
    for paper in all_evidence:
        if paper["url"] not in seen_urls:
            seen_urls.add(paper["url"])
            unique_evidence.append(paper)

    print(f"[search] Found {len(unique_evidence)} unique papers.")
    return {"evidence": unique_evidence}


def write_node(state: AgentState) -> dict:
    print("\n[write] Writing final answer...")
    question = state["question"]
    evidence = state.get("evidence", [])

    if not evidence:
        return {"draft": "I could not find any relevant papers on arXiv to answer this question."}

    # 6. Format the evidence so the LLM can easily read it
    context = ""
    for i, paper in enumerate(evidence):
        context += f"[{i+1}] Title: {paper['title']}\nAbstract: {paper['abstract']}\n\n"

    prompt = f"""
    You are an expert researcher. Answer the following question using ONLY the provided context.
    Use inline citations like [1], [2] that correspond to the paper numbers provided.
    If the context doesn't contain the answer, say so.
    
    Question: {question}
    
    Context:
    {context}
    
    Draft your answer:
    """

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2 # Slightly higher temperature for better writing flow
        )
        draft = response.choices[0].message.content
        print("[write] Draft generated.")
        return {"draft": draft}

    except Exception as e:
        print(f"[write] ERROR: {e}")
        return {"draft": "Failed to generate an answer due to an LLM error."}

def critic_node(state: AgentState) -> dict:
    print("\n[critic] Evaluating draft...")
    question = state["question"]
    draft = state.get("draft", "")
    evidence = state.get("evidence", [])
    
    # Format evidence just like we did in write_node
    context = ""
    for i, paper in enumerate(evidence):
        context += f"[{i+1}] {paper['title']}: {paper['abstract']}\n"
        
    prompt = f"""
    You are a strict research critic. Evaluate the draft answer below.
    
    Question: {question}
    Evidence: {context}
    Draft: {draft}
    
    Check two things:
    1. Does the draft directly answer the question?
    2. Is every claim in the draft supported by the numbered evidence?
    
    If the draft is good, return JSON: {{"pass": true, "reasons": []}}
    If the draft is bad or missing information, return JSON: {{"pass": false, "reasons": ["Reason 1", "Reason 2"]}}
    """
    
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0,
            response_format={"type": "json_object"}
        )
        
        content = response.choices[0].message.content
        data = json.loads(content)
        
        passed = data.get("pass", False)
        # passed = False # FORCE FAILURE FOR TESTING
        reasons = data.get("reasons", [])
        if reasons:
            print(f"[critic] Real critique: {reasons}")

        
        print(f"[critic] Passed? {passed}")
        if not passed:
            print(f"[critic] Reasons: {reasons}")
            
        return {
            "critique": {"pass": passed, "reasons": reasons},
            "critique_feedback": " ".join(reasons) if reasons else ""
        }
        
    except Exception as e:
        print(f"[critic] ERROR: {e}")
        # If the critic fails, let's just pass it so we don't get stuck in a loop
        return {"critique": {"pass": True, "reasons": []}, "critique_feedback": ""}

def bump_retry_node(state: AgentState) -> dict:
    current = state.get("retry_count", 0)
    return {"retry_count": current + 1}