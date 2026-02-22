from langchain_core.messages import SystemMessage, HumanMessage
from core.config import get_llm
from core.state import TradingState
from tools.market_data import get_stock_history
from tools.technical_ind import add_all_indicators
import pandas as pd

TECHNICAL_SYSTEM_PROMPT = """You are an expert Technical Analyst for Indian Stock Markets.
Your job is to analyze the price action, volume, and technical indicators of a stock and provide a technical analysis summary.
Include insights on Moving Averages (SMA, EMA), RSI, and MACD.
Conclude with a clear 'Bullish', 'Bearish', or 'Neutral' technical signal.
Be concise but highly analytical.
"""

def technical_analyst_node(state: TradingState) -> dict:
    ticker = state.get("ticker", "")
    if not ticker:
        return {"technical_analysis": "Error: No ticker provided for technical analysis."}

    # Fetch data directly (Guarantees data availability without agent reasoning loops)
    df = get_stock_history(ticker, period="3mo")
    if df.empty:
        return {"technical_analysis": f"Could not retrieve historical data for {ticker}."}
    
    # Add indicators
    df_ind = add_all_indicators(df)
    
    # Get the last 10 days of data to provide to the LLM to avoid overwhelming context
    recent_data = df_ind.tail(10).to_json(orient="records")

    llm = get_llm(temperature=0.1)
    
    messages = [
        SystemMessage(content=TECHNICAL_SYSTEM_PROMPT),
        HumanMessage(content=f"Analyze the following recent technical data for {ticker}:\n{recent_data}")
    ]
    
    response = llm.invoke(messages)
    
    return {"technical_analysis": response.content}
