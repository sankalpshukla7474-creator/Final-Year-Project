from flask import Flask, render_template, jsonify
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "templates"),
    static_folder=os.path.join(BASE_DIR, "static")
)

# ================= HOME =================
@app.route("/")
def index():
    return render_template("index.html")

# ================= API =================
@app.route("/api/data")
def get_data():
    from detect_anomaly import load_results
    return jsonify(load_results())
@app.route("/api/endpoints")
def get_endpoints():
    from detect_anomaly import endpoint_summary
    return jsonify(endpoint_summary())

@app.route("/api/simulate_attack", methods=["POST"])
def simulate_attack():
    from attack_simulator import simulate_attack
    simulate_attack()
    return jsonify({"status": "attack simulated"})

if __name__ == "__main__":
    app.run(debug=True)
