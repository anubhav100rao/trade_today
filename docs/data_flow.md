# Data Flow Architecture

This document outlines how data moves through the Trading Analysis Agent system, from the initial user input to the final recommendation.

## 1. Input & Initialization

**Component:** Streamlit UI (`app.py`) -> LangGraph State (`core/state.py`)

1. **User Query:** The user enters a query in the Streamlit chat interface (e.g., "Analyze RELIANCE.NS for a short-term swing trade").
2. **State Creation:** `app.py` initializes a `TradingState` dictionary. The `user_query` is placed into the state, and the remaining fields (like `technical_analysis`, `fundamental_analysis`, etc.) are left blank.
3. **Graph Invocation:** The state is passed as input to the compiled LangGraph workflow defined in `graph/workflow.py`.

## 2. Orchestration & Extraction

**Component:** Supervisor Node (`graph/workflow.py`)

1. **Input:** The current `TradingState` (containing the user query).
2. **Action:** The Supervisor (a lightweight LLM call) reads the `user_query` to extract the exact ticker symbol (e.g., "RELIANCE.NS").
3. **Update State:** The extracted ticker is added to the `ticker` field in the `TradingState`.
4. **Routing:** The Supervisor routes the updated state to the four parallel analyst agents.

## 3. Parallel Analysis (The Swarm)

**Components:** Analyst Agents (`agents/*.py`) and Tools (`tools/*.py`)

The LangGraph system now passes the state to four different nodes *simultaneously*. Each node operates independently:

### A. Technical Analyst (`agents/technical.py`)
1. **Input:** The `ticker` from the state.
2. **Tool Execution:** Calls `tools/market_data.py` to fetch OHLCV (Open, High, Low, Close, Volume) data via Yahoo Finance.
3. **Indicator Calculation:** Passes OHLCV data to `tools/technical_ind.py` to calculate RSI, MACD, and Moving Averages.
4. **LLM Synthesis:** The LLM reads the raw indicators and drafts a technical summary.
5. **Update State:** Writes the summary to `TradingState["technical_analysis"]`.

### B. Fundamental Analyst (`agents/fundamental.py`)
1. **Input:** The `ticker` from the state.
2. **Tool Execution:** Calls `tools/market_data.py` to fetch P/E ratio, EPS, income statements, and balance sheets.
3. **RAG Query (Optional):** If needed, queries the local ChromaDB (`vector_db/ingestion.py`) for specific financial reports.
4. **LLM Synthesis:** The LLM drafts a fundamental health summary.
5. **Update State:** Writes the summary to `TradingState["fundamental_analysis"]`.

### C. Sentiment Analyst (`agents/sentiment.py`)
1. **Input:** The `ticker` from the state.
2. **Tool Execution:** Calls `tools/search.py` (DuckDuckGo) to find the latest news headlines about the company.
3. **LLM Synthesis:** The LLM gauges the sentiment (bullish/bearish) of the headlines.
4. **Update State:** Writes the summary to `TradingState["sentiment_analysis"]`.

### D. Risk Analyst (`agents/risk.py`)
1. **Input:** The `ticker` from the state.
2. **Tool Execution:** Calls `tools/market_data.py` to fetch beta, implied volatility, or compare against a benchmark (like NIFTY 50).
3. **LLM Synthesis:** The LLM assesses the risk profile of the trade.
4. **Update State:** Writes the summary to `TradingState["risk_analysis"]`.

## 4. Synthesis & Final Verdict

**Component:** The Judge Node (`agents/judge.py`)

1. **Synchronization:** The LangGraph system waits until *all four* parallel analysts have finished updating the state.
2. **Input:** The fully populated `TradingState` now contains four separate analysis strings.
3. **Execution:** The Judge (a final LLM call) reads the entire state. It weighs the technical, fundamental, sentiment, and risk aspects. If there are conflicts (e.g., Technical says "buy", Fundamental says "sell"), the Judge's system prompt instructs it on how to weigh the evidence.
4. **Update State:** The Judge drafts a final, cohesive response and a definitive "BUY", "HOLD", or "SELL" rating, writing this to `TradingState["final_recommendation"]`.

## 5. Output to User

**Component:** Streamlit UI (`app.py`)

1. **Return Value:** The LangGraph workflow finishes execution and returns the final `TradingState` back to `app.py`.
2. **Rendering:** `app.py` extracts the individual analysis strings and the `final_recommendation` from the state.
3. **Display:** The UI elegantly displays the findings in expanders, revealing the exact thought process, and then presents the final verdict to the user in the chat window.
