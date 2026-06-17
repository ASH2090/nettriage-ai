from llm_client import get_llm
from state import TriageState

llm = get_llm(temperature=0.3)

REMEDIATION_PROMPT = """You are a security operations engineer recommending next steps.

Incident report:
{report}

Anomaly score: {anomaly_score}

Based on this incident, suggest 3-4 concrete remediation steps an engineer should take right now.
Be specific and actionable (e.g. "block IP X", "reset credentials", "enable rate limiting on Y").
Format as a short numbered list. Do not include any preamble — just the numbered list.
"""


def remediation_agent(state: TriageState) -> TriageState:
    """
    Reads report and anomaly_score from state,
    and writes a list of remediation suggestions back to state.
    """
    report = state.get("report", "No report available.")
    anomaly_score = state.get("anomaly_score", 0.0)
    errors = state.get("errors") or []

    prompt = REMEDIATION_PROMPT.format(report=report, anomaly_score=anomaly_score)

    try:
        response = llm.invoke(prompt)
        remediation_text = response.content.strip()
        return {**state, "remediation": remediation_text, "errors": errors}

    except Exception as e:
        errors.append(f"remediation_agent: failed to generate remediation - {e}")
        return {**state, "remediation": "Remediation generation failed.", "errors": errors}