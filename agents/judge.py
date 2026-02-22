from langchain_core.messages import SystemMessage, HumanMessage
from core.config import get_llm
from core.state import TradingState

JUDGE_SYSTEM_PROMPT = """You are the Lead Portfolio Manager and Final Judge.
You are reviewing a comprehensive report on an Indian Stock compiled by 4 expert analysts: Technical, Fundamental, Sentiment, and Risk.
Your job is to synthesize these 4 perspectives, resolve any conflicts (e.g., strong fundamentals but bearish technicals might mean 'Hold' or 'Wait for better entry'), and make a final investment decision.

Your output MUST end with a clear, definitive recommendation formatted exactly as one of the following:
FINAL RECOMMENDATION: BUY
FINAL RECOMMENDATION: HOLD
FINAL RECOMMENDATION: SELL

Keep your synthesis concise, highlighting the most heavily weighted factors.
"""

def judge_node(state: TradingState) -> dict:
    ticker = state.get("ticker", "Unknown")
    tech = state.get("technical_analysis", "")
    fund = state.get("fundamental_analysis", "")
    sent = state.get("sentiment_analysis", "")
    risk = state.get("risk_analysis", "")

    synthesis_report = f"""
    --- STOCK: {ticker} ---
    
    [TECHNICAL ANALYSIS]
    {tech}
    
    [FUNDAMENTAL ANALYSIS]
    {fund}
    
    [SENTIMENT ANALYSIS]
    {sent}
    
    [RISK ANALYSIS]
    {risk}
    """

    llm = get_llm(temperature=0.3)
    
    messages = [
        SystemMessage(content=JUDGE_SYSTEM_PROMPT),
        HumanMessage(content=f"Here are the analyst reports to synthesize:\n{synthesis_report}")
    ]
    
    response = llm.invoke(messages)
    
    return {"final_recommendation": response.content}
