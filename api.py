import os
import re
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List, Optional

from graph.workflow import build_graph
from core.router import route_query

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


class WatchlistRequest(BaseModel):
    """Request model for watchlist scan."""
    tickers: List[str]  # e.g. ["RELIANCE.NS", "TCS.NS", "INFY.NS"]
    signal_filter: Optional[str] = None  # "BUY", "SELL", or None for all


class StockSignal(BaseModel):
    """A single stock's analysis result for watchlist scan."""
    ticker: str
    recommendation: str  # "BUY", "HOLD", "SELL"
    risk_level: str
    summary: str


class WatchlistResponse(BaseModel):
    """Response model for watchlist scan."""
    total_scanned: int
    signals: List[StockSignal]
    actionable: List[StockSignal]  # filtered BUY/SELL signals


class SmartAnalyzeResponse(BaseModel):
    """Response model that handles both single-stock and multi-stock results."""
    intent: str
    # Single-stock fields (present when intent == single_stock_analysis)
    ticker: Optional[str] = None
    technical_analysis: Optional[str] = None
    fundamental_analysis: Optional[str] = None
    sentiment_analysis: Optional[str] = None
    risk_analysis: Optional[str] = None
    final_recommendation: Optional[str] = None
    # Multi-stock fields (present for compare/portfolio intents)
    tickers: Optional[List[str]] = None
    crew_result: Optional[str] = None
    error: Optional[str] = None

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


@app.post("/smart-analyze", response_model=SmartAnalyzeResponse)
async def smart_analyze(request: AnalyzeRequest):
    """
    Smart endpoint that auto-detects query intent and routes to the right workflow:
    - Single stock queries -> existing LangGraph pipeline
    - Compare/portfolio queries -> CrewAI crew
    """
    if request.api_key:
        os.environ["GEMINI_API_KEY"] = request.api_key

    try:
        result = route_query(request.query)
        return SmartAnalyzeResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def _extract_recommendation(text: str) -> str:
    """Extract BUY/HOLD/SELL from the judge's final recommendation text."""
    text_upper = text.upper()
    match = re.search(r"FINAL\s+RECOMMENDATION:\s*(BUY|HOLD|SELL)", text_upper)
    if match:
        return match.group(1)
    # Fallback: look for standalone keywords
    for signal in ["BUY", "SELL", "HOLD"]:
        if signal in text_upper:
            return signal
    return "UNKNOWN"


def _extract_risk_level(text: str) -> str:
    """Extract risk level from risk analysis text."""
    text_upper = text.upper()
    for level in ["HIGH RISK", "MEDIUM RISK", "LOW RISK"]:
        if level in text_upper:
            return level
    return "UNKNOWN"


@app.post("/watchlist-scan", response_model=WatchlistResponse)
async def watchlist_scan(request: WatchlistRequest):
    """
    Scan a list of tickers and return analysis signals for each.
    Designed to be called by n8n's scheduled workflow for daily pre-market alerts.

    - Runs the full LangGraph analysis pipeline on each ticker
    - Returns structured signals with BUY/HOLD/SELL + risk level
    - Filters actionable signals (BUY or SELL) for easy alerting
    """
    graph = build_graph()
    signals: List[StockSignal] = []

    for ticker in request.tickers:
        try:
            final_state = graph.invoke({
                "user_query": f"Analyze {ticker}",
                "ticker": ticker,
                "technical_analysis": "",
                "fundamental_analysis": "",
                "sentiment_analysis": "",
                "risk_analysis": "",
                "final_recommendation": "",
                "messages": [],
            })

            recommendation = _extract_recommendation(
                final_state.get("final_recommendation", "")
            )
            risk_level = _extract_risk_level(
                final_state.get("risk_analysis", "")
            )

            # Build a concise summary from all analyses
            # Strip markdown formatting (headers, bold) for clean summaries
            def clean_text(text: str) -> str:
                cleaned = re.sub(r"[#*_`]+", "", text).strip()
                # Get first meaningful sentence (skip empty lines)
                for line in cleaned.split("\n"):
                    line = line.strip()
                    if len(line) > 20:
                        # Take first sentence
                        sentence = line.split(".")[0].strip()
                        return sentence + "." if not sentence.endswith(".") else sentence
                return cleaned[:150] if cleaned else ""

            summary_parts = []
            tech = final_state.get("technical_analysis", "")
            if tech:
                summary_parts.append(f"Technical: {clean_text(tech)}")

            fund = final_state.get("fundamental_analysis", "")
            if fund:
                summary_parts.append(f"Fundamental: {clean_text(fund)}")

            summary = " | ".join(summary_parts) if summary_parts else "Analysis completed."

            signal = StockSignal(
                ticker=ticker,
                recommendation=recommendation,
                risk_level=risk_level,
                summary=summary,
            )
            signals.append(signal)

        except Exception as e:
            signals.append(StockSignal(
                ticker=ticker,
                recommendation="ERROR",
                risk_level="UNKNOWN",
                summary=f"Analysis failed: {str(e)}",
            ))

    # Filter actionable signals
    actionable = [
        s for s in signals
        if s.recommendation in ("BUY", "SELL")
    ]

    # Apply signal_filter if provided
    if request.signal_filter:
        actionable = [
            s for s in actionable
            if s.recommendation == request.signal_filter.upper()
        ]

    return WatchlistResponse(
        total_scanned=len(request.tickers),
        signals=signals,
        actionable=actionable,
    )
