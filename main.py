from langgraph.graph import StateGraph, END
from state import TriageState
from agents.ingestion_agent import ingestion_agent
from agents.classification_agent import classification_agent
from agents.report_agent import report_agent
from agents.remediation_agent import remediation_agent


def route_after_classification(state: TriageState) -> str:
    """
    Conditional routing function. LangGraph calls this after the
    classification node runs, and uses its return value to decide
    which node to go to next.
    """
    if state.get("anomaly_flagged"):
        return "report"
    return "end_no_incident"


def build_graph():
    graph = StateGraph(TriageState)

    # Register each agent function as a node
    graph.add_node("ingestion", ingestion_agent)
    graph.add_node("classification", classification_agent)
    graph.add_node("report", report_agent)
    graph.add_node("remediation", remediation_agent)

    # Entry point: always start at ingestion
    graph.set_entry_point("ingestion")

    # Simple edges: ingestion always leads to classification
    graph.add_edge("ingestion", "classification")

    # Conditional edge: after classification, branch based on the flag
    graph.add_conditional_edges(
        "classification",
        route_after_classification,
        {
            "report": "report",            # if flagged -> go to report agent
            "end_no_incident": END,        # if not flagged -> stop here
        },
    )

    # After report, always run remediation, then stop
    graph.add_edge("report", "remediation")
    graph.add_edge("remediation", END)

    return graph.compile()


# --- Quick standalone test ---
if __name__ == "__main__":
    app = build_graph()

    # Test case 1: should trigger the full pipeline (anomaly present)
    suspicious_logs = """2026-06-17 14:32:10 [ERROR] source=auth_service - Failed login attempt for user admin
2026-06-17 14:32:15 [ERROR] source=auth_service - Failed login attempt for user admin
2026-06-17 14:32:20 [ERROR] source=auth_service - Failed login attempt for user admin
2026-06-17 14:32:25 [ERROR] source=auth_service - Failed login attempt for user admin
2026-06-17 14:32:30 [ERROR] source=auth_service - Failed login attempt for user admin"""

    print("=" * 60)
    print("TEST 1: Suspicious logs (should run full pipeline)")
    print("=" * 60)
    result = app.invoke({"raw_logs": suspicious_logs})
    print("Anomaly Flagged:", result.get("anomaly_flagged"))
    print("Report present:", "report" in result and result["report"] is not None)
    print("Remediation present:", "remediation" in result and result["remediation"] is not None)
    if result.get("report"):
        print("\n--- Report ---")
        print(result["report"])
    if result.get("remediation"):
        print("\n--- Remediation ---")
        print(result["remediation"])

    # Test case 2: should stop early (normal logs, no anomaly)
    normal_logs = """2026-06-17 09:00:01 [INFO] source=web_server - Request served in 80ms
2026-06-17 09:00:15 [INFO] source=web_server - Request served in 95ms
2026-06-17 09:01:02 [INFO] source=web_server - Request served in 70ms"""

    print("\n" + "=" * 60)
    print("TEST 2: Normal logs (should stop after classification)")
    print("=" * 60)
    result2 = app.invoke({"raw_logs": normal_logs})
    print("Anomaly Flagged:", result2.get("anomaly_flagged"))
    print("Report present:", result2.get("report") is not None)
    print("Remediation present:", result2.get("remediation") is not None)