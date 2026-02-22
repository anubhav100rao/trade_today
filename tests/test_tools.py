import pytest
import pandas as pd
import numpy as np
import time

# Import functions from our phase 2 tools
from tools.market_data import get_stock_history, get_financial_metrics, get_balance_sheet, get_income_statement
from tools.technical_ind import calculate_sma, add_all_indicators
from tools.search import search_financial_news, search_web
from vector_db.ingestion import index_text, search_db, HAS_CHROMA

# We use a well-known, high-volume Indian stock for our integration tests
TEST_TICKER = "RELIANCE.NS"

# --- Tests for tools/market_data.py ---

def test_get_stock_history():
    """
    Test that we can retrieve historical OHLCV data for a ticker.
    It should return a DataFrame with specific columns and not be empty.
    """
    df = get_stock_history(TEST_TICKER, period="1mo", interval="1d")
    
    # Assert we get a pandas DataFrame back
    assert isinstance(df, pd.DataFrame)
    
    # Assert it's not empty
    assert not df.empty
    
    # Assert it contains the expected columns
    expected_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
    for col in expected_cols:
        assert col in df.columns

def test_get_financial_metrics():
    """
    Test that we can retrieve fundamental metrics for a ticker.
    It should return a dictionary with some known keys like 'marketCap'.
    """
    metrics = get_financial_metrics(TEST_TICKER)
    
    # Assert we get a dictionary
    assert isinstance(metrics, dict)
    
    # Assert we at least got some data back (e.g. marketCap is a common one)
    assert 'marketCap' in metrics
    # Verify that the value for marketCap is present (not None) if the API worked
    if metrics['marketCap'] is not None:
        assert isinstance(metrics['marketCap'], (int, float))

def test_get_balance_sheet():
    """
    Test that we can fetch the balance sheet and it returns a DataFrame.
    """
    bs = get_balance_sheet(TEST_TICKER)
    assert isinstance(bs, pd.DataFrame)
    # yfinance sometimes returns an empty DataFrame if data is missing, 
    # but the type should always be correct.

# --- Tests for tools/technical_ind.py ---

def test_add_all_indicators():
    """
    Test calculating technical indicators.
    We create a dummy DataFrame to ensure the math functions don't fail,
    simulating a stock's closing prices.
    """
    # Create a dummy DataFrame with 30 days of closing prices
    data = {'Close': np.random.rand(30) * 100}
    df = pd.DataFrame(data)
    
    # Process indicators
    df_with_inds = add_all_indicators(df)
    
    # Assert the new columns were added successfully
    expected_ind_cols = ['SMA_20', 'SMA_50', 'EMA_20', 'RSI_14', 'MACD_Line', 'MACD_Signal', 'MACD_Hist']
    for col in expected_ind_cols:
        assert col in df_with_inds.columns

# --- Tests for tools/search.py ---

def test_search_financial_news():
    """
    Test that DuckDuckGo search fetches news successfully.
    We avoid hitting rate limits by just running a small query.
    """
    time.sleep(1) # Sleep briefly to avoid DDGS rate limits
    news = search_financial_news("Reliance Industries stock", max_results=2)
    
    # Assert we got a list back
    assert isinstance(news, list)
    
    # If the network call succeeded and found news, assert structure
    if len(news) > 0:
        first_item = news[0]
        assert "title" in first_item
        assert "snippet" in first_item

def test_search_web():
    """
    Test general web search via DuckDuckGo.
    """
    time.sleep(1) # Sleep briefly to avoid DDGS rate limits
    results = search_web("Indian stock market", max_results=2)
    
    assert isinstance(results, list)
    if len(results) > 0:
        assert "title" in results[0]
        assert "url" in results[0]

# --- Tests for vector_db/ingestion.py ---

@pytest.mark.skipif(not HAS_CHROMA, reason="VectorDB not available")
def test_faiss_ingestion_and_search():
    """
    Test that we can index a document into local FAISS and search for it.
    """
    test_collection = "test_financial_docs"
    test_text = "Reliance Industries announced a massive profit margin this quarter."
    test_metadata = {"source": "fake_news", "ticker": "RELIANCE.NS"}
    test_id = "doc1"
    
    # Index the document
    index_text(test_text, test_metadata, test_id, collection=test_collection)
    
    # Search the vector DB for a related term
    results = search_db("profit margin", n_results=1, collection=test_collection)
    
    # Assert that the results dictionary contains our document
    assert results is not None
    assert 'documents' in results
    assert len(results['documents']['0'] if isinstance(results['documents'], dict) else results['documents'][0]) > 0
    
    # Check if the document retrieved matches our indexed text
    retrieved_docs = results['documents'][0]
    assert test_text in retrieved_docs
