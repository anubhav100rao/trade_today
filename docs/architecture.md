# Trading Analysis Agent for Indian Markets - Architecture Blueprint

## Overview
A Multi-Agent system to analyze Indian stocks using Gemini, LangGraph, and other free, easily accessible tools. The architecture focuses on cost-effectiveness while maintaining high performance.

## Core Components

### 1. Language Model (LLM)
* **Model**: Google Gemini (via `langchain-google-genai`)
* **Purpose**: Used for planning, reasoning, summarizing, and final judgment across all agents. Provides excellent capabilities with a generous free tier or API key access.

### 2. User Interface
* **Component**: Streamlit
* **Why**: It is free, native to Python, and allows for rapid creation of interactive chat interfaces without needing dedicated frontend code.

### 3. Orchestration & Framework
* **Orchestrator**: LangGraph
  * State management using a `TypedDict`.
  * Parallel execution of the various analyst agents to reduce latency.
* **Agent Framework**: LangChain
  * Provides the standard wrappers for the LLMs, tools, and RAG pipelines.

### 4. Vector Database (RAG)
* **Component**: ChromaDB or FAISS 
* **Why**: These are free, open-source, and can run locally. They eliminate the need for paid cloud vector databases while still providing robust embeddings storage for document retrieval.

### 5. Tools & Data Sources (Free Alternatives)
* **Market Data**: `yfinance` (Yahoo Finance Python API)
  * Seamlessly supports Indian stocks (e.g., `RELIANCE.NS`, `TCS.BO`).
  * Replaces complex MCPs with direct tool execution. Provides OHLCV data, P/E ratios, EPS, and balance sheets.
* **Web & News Search**: DuckDuckGo Search (`duckduckgo-search` library)
  * Allows free web scraping for news and sentiment analysis without API limits/quotas.
* **Financial Reports**: 
  * Leveraging `yfinance` for basic financials or local PDF ingestion via LangChain document loaders (annual reports scraped from NSE/BSE).

## Execution Flow

1. **User Query**: The Streamlit UI captures a query like *"Should I invest in HDFC Bank right now?"*
2. **Supervisor Node**: The LangGraph router invokes Gemini to extract the ticker target (ensuring Indian suffixes like `.NS` are added) and initializes the `State`.
3. **Parallel Agents execution**:
   * **Technical Analyst**: Uses Gemini + `yfinance` tools to retrieve price history and calculate MAs/RSI.
   * **Fundamental Analyst**: Uses Gemini + `yfinance` fundamental data (and local RAG when needed) to check company health.
   * **Sentiment Analyst**: Uses Gemini + `DuckDuckGo` to search recent news and determine market mood.
   * **Risk Analyst**: Examines market context (e.g., NIFTY50 performance vs the stock) and volatility.
4. **The Judge**: A final Gemini node that reads the `State` populated by the 4 analysts, resolves any conflicts, and outputs a concrete Buy/Hold/Sell recommendation.
5. **Output**: The entire thought process and the final verdict are rendered beautifully on the Streamlit interface.
