from llm_client import get_llm
from state import TriageState, format_logs_for_prompt


llm = get_llm(temperature=0.3)

REPORT_PROMPT = """You are a security operations engineer writing an incident report.

Anomaly summary: {anomaly_summary}
Anomaly score: {anomaly_score}

Relevant log entries:
{logs}

Write a clear, professional incident report covering:
1. What happened (brief title)
2. Timeline of events
3. Severity assessment
4. Affected systems/sources

Keep it concise — 4-6 sentences total. Do not include any preamble like "Here is the report" — just write the report itself.
"""


def report_agent(state: TriageState) -> TriageState:
    """
    Reads anomaly_summary, anomaly_score, and parsed_logs from state,
    and writes a human-readable incident report back to state.
    """
    parsed_logs = state.get("parsed_logs") or []
    anomaly_summary = state.get("anomaly_summary", "Unknown anomaly")
    anomaly_score = state.get("anomaly_score", 0.0)
    errors = state.get("errors") or []

    logs_text = "\n".join(
        f"{entry.get('timestamp')} [{entry.get('severity')}] "
        f"source={entry.get('source')} - {entry.get('message')}"
        for entry in parsed_logs
    )

    prompt = REPORT_PROMPT.format(
        anomaly_summary=anomaly_summary,
        anomaly_score=anomaly_score,
        logs=logs_text,
    )

    try:
        response = llm.invoke(prompt)
        report_text = response.content.strip()
        return {**state, "report": report_text, "errors": errors}

    except Exception as e:
        errors.append(f"report_agent: failed to generate report - {e}")
        return {**state, "report": "Report generation failed.", "errors": errors}