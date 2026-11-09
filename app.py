import os
import joblib
import pandas as pd
import requests
import math

from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from functools import wraps

load_dotenv()

app = Flask(__name__)

SUPABASE_URL = os.getenv("SUPABASE_URL", "").rstrip("/")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY", "")

if not SUPABASE_URL or not SUPABASE_ANON_KEY:
    raise RuntimeError("Supabase environment variables are missing.")

CORS(
    app,
    resources={
        r"/predict-delay": {
            "origins": [
    "https://review-document-landguard-ai.v0.build",
    "https://review-document-azgdcxc0w-mr-devil2.vercel.app"
]
        }
    },
    methods=["POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"]
)

model = joblib.load("landguard_model.pkl")

FEATURES = [
    "land_area",
    "number_of_landowners",
    "pending_approvals",
    "legal_disputes",
    "compensation_percentage",
    "project_progress"
]


def require_supabase_login(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")

        if not auth_header.startswith("Bearer "):
            return jsonify({"error": "Authentication required"}), 401

        token = auth_header.split(" ", 1)[1].strip()

        if not token:
            return jsonify({"error": "Invalid token"}), 401

        try:
            response = requests.get(
                f"{SUPABASE_URL}/auth/v1/user",
                headers={
                    "apikey": SUPABASE_ANON_KEY,
                    "Authorization": f"Bearer {token}"
                },
                timeout=10
            )

            if response.status_code != 200:
                return jsonify({"error": "Invalid or expired session"}), 401

        except requests.RequestException:
            return jsonify({"error": "Authentication service unavailable"}), 503

        return func(*args, **kwargs)

    return wrapper


@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "LandGuard AI API is running!"})



@app.route("/predict-delay", methods=["POST"])
@require_supabase_login
def predict_delay():
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "JSON input required"}), 400

        missing = [f for f in FEATURES if f not in data]

        if missing:
            return jsonify({"error": "Missing fields", "fields": missing}), 400

        values = {}

        for field in FEATURES:
            if isinstance(data[field], bool):
                return jsonify({"error": f"{field} must be numeric"}), 400

            try:
                value = float(data[field])
            except (ValueError, TypeError):
                return jsonify({"error": f"{field} must be numeric"}), 400

            if not math.isfinite(value):
                return jsonify({"error": f"{field} must be a finite number"}), 400

            values[field] = value

        if values["land_area"] <= 0:
            return jsonify({"error": "Land area must be greater than zero"}), 400

        for field in ["number_of_landowners", "pending_approvals", "legal_disputes"]:
            if values[field] < 0 or not values[field].is_integer():
                return jsonify({"error": f"{field} must be a non-negative whole number"}), 400

        for field in ["compensation_percentage", "project_progress"]:
            if not 0 <= values[field] <= 100:
                return jsonify({"error": f"{field} must be between 0 and 100"}), 400

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

    except Exception:
        return jsonify({"error": "Prediction failed"}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5000)