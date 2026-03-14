import pandas as pd
import numpy as np
from typing import List, Dict, Any
from tools.market_data import get_stock_history


def calculate_correlation_matrix(
    tickers: List[str], period: str = "6mo"
) -> pd.DataFrame:
    """
    Fetch closing prices for multiple tickers and return their correlation matrix.
    Returns an empty DataFrame if fewer than 2 tickers have valid data.
    """
    close_prices = {}
    for ticker in tickers:
        df = get_stock_history(ticker, period=period)
        if not df.empty and "Close" in df.columns:
            close_prices[ticker] = df.set_index("Date")["Close"]

    if len(close_prices) < 2:
        return pd.DataFrame()

    combined = pd.DataFrame(close_prices).dropna()
    return combined.corr()


def calculate_portfolio_metrics(
    holdings: Dict[str, float], period: str = "6mo"
) -> Dict[str, Any]:
    """
    Calculate portfolio-level metrics for given holdings.

    Args:
        holdings: Dict of {ticker: weight} where weights should sum to ~1.0
        period: Historical data period (default: 6 months)

    Returns:
        Dict with individual returns, volatilities, correlation matrix,
        portfolio return, portfolio volatility, and Sharpe ratio.
    """
    tickers = list(holdings.keys())
    weights = np.array([holdings[t] for t in tickers])

    returns_dict = {}
    for ticker in tickers:
        df = get_stock_history(ticker, period=period)
        if not df.empty and "Close" in df.columns:
            close = df.set_index("Date")["Close"]
            returns_dict[ticker] = close.pct_change().dropna()

    if len(returns_dict) < 2:
        return {}

    returns_df = pd.DataFrame(returns_dict).dropna()
    cov_matrix = returns_df.cov() * 252  # annualized covariance
    corr_matrix = returns_df.corr()

    mean_returns = returns_df.mean() * 252  # annualized returns
    portfolio_return = float(np.dot(weights, mean_returns))
    portfolio_volatility = float(
        np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
    )
    sharpe_ratio = (
        portfolio_return / portfolio_volatility if portfolio_volatility > 0 else 0.0
    )

    return {
        "individual_annual_returns": mean_returns.to_dict(),
        "individual_annual_volatility": (returns_df.std() * np.sqrt(252)).to_dict(),
        "correlation_matrix": corr_matrix.to_dict(),
        "portfolio_annual_return": round(portfolio_return, 4),
        "portfolio_annual_volatility": round(portfolio_volatility, 4),
        "sharpe_ratio": round(sharpe_ratio, 4),
    }


def get_sector_diversity(tickers: List[str]) -> Dict[str, List[str]]:
    """
    Group tickers by their sector using yfinance data.
    Returns a dict of {sector: [tickers]}.
    """
    from tools.market_data import get_financial_metrics

    sector_map: Dict[str, List[str]] = {}
    for ticker in tickers:
        metrics = get_financial_metrics(ticker)
        sector = metrics.get("sector", "Unknown")
        if sector not in sector_map:
            sector_map[sector] = []
        sector_map[sector].append(ticker)

    return sector_map
