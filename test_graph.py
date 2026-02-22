from graph.workflow import build_graph
import pprint

def main():
    print("Initializing Multi-Agent Trading Swarm...")
    app = build_graph()
    
    print("\n" + "="*50)
    print("Welcome to Trade Today CLI")
    print("="*50)
    
    query = 'Should I buy RELIANCE.NS?'
            
    initial_state = {
        "user_query": query,
        "ticker": "",
        "technical_analysis": "",
        "fundamental_analysis": "",
        "sentiment_analysis": "",
        "risk_analysis": "",
        "final_recommendation": "",
        "messages": []
    }
        
    print("\n[Orchestrator] Triggering workflow...")
    
    # Stream the graph execution to see the steps
    for step in app.stream(initial_state):
        for node_name, state_update in step.items():
            print(f"--- Completed Node: {node_name} ---")
            
            # Print specific state updates to see exactly what each agent learned
            if node_name == "supervisor":
                print(f"Extracted Ticker: {state_update.get('ticker')}")
            elif node_name == "technical_analyst":
                print(f"Technical summary drafted.")
            elif node_name == "fundamental_analyst":
                print(f"Fundamental summary drafted.")
            elif node_name == "sentiment_analyst":
                print(f"Sentiment summary drafted.")
            elif node_name == "risk_analyst":
                print(f"Risk summary drafted.")
            elif node_name == "judge":
                print("\n[THE VERDICT]")
                print(state_update.get("final_recommendation", ""))
    print("\n" + "="*50)

if __name__ == "__main__":
    main()
