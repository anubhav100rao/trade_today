# Implementation Todo List

## Phase 1: Project Setup & Core Logic
- [x] Initialize Python virtual environment (`python -m venv venv` and `source venv/bin/activate`).
- [x] Create `requirements.txt` with dependencies: `langchain`, `langgraph`, `langchain-google-genai`, `yfinance`, `duckduckgo-search`, `streamlit`, `chromadb`, `pandas`.
- [x] Configure environment variables (create `.env` file for `GEMINI_API_KEY`).
- [x] Define the LangGraph State (`TradingState` using `TypedDict`).

## Phase 2: Tools Development
- [x] Implement `yfinance` tool functions (History prices, Fundamentals/Ratios, Balance Sheet).
- [x] Implement Technical Indicators logic (Moving Averages, RSI, MACD using pandas).
- [x] Implement DuckDuckGo search tool wrapper for fetching live financial news.
- [x] Setup local ChromaDB/FAISS pipeline for basic Document indexing (RAG foundation).

## Phase 2.5: Tools Testing
- [x] Write pytest unit and integration tests for tools (`tests/test_tools.py`).

## Phase 3: Agent Creation (Gemini-powered)
- [x] Build **Technical Analyst Agent**: System prompt + yfinance technical tools.
- [x] Build **Fundamental Analyst Agent**: System prompt + yfinance fundamental tools.
- [x] Build **Sentiment Analyst Agent**: System prompt + DuckDuckGo news tool.
- [x] Build **Risk Analyst Agent**: System prompt + volatility calculation tools.
- [x] Build **The Judge Node**: System prompt designed to synthesize the state and produce the final verdict.

## Phase 3.5: Agent Testing
- [x] Write pytest unit tests for agents (`tests/test_agents.py`) using mocked LLM calls to save Gemini credits.

## Phase 4: LangGraph Orchestration
- [x] Create the LangGraph `StateGraph`.
- [x] Add all nodes (Supervisor, the 4 Parallel Analysts, The Judge).
- [x] Design graph edges: Supervisor routing -> Parallel execution of Analysts -> Join at The Judge.
- [x] Compile the graph.
- [x] Write a simple CLI script (`test_graph.py`) to verify the execution trace using a sample Indian ticker (e.g., `RELIANCE.NS`).

## Phase 5: Streamlit Interface
- [x] Setup basic Streamlit scaffolding (`app.py`).
- [x] Integrate chat input/output natively with the LangGraph execution.
- [x] Add sidebar for basic settings (API key override, debugging toggles).
- [x] Create expanders in the UI to display individual agent findings before summarizing the final verdict.

## Phase 6: Refinement & Testing
- [ ] Test the pipeline with diverse Indian stocks across multiple sectors.
- [ ] Tune and refine individual agent prompts to optimize reasoning and minimize hallucinations.
- [ ] Add basic error handling (e.g., invalid ticker formats, API timeout resilience).
