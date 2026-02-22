from duckduckgo_search import DDGS
from typing import List, Dict

def search_financial_news(query: str, max_results: int = 5) -> List[Dict[str, str]]:
    """
    Scrapes DuckDuckGo specifically for news articles about a financial query.
    Returns a list of dictionaries with 'title', 'body', 'date', and 'url'.
    """
    try:
        with DDGS() as ddgs:
            # We use 'news' to get current events
            results = ddgs.news(query, max_results=max_results)
            # DDGS news returns an iterator of dicts, let's coerce to list
            news_items = list(results)
            
            clean_results = []
            for item in news_items:
                clean_results.append({
                    "title": item.get("title", ""),
                    "snippet": item.get("body", ""),
                    "date": item.get("date", ""),
                    "source": item.get("source", ""),
                    "url": item.get("url", "")
                })
            return clean_results
    except Exception as e:
        print(f"Error performing news search for query '{query}': {e}")
        return []

def search_web(query: str, max_results: int = 5) -> List[Dict[str, str]]:
    """
    General web search for background information.
    """
    try:
        with DDGS() as ddgs:
            results = ddgs.text(query, max_results=max_results)
            web_items = list(results)
            
            clean_results = []
            for item in web_items:
                clean_results.append({
                    "title": item.get("title", ""),
                    "snippet": item.get("body", ""),
                    "url": item.get("href", "")
                })
            return clean_results
    except Exception as e:
        print(f"Error performing web search for query '{query}': {e}")
        return []
