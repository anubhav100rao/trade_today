import streamlit as st
import os
from graph.workflow import build_graph
from core.classifier import classify_intent, extract_tickers
from crew.portfolio_crew import run_compare_stocks_crew, run_portfolio_crew

# --- Setup Streamlit Page ---
st.set_page_config(page_title="Trade Today AI", layout="wide", page_icon="📈")
st.title("📈 Trade Today - AI Trading Swarm")

# --- Sidebar ---
with st.sidebar:
    st.header("Settings")
    api_key = st.text_input("Gemini API Key override (optional)", type="password")
    if api_key:
        os.environ["GEMINI_API_KEY"] = api_key
    
    debug_mode = st.toggle("Debug Mode", value=False)
    st.markdown("---")
    st.markdown("This application uses a multi-agent swarm to analyze stocks (Technical, Fundamental, Sentiment, Risk) and provide a final verdict.")

# --- Session State ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if "expanders" in message:
            for title, content in message["expanders"]:
                with st.expander(title):
                    st.markdown(content)
        st.markdown(message["content"])

# --- Chat Input ---
if prompt := st.chat_input("Ask about stocks (e.g., 'Analyze RELIANCE' or 'Compare TCS vs INFY')"):
    # Add user message to state
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        status_placeholder = st.empty()
        status_placeholder.info("🔍 Classifying your query...")

        try:
            # Step 1: Classify intent
            intent = classify_intent(prompt)

            if debug_mode:
                st.sidebar.write(f"Detected intent: {intent}")

            # ============================================
            # PATH A: Single Stock Analysis (existing flow)
            # ============================================
            if intent == "single_stock_analysis":
                status_placeholder.info("Initializing Single-Stock Swarm...")
                app = build_graph()

                initial_state = {
                    "user_query": prompt,
                    "ticker": "",
                    "technical_analysis": "",
                    "fundamental_analysis": "",
                    "sentiment_analysis": "",
                    "risk_analysis": "",
                    "final_recommendation": "",
                    "messages": []
                }

                expanders_data = []
                st_expanders = {
                    "supervisor": st.empty(),
                    "technical_analyst": st.empty(),
                    "fundamental_analyst": st.empty(),
                    "sentiment_analyst": st.empty(),
                    "risk_analyst": st.empty()
                }
                verdict_placeholder = st.empty()

                for step in app.stream(initial_state):
                    for node_name, state_update in step.items():
                        if debug_mode:
                            st.sidebar.write(f"Node completed: {node_name}")
                            st.sidebar.json(state_update)

                        if node_name == "supervisor":
                            ticker = state_update.get("ticker", "Unknown")
                            status_placeholder.info(f"Supervisor identified ticker: **{ticker}**")
                            summary = f"Identified Ticker: {ticker}"
                            expanders_data.append(("Supervisor", summary))
                            with st_expanders["supervisor"].container():
                                with st.expander("Supervisor Context"):
                                    st.write(summary)

                        elif node_name == "technical_analyst":
                            analysis = state_update.get("technical_analysis", "")
                            status_placeholder.info("Technical Analyst completed analysis.")
                            expanders_data.append(("Technical Analysis", analysis))
                            with st_expanders["technical_analyst"].container():
                                with st.expander("Technical Analysis", icon="📊"):
                                    st.write(analysis)

                        elif node_name == "fundamental_analyst":
                            analysis = state_update.get("fundamental_analysis", "")
                            status_placeholder.info("Fundamental Analyst completed analysis.")
                            expanders_data.append(("Fundamental Analysis", analysis))
                            with st_expanders["fundamental_analyst"].container():
                                with st.expander("Fundamental Analysis", icon="🏢"):
                                    st.write(analysis)

                        elif node_name == "sentiment_analyst":
                            analysis = state_update.get("sentiment_analysis", "")
                            status_placeholder.info("Sentiment Analyst completed analysis.")
                            expanders_data.append(("Sentiment Analysis", analysis))
                            with st_expanders["sentiment_analyst"].container():
                                with st.expander("Sentiment Analysis", icon="📰"):
                                    st.write(analysis)

                        elif node_name == "risk_analyst":
                            analysis = state_update.get("risk_analysis", "")
                            status_placeholder.info("Risk Analyst completed analysis.")
                            expanders_data.append(("Risk Analysis", analysis))
                            with st_expanders["risk_analyst"].container():
                                with st.expander("Risk Analysis", icon="⚠️"):
                                    st.write(analysis)

                        elif node_name == "judge":
                            status_placeholder.success("Judge finalized recommendation.")
                            verdict = state_update.get("final_recommendation", "")
                            verdict_placeholder.markdown("### 🧑‍⚖️ The Verdict\n" + verdict)

                            st.session_state.messages.append({
                                "role": "assistant",
                                "content": "### 🧑‍⚖️ The Verdict\n" + verdict,
                                "expanders": expanders_data
                            })

            # ============================================
            # PATH B: Multi-Stock (CrewAI) — Compare / Portfolio
            # ============================================
            else:
                intent_labels = {
                    "compare_stocks": "📊 Stock Comparison",
                    "portfolio_allocation": "💰 Portfolio Allocation",
                    "portfolio_analysis": "📋 Portfolio Analysis",
                }
                label = intent_labels.get(intent, "Multi-Stock Analysis")
                status_placeholder.info(f"Detected: **{label}** — extracting tickers...")

                # Extract tickers from query
                tickers = extract_tickers(prompt)

                if not tickers:
                    status_placeholder.error(
                        "Could not extract stock tickers from your query. "
                        "Please mention specific stock names (e.g., RELIANCE, TCS, INFY)."
                    )
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": "❌ Could not extract stock tickers. Please mention specific stock names."
                    })
                else:
                    st.info(f"**Stocks detected:** {', '.join(tickers)}")
                    status_placeholder.info(
                        f"🚀 Launching CrewAI {label} crew for {', '.join(tickers)}... "
                        f"This may take a minute as each stock is analyzed individually."
                    )

                    # Run the appropriate crew
                    if intent == "compare_stocks":
                        crew_result = run_compare_stocks_crew(tickers, prompt)
                    else:
                        crew_result = run_portfolio_crew(tickers, prompt)

                    status_placeholder.success(f"{label} complete!")

                    # Display crew result
                    st.markdown(f"### {label} Result")
                    st.markdown(crew_result)

                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": f"### {label} Result\n\n{crew_result}"
                    })

        except Exception as e:
            status_placeholder.error(f"An error occurred: {str(e)}")
            st.session_state.messages.append({"role": "assistant", "content": f"Error: {str(e)}"})
