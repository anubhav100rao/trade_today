from langchain_core.messages import SystemMessage, HumanMessage
from core.config import get_llm
from core.state import TradingState
from tools.market_data import get_financial_metrics
import json

FUNDAMENTAL_SYSTEM_PROMPT = """You are an expert Fundamental Analyst for Indian Stock Markets.
Your job is to evaluate a company's financial health based on core metrics (P/E, EPS, Margins, Debt, ROE).
Compare valuation, profitability, and growth.
Conclude with a clear 'Undervalued', 'Overvalued', or 'Fairly Valued' assessment.
Be concise but highly analytical.
"""

def fundamental_analyst_node(state: TradingState) -> dict:
    ticker = state.get("ticker", "")
    if not ticker:
        return {"fundamental_analysis": "Error: No ticker provided."}

    # Fetch financial metrics
    metrics = get_financial_metrics(ticker)
    
    if not metrics or metrics.get("marketCap") is None:
        return {"fundamental_analysis": f"Could not retrieve fundamental metrics for {ticker}."}

    metrics_str = json.dumps(metrics, indent=2)

    llm = get_llm(temperature=0.1)
    
    messages = [
        SystemMessage(content=FUNDAMENTAL_SYSTEM_PROMPT),
        HumanMessage(content=f"Analyze the following financial metrics for {ticker}:\n{metrics_str}")
    ]
    
    response = llm.invoke(messages)
    
    return {"fundamental_analysis": response.content}
