from flask import Flask, request, jsonify
from main import build_graph

app = Flask(__name__)
graph = build_graph()


@app.route("/", methods=["GET"])
def health_check():
    return jsonify({"status": "ok", "service": "NetTriage AI"})


@app.route("/triage", methods=["POST"])
def triage():
    """
    Accepts JSON: { "logs": "raw log text here" }
    Returns the full pipeline result: parsed logs, anomaly classification,
    incident report, and remediation steps (if an anomaly was flagged).
    """
    data = request.get_json(silent=True)

    if not data or "logs" not in data:
        return jsonify({"error": "Request body must be JSON with a 'logs' field"}), 400

    raw_logs = data["logs"]

    if not isinstance(raw_logs, str) or not raw_logs.strip():
        return jsonify({"error": "'logs' must be a non-empty string"}), 400

    try:
        result = graph.invoke({"raw_logs": raw_logs})
    except Exception as e:
        return jsonify({"error": f"Pipeline execution failed: {str(e)}"}), 500

    response = {
        "anomaly_flagged": result.get("anomaly_flagged", False),
        "anomaly_score": result.get("anomaly_score"),
        "anomaly_summary": result.get("anomaly_summary"),
        "parsed_logs": result.get("parsed_logs"),
        "report": result.get("report"),
        "remediation": result.get("remediation"),
        "errors": result.get("errors", []),
    }

    return jsonify(response), 200


if __name__ == "__main__":
    app.run(debug=True, port=5000)