# Flask backend for the SuperKart sales forecasting model
import os
import joblib
import numpy as np
import pandas as pd
from flask import Flask, request, jsonify

# Initialise the Flask application
superkart_api = Flask("SuperKart Sales Predictor")

# Load the serialized pipeline (preprocessing + model)
MODEL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "superkart_model.joblib")
model = joblib.load(MODEL_PATH)

# Columns the model was trained on (order does not matter, names do)
FEATURES = [
    "Product_Weight", "Product_Sugar_Content", "Product_Allocated_Area", "Product_MRP",
    "Store_Size", "Store_Location_City_Type", "Store_Type",
    "Product_Id_char", "Store_Age_Years", "Product_Type_Category",
]


@superkart_api.get("/")
def home():
    """Health check."""
    return "Welcome to the SuperKart Sales Prediction API!"


@superkart_api.post("/v1/predict")
def predict_sales():
    """Online inference: one JSON record in, one prediction out."""
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Request body must be a JSON object"}), 400

    missing = [c for c in FEATURES if c not in data]
    if missing:
        return jsonify({"error": f"Missing fields: {missing}"}), 400

    input_df = pd.DataFrame([{c: data[c] for c in FEATURES}])
    prediction = float(model.predict(input_df)[0])
    return jsonify({"Predicted_Product_Store_Sales_Total": round(prediction, 2)})


@superkart_api.post("/v1/predictbatch")
def predict_sales_batch():
    """Batch inference: a CSV file (form field 'file') in, one prediction per row out."""
    if "file" not in request.files:
        return jsonify({"error": "Upload a CSV file using the form field 'file'"}), 400

    input_df = pd.read_csv(request.files["file"])
    missing = [c for c in FEATURES if c not in input_df.columns]
    if missing:
        return jsonify({"error": f"Missing columns: {missing}"}), 400

    predictions = model.predict(input_df[FEATURES]).round(2)
    # {row_index: predicted_sales}
    return jsonify({str(i): float(p) for i, p in zip(input_df.index, predictions)})


if __name__ == "__main__":
    superkart_api.run(host="0.0.0.0", port=7860, debug=False)
