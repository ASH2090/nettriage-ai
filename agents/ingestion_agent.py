import re
from datetime import datetime
from state import TriageState


def ingestion_agent(state: TriageState) -> TriageState:
    """
    Parses raw log text into a structured list of log entries.
    Expects each line in roughly the format:
        2026-06-17 14:32:10 [ERROR] source=auth_service - Failed login attempt
    Falls back gracefully if the format doesn't match exactly.
    """
    raw_logs = state.get("raw_logs", "")
    errors = state.get("errors") or []
    parsed_logs = []

    log_pattern = re.compile(
        r"(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\s+"
        r"\[(?P<severity>\w+)\]\s+"
        r"source=(?P<source>\S+)\s+-\s+"
        r"(?P<message>.+)"
    )

    if not raw_logs.strip():
        errors.append("ingestion_agent: raw_logs was empty")
        return {**state, "parsed_logs": [], "errors": errors}

    for line_number, line in enumerate(raw_logs.strip().splitlines(), start=1):
        line = line.strip()
        if not line:
            continue

        match = log_pattern.match(line)
        if match:
            parsed_logs.append({
                "timestamp": match.group("timestamp"),
                "severity": match.group("severity").upper(),
                "source": match.group("source"),
                "message": match.group("message"),
            })
        else:
            parsed_logs.append({
                "timestamp": None,
                "severity": "UNKNOWN",
                "source": "UNKNOWN",
                "message": line,
            })
            errors.append(f"ingestion_agent: could not parse line {line_number}: '{line}'")

    return {**state, "parsed_logs": parsed_logs, "errors": errors}


# --- Quick standalone test ---
if __name__ == "__main__":
    sample_logs = """2026-06-17 14:32:10 [ERROR] source=auth_service - Failed login attempt for user admin
2026-06-17 14:32:15 [ERROR] source=auth_service - Failed login attempt for user admin
2026-06-17 14:32:20 [ERROR] source=auth_service - Failed login attempt for user admin
2026-06-17 14:35:01 [INFO] source=web_server - Request served in 120ms
this is a malformed line that won't match"""

    test_state: TriageState = {"raw_logs": sample_logs}
    result = ingestion_agent(test_state)

    print("--- Parsed Logs ---")
    for entry in result["parsed_logs"]:
        print(entry)

    print("\n--- Errors ---")
    for err in result.get("errors", []):
        print(err)