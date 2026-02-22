from langchain_core.messages import SystemMessage, HumanMessage
from core.config import get_llm
from core.state import TradingState
from tools.search import search_financial_news
import json

SENTIMENT_SYSTEM_PROMPT = """You are an expert Market Sentiment Analyst.
Your job is to read recent news headlines and snippets about a specific stock and gauge the market's mood.
Identify any major catalysts, positive news, or concerning events.
Conclude with a clear 'Bullish', 'Bearish', or 'Neutral' sentiment rating.
Be concise.
"""

def sentiment_analyst_node(state: TradingState) -> dict:
    ticker = state.get("ticker", "")
    query = state.get("user_query", ticker)
    if not ticker:
        return {"sentiment_analysis": "Error: No ticker provided."}

    # Search DuckDuckGo for news
    # Removing .NS/.BO for better search results if purely searching news
    search_term = ticker.split(".")[0] + " share news Indian stock market"
    news_items = search_financial_news(search_term, max_results=5)
    
    if not news_items:
        return {"sentiment_analysis": f"Could not find recent news for {ticker}."}

    news_str = json.dumps(news_items, indent=2)

    llm = get_llm(temperature=0.2)
    
    messages = [
        SystemMessage(content=SENTIMENT_SYSTEM_PROMPT),
        HumanMessage(content=f"Analyze the following recent news for {ticker}:\n{news_str}")
    ]
    
    response = llm.invoke(messages)
    
    return {"sentiment_analysis": response.content}
