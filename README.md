# Autonomous Research Agent

An AI-powered research agent that takes a broad question, searches academic literature (arXiv), synthesizes findings, and self-critiques its own work before delivering a cited answer.

## 🏗️ Architecture

This agent is built as a stateful graph using **LangGraph**. It is not a simple chain; it uses a bounded retry loop to improve its output.

graph TD
    START --> Plan
    Plan --> Search[Search arXiv]
    Search --> Write[Write Draft]
    Write --> Critic[Critique Draft]
    Critic -->|Pass| END
    Critic -->|Fail| BumpRetry[Bump Retry Count]
    BumpRetry -->|retry_count < max| Plan
    BumpRetry -->|retry_count >= max| END


## 🛠️ Tech Stack
- **Framework:** LangGraph (Stateful Agent Workflows)
- **LLM:** Groq (`openai/gpt-oss-120b`)
- **Tools:** `arxiv` Python API
- **Environment:** Python 3.14, `python-dotenv`

## 🚀 Key Engineering Decisions

- **Structured Outputs:** The Planner and Critic use JSON formatting to guarantee valid parsing.
- **Graceful Degradation:** If the arXiv API fails, the tool catches the error and returns an empty list rather than crashing the graph.
- **Bounded Loops:** The Critic can reject a draft, but the graph enforces a `max_retries` limit to prevent infinite API costs.
- **Deduplication:** The search node normalizes URLs to ensure the same paper isn't sent to the LLM multiple times.

## 📊 Evaluation

We built an evaluation harness (`eval.py`) with a 3-question "golden dataset" to programmatically score the agent's outputs against expected keywords.

**Results:** 2/3 Tests Passed (67% Success Rate)
- ✅ *What are recent methods to reduce hallucination in LLMs?* (Hit 67% of expected keywords)
- ✅ *How does Retrieval-Augmented Generation work?* (Hit 100% of expected keywords)
- ❌ *What is the purpose of the THaMES framework?* (Failed - arXiv API could not retrieve the specific acronym. The Critic correctly flagged the hallucination and blocked the final answer).

## ⚠️ Known Limitations & Next Steps
1. **Acronym Search Failure:** The arXiv API struggles with specific acronyms (e.g., "THaMES"). **Next step:** Add a web search fallback (e.g., Tavily) if arXiv returns zero relevant results.
2. **Citation Formatting:** The LLM occasionally outputs full-width brackets (`【1】`) instead of standard brackets (`[1]`). **Next step:** Add a regex post-processing step to normalize citations.
3. **Rollback Granularity:** Currently, a failed critique restarts the graph from the `plan` node. **Next step:** Implement a `failure_type` check so the Critic can route directly to `search` (if evidence was bad) or `write` (if writing was bad), saving API calls.