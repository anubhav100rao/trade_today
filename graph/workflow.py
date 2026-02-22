from langgraph.graph import StateGraph, START, END
from langchain_core.messages import SystemMessage, HumanMessage

from core.state import TradingState
from core.config import get_llm
from agents.technical import technical_analyst_node
from agents.fundamental import fundamental_analyst_node
from agents.sentiment import sentiment_analyst_node
from agents.risk import risk_analyst_node
from agents.judge import judge_node

SUPERVISOR_SYSTEM_PROMPT = """You are the Supervisor of a Trading Analysis Swarm.
Your ONLY job is to extract the stock ticker from the user query.
If the user provides an Indian stock name, attempt to append the correct Yahoo Finance suffix (.NS for NSE, .BO for BSE) if missing. 
Respond ONLY with the exact ticker string (e.g. 'RELIANCE.NS'). Do not include any other text, reasoning, or markdown formatting.
If you cannot determine a ticker, output 'UNKNOWN'.
"""

def supervisor_node(state: TradingState) -> dict:
    """Supervisory node that parses the user query and populates the target ticker."""
    query = state.get("user_query", "")
    
    # Bypass LLM if ticker is already perfectly defined
    if state.get("ticker"):
        return {"ticker": state["ticker"]}
        
    llm = get_llm(temperature=0.0) # Zero temp for strict string extraction
    messages = [
        SystemMessage(content=SUPERVISOR_SYSTEM_PROMPT),
        HumanMessage(content=query)
    ]
    
    response = llm.invoke(messages)
    ticker = response.content.strip()
    
    # Store the parsed ticker in the state
    return {"ticker": ticker}

def build_graph() -> StateGraph:
    """Constructs and returns the compiled LangGraph execution graph."""
    
    # Initialize the graph with our state schema
    workflow = StateGraph(TradingState)
    
    # ==========================
    # 1. Add Nodes
    # ==========================
    workflow.add_node("supervisor", supervisor_node)
    workflow.add_node("technical_analyst", technical_analyst_node)
    workflow.add_node("fundamental_analyst", fundamental_analyst_node)
    workflow.add_node("sentiment_analyst", sentiment_analyst_node)
    workflow.add_node("risk_analyst", risk_analyst_node)
    workflow.add_node("judge", judge_node)
    
    # ==========================
    # 2. Define Edges & Routing
    # ==========================
    # Entry point
    workflow.add_edge(START, "supervisor")
    
    # After the supervisor extracts the ticker, fan out to all 4 analysts in parallel
    workflow.add_edge("supervisor", "technical_analyst")
    workflow.add_edge("supervisor", "fundamental_analyst")
    workflow.add_edge("supervisor", "sentiment_analyst")
    workflow.add_edge("supervisor", "risk_analyst")
    
    # All 4 analysts must complete before moving to the judge (LangGraph handles the join implicitly via the edges downstream)
    workflow.add_edge("technical_analyst", "judge")
    workflow.add_edge("fundamental_analyst", "judge")
    workflow.add_edge("sentiment_analyst", "judge")
    workflow.add_edge("risk_analyst", "judge")
    
    # End execution after the judge makes the final recommendation
    workflow.add_edge("judge", END)
    
    # ==========================
    # 3. Compile Graph
    # ==========================
    app = workflow.compile()
    return app
