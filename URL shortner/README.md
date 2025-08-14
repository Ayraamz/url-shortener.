# PyShort — URL Shortener (Flask)

A clean, exam-ready URL shortener with a **web interface**.  
Built with **Python (Flask)**, SQLite (file db), and Bootstrap.

## Features
- Enter a long URL -> get a short link like `http://127.0.0.1:5000/abc123`
- Redirect from short link to original
- Store mappings in **SQLite** (persists on disk)
- Optional **custom short codes**
- **Click counter**
- Clean responsive UI
- **Dockerfile** for one-command start
- Deploy guide for **Render**

## Run Locally (fast)
```bash
pip install -r requirements.txt
python app.py
```
Open: http://127.0.0.1:5000

## Docker (one command)
```bash
docker build -t pyshort .
docker run -p 8000:8000 pyshort
```
Open: http://127.0.0.1:8000

## Deploy to Render (public URL)
1) Push this folder to a **public GitHub repo**.  
2) On render.com -> **New** -> **Web Service** -> Connect your repo.  
3) **Build Command:** `pip install -r requirements.txt`  
   **Start Command:** `gunicorn -b 0.0.0.0:8000 app:app`  
   **Runtime:** Python 3.11 (Auto)  
4) After deploy, you’ll get a live URL like `https://pyshort.onrender.com`.

## Screens to Show in Recording (1–2 minutes)
- Home page -> paste a long URL -> Shorten
- Copy the short link -> open in new tab (it redirects)
- Show that **click counter** increased
- Show **GitHub repo** and **Render URL**

## Notes
- DB file: `db.sqlite3` is created automatically on first run.
- You can control code length by env var `SHORT_CODE_LEN`.
- API list: `/api/list` returns recent links as JSON.

---
Generated: 2025-08-14T05:18:54.095251Z