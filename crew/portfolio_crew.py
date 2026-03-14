import json
import os
from typing import List, Dict

from crewai import Agent, Task, Crew, Process, LLM
from crewai.tools import tool

from core.config import get_llm
from graph.workflow import build_graph
from tools.market_data import get_financial_metrics
from tools.correlation import (
    calculate_correlation_matrix,
    calculate_portfolio_metrics,
    get_sector_diversity,
)


# ============================================================
# CrewAI Tool Wrappers
# ============================================================


@tool("Analyze Single Stock")
def analyze_single_stock(ticker: str) -> str:
    """Run the full LangGraph multi-agent analysis pipeline on a single stock ticker.
    Returns the complete analysis including technical, fundamental, sentiment,
    risk analysis and final BUY/HOLD/SELL recommendation."""
    try:
        graph = build_graph()
        result = graph.invoke(
            {
                "user_query": f"Analyze {ticker}",
                "ticker": ticker,
                "technical_analysis": "",
                "fundamental_analysis": "",
                "sentiment_analysis": "",
                "risk_analysis": "",
                "final_recommendation": "",
                "messages": [],
            }
        )
        return json.dumps(
            {
                "ticker": result.get("ticker", ""),
                "technical": result.get("technical_analysis", ""),
                "fundamental": result.get("fundamental_analysis", ""),
                "sentiment": result.get("sentiment_analysis", ""),
                "risk": result.get("risk_analysis", ""),
                "recommendation": result.get("final_recommendation", ""),
            },
            indent=2,
        )
    except Exception as e:
        return f"Error analyzing {ticker}: {str(e)}"


@tool("Get Correlation Matrix")
def get_correlation_matrix(tickers_csv: str) -> str:
    """Calculate the price correlation matrix for multiple stocks.
    Input: comma-separated tickers, e.g. 'RELIANCE.NS,TCS.NS,INFY.NS'
    Returns the correlation matrix showing how closely stocks move together."""
    try:
        tickers = [t.strip() for t in tickers_csv.split(",")]
        corr = calculate_correlation_matrix(tickers)
        if corr.empty:
            return "Could not calculate correlations — insufficient data."
        return corr.to_string()
    except Exception as e:
        return f"Error calculating correlation: {str(e)}"


@tool("Calculate Portfolio Metrics")
def get_portfolio_metrics(holdings_json: str) -> str:
    """Calculate portfolio risk-return metrics.
    Input: JSON string of {ticker: weight}, e.g. '{"RELIANCE.NS": 0.4, "TCS.NS": 0.6}'.
    Returns annualized return, volatility, Sharpe ratio, and correlation matrix."""
    try:
        holdings = json.loads(holdings_json)
        metrics = calculate_portfolio_metrics(holdings)
        if not metrics:
            return "Could not calculate portfolio metrics — insufficient data."
        return json.dumps(metrics, indent=2, default=str)
    except Exception as e:
        return f"Error calculating portfolio metrics: {str(e)}"


@tool("Get Stock Fundamentals")
def get_stock_fundamentals(ticker: str) -> str:
    """Fetch key fundamental financial metrics for a stock ticker.
    Returns P/E ratio, market cap, EPS, margins, beta, sector, and more."""
    try:
        metrics = get_financial_metrics(ticker)
        return json.dumps(metrics, indent=2, default=str)
    except Exception as e:
        return f"Error fetching fundamentals for {ticker}: {str(e)}"


@tool("Get Sector Diversity")
def get_sector_diversity_tool(tickers_csv: str) -> str:
    """Check sector diversity for a list of stocks.
    Input: comma-separated tickers, e.g. 'RELIANCE.NS,TCS.NS'.
    Returns stocks grouped by sector to assess diversification."""
    try:
        tickers = [t.strip() for t in tickers_csv.split(",")]
        diversity = get_sector_diversity(tickers)
        return json.dumps(diversity, indent=2)
    except Exception as e:
        return f"Error checking sector diversity: {str(e)}"


# ============================================================
# Agent Factory Functions
# ============================================================


def _get_crewai_llm(temperature: float = 0.2):
    """Returns a CrewAI-native LLM instance using Google Gemini."""
    api_key = os.getenv("GEMINI_API_KEY", "")
    return LLM(
        model="gemini/gemini-2.5-flash",
        api_key=api_key,
        temperature=temperature,
    )


def create_stock_scorer_agent() -> Agent:
    """Creates an agent that scores individual stocks using the existing LangGraph pipeline."""
    return Agent(
        role="Stock Scorer",
        goal="Run the full analysis pipeline on each individual stock and summarize the scores with clear BUY/HOLD/SELL verdicts",
        backstory=(
            "You are a senior equity analyst who delegates per-stock deep-dives "
            "to a specialized multi-agent analysis system. You collect their findings "
            "and present a clear summary for each stock."
        ),
        tools=[analyze_single_stock, get_stock_fundamentals],
        llm=_get_crewai_llm(),
        verbose=True,
    )


def create_correlation_analyst_agent() -> Agent:
    """Creates an agent that analyzes correlation and diversification."""
    return Agent(
        role="Correlation & Diversification Analyst",
        goal="Analyze correlation between stocks, assess sector diversification, and evaluate portfolio risk metrics",
        backstory=(
            "You are a quantitative analyst specializing in portfolio risk, "
            "diversification metrics, and modern portfolio theory for Indian equities."
        ),
        tools=[
            get_correlation_matrix,
            get_portfolio_metrics,
            get_sector_diversity_tool,
        ],
        llm=_get_crewai_llm(),
        verbose=True,
    )


def create_portfolio_strategist_agent() -> Agent:
    """Creates the final strategist agent that synthesizes all data into recommendations."""
    return Agent(
        role="Portfolio Strategist",
        goal="Synthesize individual stock scores and correlation data into actionable portfolio advice with specific allocation percentages",
        backstory=(
            "You are a senior portfolio manager for Indian equities with 20 years "
            "of experience. You make final allocation decisions based on analyst input, "
            "balancing risk-reward and diversification."
        ),
        tools=[],
        llm=_get_crewai_llm(temperature=0.3),
        verbose=True,
    )


# ============================================================
# Crew Runner Functions
# ============================================================


def run_compare_stocks_crew(tickers: List[str], user_query: str) -> str:
    """
    Compare multiple stocks side-by-side.
    Runs the full analysis on each stock, calculates correlation,
    and provides a comparative recommendation.
    """
    scorer = create_stock_scorer_agent()
    correlation_analyst = create_correlation_analyst_agent()
    strategist = create_portfolio_strategist_agent()

    tickers_str = ", ".join(tickers)
    tickers_csv = ",".join(tickers)

    task_score = Task(
        description=(
            f"Analyze each of these stocks individually: {tickers_str}. "
            f"Use the 'Analyze Single Stock' tool for EACH ticker one by one. "
            f"Summarize the BUY/HOLD/SELL recommendation and key strengths/weaknesses for each stock."
        ),
        expected_output="A clear summary of each stock's analysis with BUY/HOLD/SELL recommendation and key metrics.",
        agent=scorer,
    )

    task_correlation = Task(
        description=(
            f"Calculate the correlation matrix for these tickers: {tickers_csv}. "
            f"Also check their sector diversity using the sector diversity tool with: {tickers_csv}. "
            f"Explain what the correlation and sector spread means for an investor choosing between these stocks."
        ),
        expected_output="Correlation matrix, sector diversity assessment, and diversification analysis.",
        agent=correlation_analyst,
    )

    task_strategy = Task(
        description=(
            f"Based on the individual stock scores and correlation analysis provided above, "
            f"answer the user's original question: '{user_query}'. "
            f"Provide a clear head-to-head comparison and a final recommendation on which stock(s) "
            f"are the better pick and why. Include specific reasons."
        ),
        expected_output="A clear comparison of all stocks with a final recommendation and reasoning.",
        agent=strategist,
    )

    crew = Crew(
        agents=[scorer, correlation_analyst, strategist],
        tasks=[task_score, task_correlation, task_strategy],
        process=Process.sequential,
        verbose=True,
    )

    result = crew.kickoff()
    return str(result)


def run_portfolio_crew(
    tickers: List[str],
    user_query: str,
    weights: Dict[str, float] = None,
) -> str:
    """
    Run portfolio analysis or allocation crew.
    Analyzes individual stocks, calculates portfolio metrics,
    and suggests optimal allocation.
    """
    scorer = create_stock_scorer_agent()
    correlation_analyst = create_correlation_analyst_agent()
    strategist = create_portfolio_strategist_agent()

    tickers_str = ", ".join(tickers)
    tickers_csv = ",".join(tickers)

    task_score = Task(
        description=(
            f"Analyze each of these stocks individually: {tickers_str}. "
            f"Use the 'Analyze Single Stock' tool for EACH ticker one by one. "
            f"Provide a complete summary with BUY/HOLD/SELL and key metrics for each."
        ),
        expected_output="Summary of each stock's analysis with recommendation.",
        agent=scorer,
    )

    if weights:
        weights_json = json.dumps(weights)
        task_portfolio = Task(
            description=(
                f"Calculate portfolio metrics for these holdings: {weights_json}. "
                f"Also calculate the correlation matrix for: {tickers_csv}. "
                f"Check sector diversity for: {tickers_csv}. "
                f"Assess the portfolio's diversification quality, risk level, and suggest improvements."
            ),
            expected_output="Portfolio metrics (return, volatility, Sharpe), correlation analysis, and sector diversity.",
            agent=correlation_analyst,
        )
    else:
        task_portfolio = Task(
            description=(
                f"Calculate the correlation matrix for: {tickers_csv}. "
                f"Check sector diversity for: {tickers_csv}. "
                f"Based on the correlations, suggest an optimal weight allocation "
                f"that maximizes diversification. Assume equal weights as starting point."
            ),
            expected_output="Correlation matrix, sector diversity, and suggested weight allocation.",
            agent=correlation_analyst,
        )

    task_strategy = Task(
        description=(
            f"Synthesize the individual stock analyses and portfolio metrics to answer: '{user_query}'. "
            f"Provide specific allocation percentages for each stock with clear rationale. "
            f"Include a risk assessment and any warnings about concentration or correlation risks."
        ),
        expected_output="Final portfolio recommendation with specific allocation percentages, risk assessment, and rationale.",
        agent=strategist,
    )

    crew = Crew(
        agents=[scorer, correlation_analyst, strategist],
        tasks=[task_score, task_portfolio, task_strategy],
        process=Process.sequential,
        verbose=True,
    )

    result = crew.kickoff()
    return str(result)
