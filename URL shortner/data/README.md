# IOSS Data Science API (Flask)

**Purpose**: A ready-to-use Python/Flask backend that showcases Data Science skills (Pandas, Scikit‑learn, Matplotlib).
Use it as a starting point for the IOSS assessment. Adjust endpoints/logic to match the question you receive.

## Endpoints
- `GET /` – API info
- `GET /summary` – numeric describe + top cities counts
- `GET /search?min_price=&max_price=&bedrooms=&city=` – quick filters
- `POST /predict` – JSON -> `{"size_sqft":1200,"bedrooms":3,"age_years":5,"city":"Kochi"}`
- `GET /chart?col=price_inr|size_sqft|age_years|bedrooms` – returns a PNG

## Run Locally (fastest)
1. Create venv (optional but recommended):
   ```bash
   python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
   ```
2. Install deps:
   ```bash
   pip install -r requirements.txt
   ```
3. Start:
   ```bash
   python app.py
   ```
   App runs at http://127.0.0.1:5000

## Docker (one command)
```bash
docker build -t ioss-ds-api .
docker run -p 8000:8000 ioss-ds-api
```
App runs at http://127.0.0.1:8000

## Deploy to Render (free)
1. Push this project to a **public GitHub repo**.
2. In Render, create **New + Web Service** -> Connect repo.
3. **Environment**: `Python 3.11` (Auto-detected), Start command: `gunicorn -b 0.0.0.0:8000 app:app`
4. **Build Command**: `pip install -r requirements.txt`
5. After deploy, you’ll get a public URL like `https://yourapp.onrender.com`.

## Quick Demo Steps for Screen Recording (1–3 min)
- Open `/` to show endpoints.
- Hit `/summary` to show stats.
- Hit `/search?city=Kochi&bedrooms=3` to show filtered rows.
- POST `/predict` with one JSON example.
- Open `/chart?col=price_inr` to show the PNG chart.
- Show the **GitHub repo** and **Render URL**.

## Adapting to Tomorrow's Question
- Replace `data/house_prices.csv` with the dataset they give (if any).
- Update feature engineering / model in `app.py` if needed.
- You can add more endpoints, e.g., `/forecast`, `/classify`, etc.
- Commit and push to GitHub, then re-deploy on Render.

---
*Generated on: 2025-08-14T05:01:54.419779Z*