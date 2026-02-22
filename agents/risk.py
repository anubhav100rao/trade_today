from langchain_core.messages import SystemMessage, HumanMessage
from core.config import get_llm
from core.state import TradingState
from tools.market_data import get_financial_metrics

RISK_SYSTEM_PROMPT = """You are an expert Risk Management Analyst for Indian Markets.
Your job is to evaluate the risk of investing in a given stock.
Analyze the Beta (volatility compared to the market), and 52-week range.
Conclude with a clear 'High Risk', 'Medium Risk', or 'Low Risk' rating.
Provide a concise risk assessment.
"""

def risk_analyst_node(state: TradingState) -> dict:
    ticker = state.get("ticker", "")
    if not ticker:
        return {"risk_analysis": "Error: No ticker provided."}

    # Fetch basic metrics necessary for risk (beta, 52 wk high/low)
    metrics = get_financial_metrics(ticker)
    
    if not metrics or metrics.get("beta") is None:
        # Fallback if no beta
        risk_data = f"Ticker: {ticker}\nBeta: Data Unavailable\n"
    else:
        risk_data = (
            f"Ticker: {ticker}\n"
            f"Beta: {metrics.get('beta')}\n"
            f"52-Week High: {metrics.get('fiftyTwoWeekHigh')}\n"
            f"52-Week Low: {metrics.get('fiftyTwoWeekLow')}\n"
            f"Debt to Equity: {metrics.get('debtToEquity')}\n"
        )

    llm = get_llm(temperature=0.1)
    
    messages = [
        SystemMessage(content=RISK_SYSTEM_PROMPT),
        HumanMessage(content=f"Evaluate the risk for {ticker} based on this data:\n{risk_data}")
    ]
    
    response = llm.invoke(messages)
    
    return {"risk_analysis": response.content}
