import arxiv

def search_arxiv(query: str, max_results: int = 3) -> list[dict]:
    """
    Searches arXiv for a given query and returns a list of papers.
    Each paper is a dict with 'title', 'abstract', and 'url'.
    """
    print(f"[arxiv_tool] Searching for: '{query}' (max {max_results} results)")
    
    # 1. Initialize the client (this replaces the old deprecated arxiv.query())
    client = arxiv.Client()
    
    # 2. Build the search object
    search = arxiv.Search(
        query=query,
        max_results=max_results,
        sort_by=arxiv.SortCriterion.Relevance
    )
    
    results = []
    
    try:
        # 3. Execute the search
        for paper in client.results(search):
            results.append({
                "title": paper.title.replace("\n", " "),
                "abstract": paper.summary.replace("\n", " "),
                "url": paper.entry_id
            })
    except Exception as e:
        # 4. If the API fails, we log it but don't crash the graph
        print(f"[arxiv_tool] ERROR: {e}")
        
    # 5. If no results are found, return an empty list
    if not results:
        print(f"[arxiv_tool] No results found for: '{query}'")
        
    return results