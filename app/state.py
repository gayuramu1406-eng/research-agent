from typing import TypedDict, List, Dict, Any

class AgentState(TypedDict, total=False):
    # 1. Input
    question: str

    # 2. Planner output
    sub_questions: List[str]

    # 3. Search output
    evidence: List[Dict[str, Any]]

    # 4. Writer output
    draft: str


    # 5. Critic output
    critique: Dict[str, Any]
    critique_feedback: str  # <--- ADD THIS LINE

    # 6. Loop control
    retry_count: int
    max_retries: int