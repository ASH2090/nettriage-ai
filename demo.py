"""
NetTriage AI — Live Demo Script
Generates realistic, randomized network logs and sends them to the
live API for real-time triage. Different every run.
"""

import random
import requests
import json
import sys
from datetime import datetime, timedelta

# --- Configuration ---
API_URL = "https://nettriage-ai.onrender.com/triage"
# For local testing, uncomment this instead:
# API_URL = "http://127.0.0.1:5000/triage"


def random_timestamp(base: datetime, offset_seconds: int) -> str:
    """Generate a timestamp offset from a base time."""
    ts = base + timedelta(seconds=offset_seconds)
    return ts.strftime("%Y-%m-%d %H:%M:%S")


def generate_normal_logs(base: datetime, count: int = 3) -> list:
    """Generate benign, everyday traffic logs."""
    services = ["web_server", "api_gateway", "load_balancer", "cdn_edge"]
    endpoints = [
        "GET /index.html 200 OK",
        "GET /api/users 200 OK",
        "POST /api/login 200 OK",
        "GET /static/logo.png 200 OK",
        "GET /api/health 200 OK",
        "POST /api/data 201 Created",
    ]
    logs = []
    for i in range(count):
        ts = random_timestamp(base, i * random.randint(5, 30))
        service = random.choice(services)
        endpoint = random.choice(endpoints)
        latency = random.randint(40, 200)
        logs.append(f"{ts} [INFO] source={service} - {endpoint} in {latency}ms")
    return logs


def generate_brute_force(base: datetime) -> list:
    """Simulate a brute-force login attack."""
    ip = f"{random.randint(10,200)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,254)}"
    users = random.choice(["admin", "root", "administrator", "sysadmin"])
    logs = []
    for i in range(random.randint(5, 8)):
        ts = random_timestamp(base, i * random.randint(3, 7))
        logs.append(f"{ts} [ERROR] source=auth_service - Failed login attempt for user {users} from {ip}")
    return logs


def generate_port_scan(base: datetime) -> list:
    """Simulate a port scanning attack."""
    ip = f"{random.randint(10,200)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,254)}"
    ports = random.sample([21, 22, 23, 25, 53, 80, 110, 143, 443, 993, 3306, 3389, 5432, 5900, 6379, 8080, 8443, 27017], k=random.randint(6, 10))
    logs = []
    for i, port in enumerate(ports):
        ts = random_timestamp(base, i)
        logs.append(f"{ts} [WARNING] source=firewall - Connection attempt on port {port} from {ip}")
    return logs


def generate_data_exfiltration(base: datetime) -> list:
    """Simulate suspicious data exfiltration activity."""
    ip = f"{random.randint(100,220)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,254)}"
    user = random.choice(["dbadmin", "backup_svc", "analytics_user", "etl_worker"])
    data_size = random.randint(200, 900)
    table = random.choice(["customers", "transactions", "user_credentials", "payment_info", "employee_records"])
    logs = [
        f"{random_timestamp(base, 0)} [WARNING] source=db_server - Unusual query volume from user {user}",
        f"{random_timestamp(base, 15)} [ERROR] source=db_server - Large data export triggered by user {user} {data_size}MB",
        f"{random_timestamp(base, 30)} [ERROR] source=db_server - Bulk SELECT on {table} table by user {user}",
        f"{random_timestamp(base, 45)} [CRITICAL] source=db_server - External connection attempt to backup database from {ip}",
    ]
    return logs


def generate_privilege_escalation(base: datetime) -> list:
    """Simulate a privilege escalation attempt."""
    user = random.choice(["jsmith", "temp_contractor", "intern_01", "guest_user"])
    logs = [
        f"{random_timestamp(base, 0)} [WARNING] source=auth_service - User {user} attempted to access /admin/settings",
        f"{random_timestamp(base, 10)} [ERROR] source=auth_service - User {user} attempted role change to SUPERADMIN",
        f"{random_timestamp(base, 20)} [CRITICAL] source=auth_service - Unauthorized sudo command executed by {user}",
        f"{random_timestamp(base, 25)} [CRITICAL] source=auth_service - User {user} modified /etc/passwd",
    ]
    return logs


def generate_ddos(base: datetime) -> list:
    """Simulate a DDoS attack pattern."""
    ips = [f"{random.randint(10,220)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,254)}" for _ in range(4)]
    logs = []
    for i in range(random.randint(6, 10)):
        ts = random_timestamp(base, i)
        ip = random.choice(ips)
        logs.append(f"{ts} [ERROR] source=web_server - Connection flood detected from {ip} - 503 Service Unavailable")
    logs.append(f"{random_timestamp(base, 12)} [CRITICAL] source=load_balancer - Server pool exhausted, all backends unresponsive")
    return logs


# Map of available attack scenarios
ATTACK_SCENARIOS = {
    "Brute Force Attack": generate_brute_force,
    "Port Scanning": generate_port_scan,
    "Data Exfiltration": generate_data_exfiltration,
    "Privilege Escalation": generate_privilege_escalation,
    "DDoS Attack": generate_ddos,
}


def run_demo(scenario_name: str = None):
    """Run a single demo: generate logs, send to API, display results."""
    base_time = datetime.now().replace(microsecond=0)

    # Pick a random attack scenario, or use the one specified
    if scenario_name and scenario_name in ATTACK_SCENARIOS:
        chosen = scenario_name
    else:
        chosen = random.choice(list(ATTACK_SCENARIOS.keys()))

    print("=" * 70)
    print(f"  NETTRIAGE AI — LIVE DEMO")
    print(f"  Scenario: {chosen}")
    print("=" * 70)

    # Generate a mix of normal logs + attack logs
    normal_logs = generate_normal_logs(base_time - timedelta(minutes=5), count=random.randint(2, 4))
    attack_logs = ATTACK_SCENARIOS[chosen](base_time)

    # Combine and sort by timestamp for realism
    all_logs = normal_logs + attack_logs
    all_logs.sort()

    raw_log_text = "\n".join(all_logs)

    print("\n--- Raw Logs Being Sent ---")
    for log in all_logs:
        print(f"  {log}")

    print(f"\n--- Sending {len(all_logs)} log entries to NetTriage AI ---")
    print(f"  Endpoint: {API_URL}")
    print(f"  Waiting for response (may take 30-60s if service is cold)...\n")

    try:
        response = requests.post(
            API_URL,
            json={"logs": raw_log_text},
            timeout=120,
        )
        result = response.json()
    except requests.exceptions.Timeout:
        print("  ERROR: Request timed out. The service may be waking up from sleep.")
        print("  Try running the demo again in 60 seconds.")
        return
    except Exception as e:
        print(f"  ERROR: {e}")
        return

    # Display results
    print("=" * 70)
    print("  TRIAGE RESULTS")
    print("=" * 70)

    flagged = result.get("anomaly_flagged", False)
    score = result.get("anomaly_score", 0)

    print(f"\n  Anomaly Detected:  {'YES' if flagged else 'NO'}")
    print(f"  Anomaly Score:     {score}")
    print(f"  Summary:           {result.get('anomaly_summary', 'N/A')}")

    if flagged and result.get("report"):
        print(f"\n--- Incident Report ---")
        print(result["report"])

    if flagged and result.get("remediation"):
        print(f"\n--- Remediation Steps ---")
        print(result["remediation"])

    if result.get("errors"):
        print(f"\n--- Errors ---")
        for err in result["errors"]:
            print(f"  {err}")

    print("\n" + "=" * 70)
    print("  Demo complete.")
    print("=" * 70)


if __name__ == "__main__":
    scenario = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else None
    run_demo(scenario)