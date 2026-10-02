# Streamlit frontend for the SuperKart sales forecasting model
import os
import requests
import pandas as pd
import streamlit as st

# URL of the Flask backend. Inside the Docker network the backend is reachable by its container name.
BACKEND_URL = os.getenv("BACKEND_URL", "http://backend:7860")

st.set_page_config(page_title="SuperKart Sales Forecast", page_icon="🛒", layout="wide")
st.title("🛒 SuperKart Sales Forecast")
st.write("Predict the total revenue a product will generate in a given store.")

tab_single, tab_batch = st.tabs(["Single prediction", "Batch prediction (CSV)"])

# ------------------------- Single prediction -------------------------
with tab_single:
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Product")
        product_weight = st.number_input("Product weight", min_value=1.0, max_value=30.0, value=12.66, step=0.01)
        sugar = st.selectbox("Sugar content", ["Low Sugar", "Regular", "No Sugar"])
        allocated_area = st.number_input("Allocated display area (ratio)", min_value=0.001, max_value=0.5, value=0.027, step=0.001, format="%.3f")
        mrp = st.number_input("Product MRP", min_value=10.0, max_value=400.0, value=117.08, step=0.01)
        id_char = st.selectbox("Product ID prefix", ["FD", "DR", "NC"], help="FD = Food, DR = Drinks, NC = Non-Consumable")
        type_cat = st.selectbox("Product type category", ["Perishables", "Non Perishables"], index=1)
    with col2:
        st.subheader("Store")
        store_size = st.selectbox("Store size", ["High", "Medium", "Small"], index=1)
        city = st.selectbox("City tier", ["Tier 1", "Tier 2", "Tier 3"], index=1)
        store_type = st.selectbox("Store type", ["Supermarket Type1", "Supermarket Type2", "Departmental Store", "Food Mart"], index=1)
        store_age = st.number_input("Store age (years)", min_value=0, max_value=60, value=16, step=1)

    payload = {
        "Product_Weight": product_weight,
        "Product_Sugar_Content": sugar,
        "Product_Allocated_Area": allocated_area,
        "Product_MRP": mrp,
        "Store_Size": store_size,
        "Store_Location_City_Type": city,
        "Store_Type": store_type,
        "Product_Id_char": id_char,
        "Store_Age_Years": int(store_age),
        "Product_Type_Category": type_cat,
    }

    if st.button("Predict sales", type="primary"):
        try:
            resp = requests.post(f"{BACKEND_URL}/v1/predict", json=payload, timeout=30)
            if resp.status_code == 200:
                value = resp.json()["Predicted_Product_Store_Sales_Total"]
                st.success(f"Predicted sales: **{value:,.2f}**")
            else:
                st.error(f"API error {resp.status_code}: {resp.text}")
        except requests.exceptions.RequestException as e:
            st.error(f"Could not reach the backend at {BACKEND_URL}: {e}")

# ------------------------- Batch prediction -------------------------
with tab_batch:
    st.write("Upload a CSV with the columns: " + ", ".join(payload.keys()))
    uploaded = st.file_uploader("Choose a CSV file", type="csv")
    if uploaded is not None:
        batch_df = pd.read_csv(uploaded)
        st.dataframe(batch_df.head())
        if st.button("Predict for all rows"):
            try:
                resp = requests.post(
                    f"{BACKEND_URL}/v1/predictbatch",
                    files={"file": ("batch.csv", batch_df.to_csv(index=False).encode("utf-8"))},
                    timeout=120,
                )
                if resp.status_code == 200:
                    preds = resp.json()
                    batch_df["Predicted_Sales"] = [preds[str(i)] for i in batch_df.index]
                    st.dataframe(batch_df)
                    st.download_button("Download predictions", batch_df.to_csv(index=False), "predictions.csv", "text/csv")
                else:
                    st.error(f"API error {resp.status_code}: {resp.text}")
            except requests.exceptions.RequestException as e:
                st.error(f"Could not reach the backend at {BACKEND_URL}: {e}")
