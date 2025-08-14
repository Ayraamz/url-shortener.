
import os
import re
import sqlite3
from datetime import datetime
from urllib.parse import urlparse

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, g

# Configuration
DATABASE = os.environ.get("DATABASE", "db.sqlite3")
SHORT_CODE_LEN = int(os.environ.get("SHORT_CODE_LEN", 6))

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key")

# ---------------------- DB Helpers ----------------------
def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE, detect_types=sqlite3.PARSE_DECLTYPES)
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(exc):
    db = g.pop("db", None)
    if db is not None:
        db.close()

def init_db():
    db = get_db()
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS urls (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            long_url TEXT NOT NULL,
            short_code TEXT NOT NULL UNIQUE,
            clicks INTEGER NOT NULL DEFAULT 0,
            created_at TIMESTAMP NOT NULL
        )
        """
    )
    db.commit()

# ---------------------- Utils ----------------------
def is_valid_url(u: str) -> bool:
    try:
        p = urlparse(u)
        return p.scheme in {"http", "https"} and bool(p.netloc)
    except Exception:
        return False

def generate_code(n=SHORT_CODE_LEN):
    alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    import random
    return ''.join(random.choices(alphabet, k=n))

def get_unique_code(db):
    while True:
        code = generate_code()
        row = db.execute("SELECT 1 FROM urls WHERE short_code = ?", (code,)).fetchone()
        if not row:
            return code

# ---------------------- Routes ----------------------
@app.route("/", methods=["GET"])
def index():
    init_db()
    db = get_db()
    recent = db.execute("SELECT long_url, short_code, clicks, created_at FROM urls ORDER BY id DESC LIMIT 20").fetchall()
    base = request.host_url  # e.g., http://127.0.0.1:5000/
    return render_template("index.html", recent=recent, base=base)

@app.route("/shorten", methods=["POST"])
def shorten():
    init_db()
    db = get_db()
    long_url = (request.form.get("long_url") or "").strip()
    custom_code = (request.form.get("custom_code") or "").strip()

    if not long_url:
        flash("Please enter a URL.", "danger")
        return redirect(url_for("index"))

    if not is_valid_url(long_url):
        flash("Invalid URL. Include http:// or https://", "danger")
        return redirect(url_for("index"))

    # If custom code provided, validate and ensure unique
    if custom_code:
        if not re.fullmatch(r"[A-Za-z0-9_-]{3,30}", custom_code):
            flash("Custom code must be 3–30 chars: letters, numbers, -, _", "danger")
            return redirect(url_for("index"))
        exists = db.execute("SELECT 1 FROM urls WHERE short_code = ?", (custom_code,)).fetchone()
        if exists:
            flash("That custom code is already taken. Try another.", "danger")
            return redirect(url_for("index"))
        code = custom_code
    else:
        code = get_unique_code(db)

    db.execute(
        "INSERT INTO urls (long_url, short_code, clicks, created_at) VALUES (?,?,0,?)",
        (long_url, code, datetime.utcnow()),
    )
    db.commit()
    flash("Short URL created successfully!", "success")
    return redirect(url_for("show", code=code))

@app.route("/u/<code>")
def show(code):
    # shows a page with the single short link details
    db = get_db()
    row = db.execute("SELECT long_url, short_code, clicks, created_at FROM urls WHERE short_code = ?", (code,)).fetchone()
    if not row:
        flash("Short code not found.", "warning")
        return redirect(url_for("index"))
    base = request.host_url
    return render_template("show.html", row=row, base=base)

@app.route("/<code>")
def go(code):
    db = get_db()
    row = db.execute("SELECT id, long_url, clicks FROM urls WHERE short_code = ?", (code,)).fetchone()
    if row:
        db.execute("UPDATE urls SET clicks = clicks + 1 WHERE id = ?", (row["id"],))
        db.commit()
        return redirect(row["long_url"], code=302)
    flash("Short code not found.", "warning")
    return redirect(url_for("index"))

# ------------- Small JSON API (optional) -------------
@app.route("/api/list")
def api_list():
    db = get_db()
    rows = db.execute("SELECT long_url, short_code, clicks, created_at FROM urls ORDER BY id DESC LIMIT 100").fetchall()
    base = request.host_url
    data = [
        {
            "long_url": r["long_url"],
            "short_url": base + r["short_code"],
            "clicks": r["clicks"],
            "created_at": r["created_at"].isoformat() if hasattr(r["created_at"], "isoformat") else str(r["created_at"]),
        }
        for r in rows
    ]
    return jsonify(data)

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)
