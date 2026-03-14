# Trade Today

Trade Today is an Indian equity analysis app built around two execution paths:

- `LangGraph` for single-stock analysis such as `Should I buy RELIANCE.NS today?`
- `CrewAI` for multi-stock workflows such as stock comparison and portfolio analysis

The current implementation also exposes a `watchlist-scan` API for scheduled automation and includes local `n8n` in Docker Compose for workflow orchestration.

## Current Status

Implemented in the repo today:

- Single-stock multi-agent analysis with supervisor -> technical, fundamental, sentiment, risk -> judge
- Intent-aware routing between LangGraph and CrewAI
- CrewAI compare and portfolio flows for queries that explicitly mention stocks
- FastAPI endpoints for health, legacy single-stock analysis, smart routing, and watchlist scans
- Streamlit chat UI
- Docker Compose for API, frontend, and n8n

In the architecture docs but not yet wired into the runtime as first-class app features:

- MCP-backed persistence and spreadsheet integrations
- Deeper n8n-driven reporting workflows beyond the current watchlist scan endpoint

The latest architecture reference is [docs/architecture_flowchart.html](./docs/architecture_flowchart.html). It reflects the current direction of the system; a few automation and MCP boxes are still roadmap items rather than fully integrated runtime paths.

## Architecture

### 1. Single-stock path

For prompts such as `Analyze INFY` or `Should I buy RELIANCE.NS?`, the app uses the LangGraph pipeline:

1. `supervisor_node` extracts the ticker
2. Four analysts run in parallel:
   - Technical
   - Fundamental
   - Sentiment
   - Risk
3. The judge synthesizes the reports into a final `BUY`, `HOLD`, or `SELL`

### 2. Multi-stock path

For prompts such as `Compare RELIANCE and TATAMOTORS` or `Analyse my portfolio of RELIANCE, INFY, TCS`, the app:

1. Classifies the query intent
2. Extracts tickers
3. Routes to a CrewAI workflow
4. Uses CrewAI agents to:
   - score each stock
   - analyze correlation and diversification
   - synthesize a compare/portfolio recommendation

### 3. Automation path

The FastAPI app exposes `POST /watchlist-scan`, which is intended for scheduled jobs such as daily pre-market scans from n8n.

## Tech Stack

- `LangGraph` for deterministic single-stock orchestration
- `CrewAI` for multi-stock workflows
- `Google Gemini` for LLM reasoning
- `yfinance` for OHLCV and financial metrics
- `duckduckgo-search` for news lookup
- `FastAPI` for APIs
- `Streamlit` for chat UI
- `Docker Compose` for local multi-service setup
- `n8n` for workflow automation

## Supported Query Types

### LangGraph

- `Should I buy RELIANCE.NS today?`
- `Analyze TCS`
- `How is HDFCBANK today?`

### CrewAI

- `Compare RELIANCE and TATAMOTORS`
- `Which is better, INFY or WIPRO?`
- `Analyse my portfolio of TATAMOTORS, RELIANCE, INFY`
- `Allocate 5L across RELIANCE, TCS and INFY`

Note: the current CrewAI routing expects explicit stock mentions in the query. Sector-only allocation prompts are part of the target architecture but are not fully supported by the current router.

## Project Structure

```text
.
|-- agents/                 # LangGraph analyst and judge nodes
|-- core/
|   |-- classifier.py       # Intent classification and ticker extraction
|   `-- router.py           # LangGraph vs CrewAI routing
|-- crew/
|   `-- portfolio_crew.py   # CrewAI agents, tools, and runners
|-- docs/
|   |-- architecture.md
|   |-- data_flow.md
|   |-- agent_tool_flow.md
|   `-- architecture_flowchart.html
|-- graph/
|   `-- workflow.py         # LangGraph graph builder
|-- tools/
|   |-- market_data.py
|   |-- technical_ind.py
|   |-- search.py
|   `-- correlation.py
|-- api.py                  # FastAPI app
|-- app.py                  # Streamlit app
|-- docker-compose.yml
`-- requirements.txt
```

## Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure environment

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_gemini_api_key
```

### 3. Run the API

```bash
uvicorn api:app --reload --port 8000
```

### 4. Run the Streamlit UI

```bash
streamlit run app.py
```

### 5. Run the full local stack with Docker Compose

```bash
docker compose up --build
```

Services:

- FastAPI: `http://localhost:8000`
- Streamlit: `http://localhost:8501`
- n8n: `http://localhost:5678`

## API Endpoints

### Health

```bash
curl http://localhost:8000/health
```

### Legacy single-stock analysis

```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"query": "Should I buy RELIANCE.NS today?"}'
```

### Intent-aware analysis

```bash
curl -X POST http://localhost:8000/smart-analyze \
  -H "Content-Type: application/json" \
  -d '{"query": "Compare RELIANCE and TATAMOTORS"}'
```

### Watchlist scan for automation

```bash
curl -X POST http://localhost:8000/watchlist-scan \
  -H "Content-Type: application/json" \
  -d '{
    "tickers": ["RELIANCE.NS", "TCS.NS", "INFY.NS"],
    "signal_filter": "BUY"
  }'
```

## Notes On n8n And MCP

- `n8n` is included in Docker Compose and is the intended automation layer for scheduled watchlist scans, notifications, and future reporting flows.
- `MCP` appears in the architecture flowchart as the planned integration layer for persistence and spreadsheet-style tooling, but the current Python runtime does not yet consume MCP servers directly.

## Development Notes

- Use `api.py` as the FastAPI entrypoint.
- `main.py` is legacy and should not be treated as the primary API surface.
- Existing unit tests focus on agents and tools; routing and CrewAI paths still need broader automated coverage.

## Documentation

- [Architecture Blueprint](./docs/architecture.md)
- [Data Flow](./docs/data_flow.md)
- [Agent Tool Flow](./docs/agent_tool_flow.md)
- [Full Architecture Flowchart](./docs/architecture_flowchart.html)
