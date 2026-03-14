from langchain_core.messages import SystemMessage, HumanMessage
from core.config import get_llm
from typing import List

CLASSIFIER_SYSTEM_PROMPT = """You are a query intent classifier for a stock trading analysis system.
Classify the user query into EXACTLY one of these categories:

1. single_stock_analysis - User wants analysis of ONE specific stock (e.g., "Should I buy RELIANCE?", "Analyze TCS", "How is HDFC today?")
2. compare_stocks - User wants to compare TWO OR MORE specific stocks side-by-side (e.g., "Compare RELIANCE vs TCS", "Which is better, INFY or WIPRO?")
3. portfolio_allocation - User wants help building or allocating a new portfolio with a budget (e.g., "I have 5L to invest in IT and pharma", "Build me a portfolio")
4. portfolio_analysis - User already holds multiple stocks and wants a health check (e.g., "I hold RELIANCE, TCS, HDFC — how's my portfolio?", "Analyze my holdings")

Respond with ONLY the category string, nothing else. No quotes, no explanation.
"""

TICKER_EXTRACTOR_PROMPT = """Extract ALL stock tickers mentioned in this query.
For Indian stocks, append .NS (NSE) suffix if not already present.
Return as a comma-separated list. Example: RELIANCE.NS,TCS.NS,INFY.NS
If you cannot determine any tickers, output 'UNKNOWN'.
Respond ONLY with the comma-separated tickers, no other text.
"""


def classify_intent(query: str) -> str:
    """
    Classify a user query into one of four intents.
    Returns: single_stock_analysis, compare_stocks, portfolio_allocation, or portfolio_analysis
    """
    llm = get_llm(temperature=0.0)
    messages = [
        SystemMessage(content=CLASSIFIER_SYSTEM_PROMPT),
        HumanMessage(content=query),
    ]
    response = llm.invoke(messages)
    intent = response.content.strip().lower().replace('"', "").replace("'", "")

    valid_intents = {
        "single_stock_analysis",
        "compare_stocks",
        "portfolio_allocation",
        "portfolio_analysis",
    }
    return intent if intent in valid_intents else "single_stock_analysis"


def extract_tickers(query: str) -> List[str]:
    """Extract multiple stock tickers from a user query."""
    llm = get_llm(temperature=0.0)
    messages = [
        SystemMessage(content=TICKER_EXTRACTOR_PROMPT),
        HumanMessage(content=query),
    ]
    response = llm.invoke(messages)
    raw = response.content.strip()

    if raw == "UNKNOWN" or not raw:
        return []

    return [t.strip() for t in raw.split(",") if t.strip()]
