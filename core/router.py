from typing import Dict, Any

from core.classifier import classify_intent, extract_tickers
from graph.workflow import build_graph
from crew.portfolio_crew import run_compare_stocks_crew, run_portfolio_crew


def route_query(query: str) -> Dict[str, Any]:
    """
    Classify the user query intent and route to the appropriate execution path.

    Returns a dict with:
      - intent: the classified intent
      - For single_stock: ticker, technical/fundamental/sentiment/risk analysis, final_recommendation
      - For multi-stock: tickers, crew_result
      - On error: error message
    """
    intent = classify_intent(query)

    if intent == "single_stock_analysis":
        # Route to existing LangGraph pipeline (unchanged)
        graph = build_graph()
        final_state = graph.invoke(
            {
                "user_query": query,
                "ticker": "",
                "technical_analysis": "",
                "fundamental_analysis": "",
                "sentiment_analysis": "",
                "risk_analysis": "",
                "final_recommendation": "",
                "messages": [],
            }
        )
        return {
            "intent": intent,
            "ticker": final_state.get("ticker", ""),
            "technical_analysis": final_state.get("technical_analysis", ""),
            "fundamental_analysis": final_state.get("fundamental_analysis", ""),
            "sentiment_analysis": final_state.get("sentiment_analysis", ""),
            "risk_analysis": final_state.get("risk_analysis", ""),
            "final_recommendation": final_state.get("final_recommendation", ""),
        }

    # Multi-stock intents — extract tickers first
    tickers = extract_tickers(query)
    if not tickers:
        return {
            "intent": intent,
            "error": "Could not extract stock tickers from your query. Please mention specific stock names.",
        }

    if intent == "compare_stocks":
        result = run_compare_stocks_crew(tickers, query)
        return {"intent": intent, "tickers": tickers, "crew_result": result}

    elif intent in ("portfolio_allocation", "portfolio_analysis"):
        result = run_portfolio_crew(tickers, query)
        return {"intent": intent, "tickers": tickers, "crew_result": result}

    return {"intent": intent, "error": "Unrecognized intent."}
