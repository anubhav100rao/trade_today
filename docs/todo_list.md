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
- [ ] Build **Technical Analyst Agent**: System prompt + yfinance technical tools.
- [ ] Build **Fundamental Analyst Agent**: System prompt + yfinance fundamental tools.
- [ ] Build **Sentiment Analyst Agent**: System prompt + DuckDuckGo news tool.
- [ ] Build **Risk Analyst Agent**: System prompt + volatility calculation tools.
- [ ] Build **The Judge Node**: System prompt designed to synthesize the state and produce the final verdict.

## Phase 4: LangGraph Orchestration
- [ ] Create the LangGraph `StateGraph`.
- [ ] Add all nodes (Supervisor, the 4 Parallel Analysts, The Judge).
- [ ] Design graph edges: Supervisor routing -> Parallel execution of Analysts -> Join at The Judge.
- [ ] Compile the graph.
- [ ] Write a simple CLI script (`test_graph.py`) to verify the execution trace using a sample Indian ticker (e.g., `RELIANCE.NS`).

## Phase 5: Streamlit Interface
- [ ] Setup basic Streamlit scaffolding (`app.py`).
- [ ] Integrate chat input/output natively with the LangGraph execution.
- [ ] Add sidebar for basic settings (API key override, debugging toggles).
- [ ] Create expanders in the UI to display individual agent findings before summarizing the final verdict.

## Phase 6: Refinement & Testing
- [ ] Test the pipeline with diverse Indian stocks across multiple sectors.
- [ ] Tune and refine individual agent prompts to optimize reasoning and minimize hallucinations.
- [ ] Add basic error handling (e.g., invalid ticker formats, API timeout resilience).
