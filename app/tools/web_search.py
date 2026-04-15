import requests
import os
from typing import List, Dict, Any

def web_search(query: str, num_results: int = 5) -> List[Dict[str, Any]]:
    """
    Web search using SerpAPI (mock if no key)
    """
    api_key = os.getenv("SERPAPI_KEY")
    if not api_key:
        # Mock results
        return [
            {"title": f"News about {query}", "link": f"https://example.com/{query.replace(' ', '-')}", "snippet": f"Latest information on {query}"}
            for _ in range(num_results)
        ]

    # Real API call
    url = "https://serpapi.com/search"
    params = {
        "q": query,
        "api_key": api_key,
        "num": num_results
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        return [
            {
                "title": result.get("title", ""),
                "link": result.get("link", ""),
                "snippet": result.get("snippet", "")
            }
            for result in data.get("organic_results", [])
        ]
    return []