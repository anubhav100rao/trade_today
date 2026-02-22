# Trading Analysis Agent for Indian Markets

A Multi-Agent system to analyze Indian stocks using Gemini, LangGraph, and free, easily accessible tools natively focusing on cost-effectiveness while maintaining high performance. 

This project orchestrates multiple specialized AI analysts to evaluate an equity and finalize a recommendation.

## 🚀 Overview

When a user asks about a stock (e.g., "Should I invest in RELIANCE.NS right now?"), the system uses a **Supervisor Node** to route the query to 4 parallel analyst agents:

1. **Technical Analyst**: Analyzes price action and technical indicators (SMA, EMA, RSI, MACD).
2. **Fundamental Analyst**: Evaluates company health, P/E ratio, EPS, margins, and valuation ratios.
3. **Sentiment Analyst**: Scrapes recent news headlines to gauge the overall market mood.
4. **Risk Analyst**: Assesses the volatility, beta, and general risk profile of the stock.

Once all analysts complete their independent checks, **The Judge Node** synthesizes the reports, resolves any conflicting signals, and outputs a final recommendation: **BUY**, **HOLD**, or **SELL**.

## 🏗️ Architecture Stack

- **Orchestration**: LangGraph (State management and parallel execution).
- **LLM Engine**: Google Gemini (via `langchain-google-genai`).
- **Data & Tools**: 
  - `yfinance` for OHLCV data, history, and financial metrics.
  - DuckDuckGo (`duckduckgo-search`) for real-time web scraping without API limits.
- **RAG/Vector DB**: ChromaDB / FAISS for local document retrieval (financial reports).
- **Interface**: Streamlit for the main UI and FastAPI for API endpoints.

> *For detailed breakdowns on the data flow and agent tools, explore the [`docs/`](./docs) directory.*

## 🛠️ Getting Started

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables
Create a `.env` file in the root directory and add your Gemini API Key:
```env
GEMINI_API_KEY=your_gemini_api_key
```

### 3. Run the FastAPI Server
Make sure port `8000` is free, then start the FastAPI application:
```bash
# Optional: Kill any process running on port 8000
lsof -ti:8000 | xargs kill -9 

# Start the uvicorn server
uvicorn api:app --reload --port 8000
```

### 4. API Endpoints

#### Health Check
```bash
curl http://localhost:8000/health
```

#### Analyze a Stock via POST
```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"query": "Should I buy RELIANCE.NS?", "api_key": ""}'
```
