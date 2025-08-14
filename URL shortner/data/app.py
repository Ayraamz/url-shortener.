
import io
import os
from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline

DATA_PATH = os.environ.get("DATA_PATH", "data/house_prices.csv")

app = Flask(__name__)
CORS(app)

# Load data and build a simple model at startup
df = pd.read_csv(DATA_PATH)
feature_cols = ["size_sqft", "bedrooms", "age_years", "city"]
target_col = "price_inr"

numeric_features = ["size_sqft", "bedrooms", "age_years"]
categorical_features = ["city"]

preprocessor = ColumnTransformer(
    transformers=[
        ("num", "passthrough", numeric_features),
        ("cat", OneHotEncoder(handle_unknown="ignore"), categorical_features),
    ]
)

model = Pipeline(steps=[("prep", preprocessor), ("reg", LinearRegression())])
model.fit(df[feature_cols], df[target_col])

@app.get("/")
def home():
    return jsonify({
        "message": "IOSS DS API up",
        "endpoints": {
            "/summary": "Dataset summary stats",
            "/search": "Filter data: params -> min_price, max_price, bedrooms, city",
            "/predict": "POST JSON -> {size_sqft, bedrooms, age_years, city}",
            "/chart": "Histogram chart of target or feature -> param: col (price_inr/size_sqft/age_years/bedrooms)",
        },
        "dataset_rows": len(df)
    })

@app.get("/summary")
def summary():
    # Basic numeric describe plus top cities
    numeric = df.select_dtypes(include="number").describe().to_dict()
    top_cities = df["city"].value_counts().to_dict()
    return jsonify({"describe": numeric, "top_cities": top_cities})

@app.get("/search")
def search():
    q = df.copy()
    min_price = request.args.get("min_price", type=float)
    max_price = request.args.get("max_price", type=float)
    bedrooms = request.args.get("bedrooms", type=int)
    city = request.args.get("city", type=str)

    if min_price is not None:
        q = q[q["price_inr"] >= min_price]
    if max_price is not None:
        q = q[q["price_inr"] <= max_price]
    if bedrooms is not None:
        q = q[q["bedrooms"] == bedrooms]
    if city:
        q = q[q["city"].str.lower() == city.lower()]

    # Limit to 100 rows to keep response light
    return jsonify({"count": len(q), "rows": q.head(100).to_dict(orient="records")})

@app.post("/predict")
def predict():
    payload = request.get_json(silent=True) or {}
    # Allow single record or list of records
    if isinstance(payload, dict) and "size_sqft" in payload:
        data = [payload]
    elif isinstance(payload, list):
        data = payload
    else:
        return jsonify({"error": "Send JSON with fields: size_sqft, bedrooms, age_years, city"}), 400

    X = pd.DataFrame(data)[["size_sqft", "bedrooms", "age_years", "city"]]
    y_pred = model.predict(X)
    return jsonify({"predictions": [float(v) for v in y_pred]})

@app.get("/chart")
def chart():
    col = request.args.get("col", "price_inr")
    if col not in ["price_inr", "size_sqft", "age_years", "bedrooms"]:
        return jsonify({"error": "col must be one of price_inr, size_sqft, age_years, bedrooms"}), 400

    fig, ax = plt.subplots(figsize=(6,4))
    ax.hist(df[col].dropna(), bins=20)
    ax.set_title(f"Histogram of {col}")
    ax.set_xlabel(col)
    ax.set_ylabel("Count")

    buf = io.BytesIO()
    fig.tight_layout()
    fig.savefig(buf, format="png")
    plt.close(fig)
    buf.seek(0)
    return send_file(buf, mimetype="image/png")

if __name__ == "__main__":
    # For local dev
    app.run(host="0.0.0.0", port=5000, debug=True)
