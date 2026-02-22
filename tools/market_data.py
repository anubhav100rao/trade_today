import yfinance as yf
import pandas as pd
from typing import Dict, Any

def get_stock_history(ticker: str, period: str = "6mo", interval: str = "1d") -> pd.DataFrame:
    """
    Fetches historical OHLCV data for a given ticker.
    Supports Indian stocks if suffixed with .NS (NSE) or .BO (BSE).
    """
    try:
        stock = yf.Ticker(ticker)
        df = stock.history(period=period, interval=interval)
        if df.empty:
            return pd.DataFrame()
        # Reset index to make strictly tabular
        df = df.reset_index()
        # Convert timezone-aware datetime to string if exists
        if "Date" in df.columns or "Datetime" in df.columns:
            date_col = "Date" if "Date" in df.columns else "Datetime"
            df[date_col] = df[date_col].astype(str)
        return df[['Date', 'Open', 'High', 'Low', 'Close', 'Volume']] if 'Date' in df.columns else df[['Datetime', 'Open', 'High', 'Low', 'Close', 'Volume']]
    except Exception as e:
        print(f"Error fetching history for {ticker}: {e}")
        return pd.DataFrame()

def get_financial_metrics(ticker: str) -> Dict[str, Any]:
    """
    Fetches fundamental metrics (P/E, EPS, Market Cap, etc.)
    """
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        metrics = {
            "marketCap": info.get("marketCap"),
            "peRatio": info.get("trailingPE"),
            "forwardPE": info.get("forwardPE"),
            "eps": info.get("trailingEps"),
            "forwardEps": info.get("forwardEps"),
            "dividendYield": info.get("dividendYield"),
            "beta": info.get("beta"),
            "fiftyTwoWeekHigh": info.get("fiftyTwoWeekHigh"),
            "fiftyTwoWeekLow": info.get("fiftyTwoWeekLow"),
            "profitMargins": info.get("profitMargins"),
            "operatingMargins": info.get("operatingMargins"),
            "revenueGrowth": info.get("revenueGrowth"),
            "freeCashflow": info.get("freeCashflow"),
            "debtToEquity": info.get("debtToEquity"),
            "returnOnEquity": info.get("returnOnEquity"),
            "returnOnAssets": info.get("returnOnAssets"),
            "sector": info.get("sector"),
            "industry": info.get("industry")
        }
        return metrics
    except Exception as e:
        print(f"Error fetching metrics for {ticker}: {e}")
        return {}

def get_balance_sheet(ticker: str) -> pd.DataFrame:
    """
    Fetches balance sheet data.
    """
    try:
        stock = yf.Ticker(ticker)
        return stock.balance_sheet
    except Exception as e:
        print(f"Error fetching balance sheet for {ticker}: {e}")
        return pd.DataFrame()

def get_income_statement(ticker: str) -> pd.DataFrame:
    """
    Fetches income statement data.
    """
    try:
        stock = yf.Ticker(ticker)
        return stock.income_stmt
    except Exception as e:
        print(f"Error fetching income stmt for {ticker}: {e}")
        return pd.DataFrame()
