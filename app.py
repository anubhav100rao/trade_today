import streamlit as st
import os
from graph.workflow import build_graph
import uuid

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
if prompt := st.chat_input("Ask about a stock (e.g., 'Should I buy RELIANCE.NS?')"):
    # Add user message to state
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        status_placeholder = st.empty()
        status_placeholder.info("Initializing Swarm...")
        
        # Build Graph
        try:
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

            # To store expanders for the current response
            expanders_data = []
            
            # Placeholders for expanders to update them dynamically
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
                            
        except Exception as e:
            status_placeholder.error(f"An error occurred: {str(e)}")
            st.session_state.messages.append({"role": "assistant", "content": f"Error: {str(e)}"})
