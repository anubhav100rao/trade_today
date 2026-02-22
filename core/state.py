from typing import TypedDict, Annotated
from operator import add

class TradingState(TypedDict):
    """
    State representing the current progression of a trading analysis workflow.
    """
    user_query: str
    ticker: str
    fundamental_analysis: str
    technical_analysis: str
    sentiment_analysis: str
    risk_analysis: str
    final_recommendation: str
    messages: Annotated[list, add] # To keep track of the conversation/agent thoughts
