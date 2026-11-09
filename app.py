
from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import joblib

app = Flask(__name__)
CORS(app)

# Load the trained model
model = joblib.load("landguard_model.pkl")

FEATURES = [
    "land_area",
    "number_of_landowners",
    "pending_approvals",
    "legal_disputes",
    "compensation_percentage",
    "project_progress"
]

@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "LandGuard AI API is running!"})

@app.route("/predict-delay", methods=["POST"])
def predict_delay():
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "JSON input required"}), 400

        missing = [f for f in FEATURES if f not in data]
        if missing:
            return jsonify({"error": "Missing fields", "fields": missing}), 400

        values = {f: float(data[f]) for f in FEATURES}
        input_data = pd.DataFrame([values], columns=FEATURES)

        probability = model.predict_proba(input_data)[0][1]

        if probability >= 0.70:
            risk = "High"
        elif probability >= 0.40:
            risk = "Medium"
        else:
            risk = "Low"

        return jsonify({
            "delay_probability": round(float(probability), 4),
            "risk_level": risk,
            "prediction": "Delayed" if probability >= 0.5 else "Not Delayed",
            "model_version": "1.0"
        })

    except (ValueError, TypeError):
        return jsonify({"error": "All input values must be numeric"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5000)
