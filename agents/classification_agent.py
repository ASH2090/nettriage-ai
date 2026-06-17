import json
from llm_client import get_llm
from state import TriageState

llm = get_llm(temperature=0)

CLASSIFICATION_PROMPT = """You are a network security analyst reviewing parsed log entries.

Given the following structured log entries, decide whether they represent a genuine anomaly
(e.g. repeated failed logins, unusual error spikes, signs of an attack) or normal/benign activity.

Log entries:
{logs}

Respond with ONLY a valid JSON object in this exact format, no other text:
{{
  "anomaly_score": <float between 0.0 and 1.0>,
  "anomaly_flagged": <true or false>,
  "anomaly_summary": "<one sentence explanation>"
}}
"""


def classification_agent(state: TriageState) -> TriageState:
    """
    Reads parsed_logs from state, asks the LLM to assess anomaly risk,
    and writes anomaly_score, anomaly_flagged, anomaly_summary back to state.
    """
    parsed_logs = state.get("parsed_logs") or []
    errors = state.get("errors") or []

    if not parsed_logs:
        errors.append("classification_agent: no parsed_logs to classify")
        return {
            **state,
            "anomaly_score": 0.0,
            "anomaly_flagged": False,
            "anomaly_summary": "No logs available to analyze.",
            "errors": errors,
        }

    logs_text = "\n".join(
        f"{entry.get('timestamp')} [{entry.get('severity')}] "
        f"source={entry.get('source')} - {entry.get('message')}"
        for entry in parsed_logs
    )

    prompt = CLASSIFICATION_PROMPT.format(logs=logs_text)

    try:
        response = llm.invoke(prompt)
        content = response.content.strip()

        if content.startswith("```"):
            content = content.strip("`").replace("json", "", 1).strip()

        result = json.loads(content)

        return {
            **state,
            "anomaly_score": float(result["anomaly_score"]),
            "anomaly_flagged": bool(result["anomaly_flagged"]),
            "anomaly_summary": result["anomaly_summary"],
            "errors": errors,
        }

    except (json.JSONDecodeError, KeyError, ValueError) as e:
        errors.append(f"classification_agent: failed to parse LLM response - {e}")
        return {
            **state,
            "anomaly_score": 0.0,
            "anomaly_flagged": False,
            "anomaly_summary": "Classification failed due to a parsing error.",
            "errors": errors,
        }


# --- Quick standalone test ---
if __name__ == "__main__":
    from agents.ingestion_agent import ingestion_agent

    sample_logs = """2026-06-17 14:32:10 [ERROR] source=auth_service - Failed login attempt for user admin
2026-06-17 14:32:15 [ERROR] source=auth_service - Failed login attempt for user admin
2026-06-17 14:32:20 [ERROR] source=auth_service - Failed login attempt for user admin
2026-06-17 14:32:25 [ERROR] source=auth_service - Failed login attempt for user admin
2026-06-17 14:32:30 [ERROR] source=auth_service - Failed login attempt for user admin"""

    state: TriageState = {"raw_logs": sample_logs}
    state = ingestion_agent(state)
    state = classification_agent(state)

    print("Anomaly Score:", state["anomaly_score"])
    print("Anomaly Flagged:", state["anomaly_flagged"])
    print("Summary:", state["anomaly_summary"])
    print("Errors:", state.get("errors"))