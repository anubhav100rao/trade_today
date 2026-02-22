import pytest
import pandas as pd
from unittest.mock import patch, MagicMock

from core.state import TradingState
from agents.technical import technical_analyst_node
from agents.fundamental import fundamental_analyst_node
from agents.sentiment import sentiment_analyst_node
from agents.risk import risk_analyst_node
from agents.judge import judge_node

def setup_mock_llm(mock_get_llm: MagicMock, return_content: str):
    """Helper feature to construct a mocked LLM that returns a specific string."""
    mock_llm = MagicMock()
    mock_response = MagicMock()
    mock_response.content = return_content
    mock_llm.invoke.return_value = mock_response
    mock_get_llm.return_value = mock_llm

@patch("agents.technical.get_llm")
@patch("agents.technical.get_stock_history")
@patch("agents.technical.add_all_indicators")
def test_technical_analyst_node(mock_add_ind, mock_get_stock, mock_get_llm):
    """
    Test Technical Analyst agent with a mocked LLM to save Gemini credits.
    We also mock the data retrieval to make the test fast and offline.
    """
    setup_mock_llm(mock_get_llm, "Bullish")
    
    # Mock return values for the tools
    dummy_df = pd.DataFrame({"Close": [100]})
    mock_get_stock.return_value = dummy_df
    mock_add_ind.return_value = pd.DataFrame({"Close": [100], "SMA_20": [100]})
    
    state: TradingState = {"user_query": "Analyze RELIANCE", "ticker": "RELIANCE.NS"}
    res = technical_analyst_node(state)
    
    assert "technical_analysis" in res
    assert res["technical_analysis"] == "Bullish"
    mock_get_llm.assert_called_once()
    
    # Ensure tool were called with the right ticker
    mock_get_stock.assert_called_once_with("RELIANCE.NS", period="3mo")

@patch("agents.fundamental.get_llm")
@patch("agents.fundamental.get_financial_metrics")
def test_fundamental_analyst_node(mock_get_metrics, mock_get_llm):
    """
    Test Fundamental Analyst agent with a mocked LLM.
    """
    setup_mock_llm(mock_get_llm, "Undervalued")
    mock_get_metrics.return_value = {"marketCap": 1000000, "peRatio": 15.0} # Mock tools
    
    state: TradingState = {"ticker": "RELIANCE.NS"}
    res = fundamental_analyst_node(state)
    
    assert "fundamental_analysis" in res
    assert res["fundamental_analysis"] == "Undervalued"
    mock_get_llm.assert_called_once()

@patch("agents.sentiment.get_llm")
@patch("agents.sentiment.search_financial_news")
def test_sentiment_analyst_node(mock_search_news, mock_get_llm):
    """
    Test Sentiment Analyst agent with a mocked LLM.
    """
    setup_mock_llm(mock_get_llm, "Bullish Sentiment")
    # Mock DuckDuckGo results
    mock_search_news.return_value = [{"title": "Reliance profits surge", "snippet": "Huge growth..."}]
    
    state: TradingState = {"ticker": "RELIANCE.NS", "user_query": "RELIANCE.NS"}
    res = sentiment_analyst_node(state)
    
    assert "sentiment_analysis" in res
    assert res["sentiment_analysis"] == "Bullish Sentiment"
    mock_get_llm.assert_called_once()
    mock_search_news.assert_called_once()

@patch("agents.risk.get_llm")
@patch("agents.risk.get_financial_metrics")
def test_risk_analyst_node(mock_get_metrics, mock_get_llm):
    """
    Test Risk Analyst agent with a mocked LLM.
    """
    setup_mock_llm(mock_get_llm, "Low Risk")
    mock_get_metrics.return_value = {"beta": 1.2, "fiftyTwoWeekHigh": 1500, "fiftyTwoWeekLow": 1000}
    
    state: TradingState = {"ticker": "RELIANCE.NS"}
    res = risk_analyst_node(state)
    
    assert "risk_analysis" in res
    assert res["risk_analysis"] == "Low Risk"
    mock_get_llm.assert_called_once()

@patch("agents.judge.get_llm")
def test_judge_node(mock_get_llm):
    """
    Test Final Judge Node with a mocked LLM.
    """
    setup_mock_llm(mock_get_llm, "FINAL RECOMMENDATION: BUY")
    
    state: TradingState = {
        "user_query": "Analyze RELIANCE",
        "ticker": "RELIANCE.NS",
        "technical_analysis": "Bullish",
        "fundamental_analysis": "Undervalued",
        "sentiment_analysis": "Bullish",
        "risk_analysis": "Low Risk",
        "messages": [],
        "final_recommendation": ""
    }
    
    res = judge_node(state)
    
    assert "final_recommendation" in res
    assert res["final_recommendation"] == "FINAL RECOMMENDATION: BUY"
    
    # We can inspect what was sent to the LLM to verify synthesis structure
    mock_llm = mock_get_llm.return_value
    calls = mock_llm.invoke.call_args_list
    assert len(calls) == 1
    
    messages = calls[0][0][0] # extracting the list of messages passed to invoke
    human_msg_content = messages[1].content
    assert "[TECHNICAL ANALYSIS]" in human_msg_content
    assert "Bullish" in human_msg_content
