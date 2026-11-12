from app.tools.arxiv_tool import search_arxiv

# Let's test it with a real query
papers = search_arxiv("hallucination in large language models", max_results=2)

print("\n--- RESULTS ---")
for i, p in enumerate(papers):
    print(f"[{i+1}] {p['title']}")
    print(f"URL: {p['url']}")
    print(f"Abstract snippet: {p['abstract'][:100]}...\n")