from typing import TypedDict, List, Dict, Optional


class TriageState(TypedDict):
    """
    Shared state object passed between all agents in the NetTriage AI graph.
    Each agent reads what it needs from this state and writes its output
    back into it before passing it along to the next node.
    """

    # --- Input ---
    raw_logs: str                      # The raw log text fed in by the user

    # --- Set by Log Ingestion Agent ---
    parsed_logs: Optional[List[Dict]]  # Structured log entries: [{timestamp, source, severity, message}, ...]

    # --- Set by Anomaly Classification Agent ---
    anomaly_score: Optional[float]     # Confidence score (0.0 - 1.0) that something is wrong
    anomaly_flagged: Optional[bool]    # True if anomaly_score crosses the threshold
    anomaly_summary: Optional[str]     # Short explanation of what looked anomalous

    # --- Set by Report Generation Agent (only runs if anomaly_flagged is True) ---
    report: Optional[str]              # Human-readable incident report

    # --- Set by Remediation Agent (only runs if anomaly_flagged is True) ---
    remediation: Optional[str]         # Suggested next steps / fix

    # --- Bookkeeping ---
    errors: Optional[List[str]]        # Collects any errors so one bad agent doesn't crash the run

def format_logs_for_prompt(parsed_logs: list) -> str:
    """Converts structured log entries back into readable text for LLM prompts."""
    return "\n".join(
        f"{entry.get('timestamp')} [{entry.get('severity')}] "
        f"source={entry.get('source')} - {entry.get('message')}"
        for entry in parsed_logs
    )