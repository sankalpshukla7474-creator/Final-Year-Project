import pandas as pd
import numpy as np
import os
import csv
from tensorflow.keras.models import load_model
from sklearn.preprocessing import MinMaxScaler

# ================= PATHS =================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_PATH = os.path.join(BASE_DIR, "..", "data", "processed", "processed_dataset.csv")
MODEL_PATH = os.path.join(BASE_DIR, "..", "models", "autoencoder_model.keras")
OUTPUT_PATH = os.path.join(BASE_DIR, "..", "results", "anomaly_results.csv")


# ================= RUN DETECTION =================
def run_detection():
    """Runs anomaly detection and saves CSV"""

    print("✅ Loading dataset...")
    df = pd.read_csv(DATA_PATH)

    X = df.select_dtypes(include=[np.number])

    scaler = MinMaxScaler()
    X_scaled = scaler.fit_transform(X)

    print("✅ Loading trained autoencoder...")
    model = load_model(MODEL_PATH)

    print("🔍 Running anomaly detection...")
    reconstructions = model.predict(X_scaled, verbose=0)

    reconstruction_error = np.mean(
        np.square(X_scaled - reconstructions), axis=1
    )

    threshold = np.percentile(reconstruction_error, 98)
    is_anomaly = (reconstruction_error > threshold).astype(int)

    results = pd.DataFrame({
        "reconstruction_error": reconstruction_error,
        "threshold": threshold,
        "is_anomaly": is_anomaly
    })

    results.to_csv(OUTPUT_PATH, index=False)

    print("🎉 Detection complete")
    print(f"📊 Total Samples: {len(results)}")
    print(f"🚨 Anomalies: {is_anomaly.sum()}")
    print(f"📈 Threshold: {threshold}")


# ================= LOAD RESULTS (FLASK API) =================
def load_results():
    """Used by Flask API"""

    results_file = OUTPUT_PATH

    errors = []
    anomaly_indices = []
    threshold = 0.0

    if not os.path.exists(results_file):
        return {
            "total_samples": 0,
            "anomalies": 0,
            "threshold": 0.0,
            "errors": [],
            "anomaly_indices": []
        }

    with open(results_file, "r") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            error = float(row["reconstruction_error"])
            errors.append(error)

            threshold = float(row["threshold"])  # same for all rows

            if row["is_anomaly"] == "1":
                anomaly_indices.append(i)

    return {
        "total_samples": len(errors),
        "anomalies": len(anomaly_indices),
        "threshold": threshold,
        "errors": errors,
        "anomaly_indices": anomaly_indices
    }


# ================= CLI RUN =================
if __name__ == "__main__":
    run_detection()
def endpoint_summary():
    """
    Groups anomalies into fake endpoints for dashboard display
    """

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    results_file = os.path.join(BASE_DIR, "..", "results", "anomaly_results.csv")

    endpoints = {}

    if not os.path.exists(results_file):
        return []

    with open(results_file, "r") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            endpoint = f"WS-ENDPOINT-{i % 10}"  # 10 endpoints
            is_anomaly = int(row["is_anomaly"])

            if endpoint not in endpoints:
                endpoints[endpoint] = {
                    "endpoint": endpoint,
                    "anomalies": 0
                }

            if is_anomaly:
                endpoints[endpoint]["anomalies"] += 1

    # severity mapping
    results = []
    for ep in endpoints.values():
        count = ep["anomalies"]

        if count >= 10:
            severity = "critical"
            status = "Compromised"
        elif count >= 5:
            severity = "high"
            status = "Investigating"
        elif count >= 1:
            severity = "medium"
            status = "Warning"
        else:
            severity = "low"
            status = "Healthy"

        ep["severity"] = severity
        ep["status"] = status
        results.append(ep)

    return results
