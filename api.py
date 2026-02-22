import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List

from graph.workflow import build_graph

app = FastAPI(
    title="Trade Today API",
    description="API for the Multi-Agent Trading Swarm",
    version="1.0.0"
)

# Initialize the LangGraph app once globally (or per request if needed)
# Depending on how the state depends on instantiation, we can also instantiate inside the endpoint.
# But build_graph() likely returns a standard compiled StateGraph which can be shared.
try:
    swarm_app = build_graph()
except Exception as e:
    swarm_app = None
    print(f"Error initializing swarm graph: {e}")

class AnalyzeRequest(BaseModel):
    query: str
    api_key: str | None = None

class AnalyzeResponse(BaseModel):
    ticker: str
    technical_analysis: str
    fundamental_analysis: str
    sentiment_analysis: str
    risk_analysis: str
    final_recommendation: str

@app.get("/health")
def health_check():
    """
    Health check endpoint to verify backend is running.
    """
    return {"status": "ok", "graph_initialized": swarm_app is not None}


@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze_query(request: AnalyzeRequest):
    """
    Accepts a query about a stock and returns the swarm's analysis and final verdict.
    """
    if swarm_app is None:
        raise HTTPException(status_code=500, detail="Graph failed to initialize.")

    if request.api_key:
        os.environ["GEMINI_API_KEY"] = request.api_key

    initial_state = {
        "user_query": request.query,
        "ticker": "",
        "technical_analysis": "",
        "fundamental_analysis": "",
        "sentiment_analysis": "",
        "risk_analysis": "",
        "final_recommendation": "",
        "messages": []
    }

    try:
        # We can use .invoke() for a full synchronous run, returning the final state
        # The stream() approach is better for UI, but for a simple REST backend, invoke is easier.
        final_state = swarm_app.invoke(initial_state)

        return AnalyzeResponse(
            ticker=final_state.get("ticker", ""),
            technical_analysis=final_state.get("technical_analysis", ""),
            fundamental_analysis=final_state.get("fundamental_analysis", ""),
            sentiment_analysis=final_state.get("sentiment_analysis", ""),
            risk_analysis=final_state.get("risk_analysis", ""),
            final_recommendation=final_state.get("final_recommendation", "")
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
