import csv
import os
import random
import time

def simulate_attack():
    """
    Injects artificial anomalies into anomaly_results.csv
    so the dashboard graph changes in real time.
    """

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    results_file = os.path.join(BASE_DIR, "..", "results", "anomaly_results.csv")

    # If file does not exist, do nothing
    if not os.path.exists(results_file):
        print("❌ anomaly_results.csv not found")
        return

    print("🚨 Simulating endpoint attack...")

    new_rows = []

    # Create 50 attack samples
    for _ in range(50):
        error = random.uniform(0.02, 0.08)   # HIGH anomaly values
        new_rows.append({
            "reconstruction_error": error,
            "threshold": 0.003,
            "is_anomaly": 1
        })

    # Append to CSV
    with open(results_file, "a", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["reconstruction_error", "threshold", "is_anomaly"]
        )
        writer.writerows(new_rows)

    print("✅ Attack injected successfully")
