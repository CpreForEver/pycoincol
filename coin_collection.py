#!/usr/bin/env python3
import sqlite3
import os
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import requests
import logging

LOGGING = True
app = Flask(__name__)
app.secret_key = os.urandom(24)

# Database path relative to current directory
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "coins.db")


def load_api_token():
    """Load PCGS API token from file and set environment variable"""
    token_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "pcgs_token.token"
    )
    if os.path.exists(token_path):
        with open(token_path, "r") as f:
            content = f.read()
            token = content.splitlines()[0].strip() if content else ""
            if token:
                os.environ["PCGS_API_KEY"] = token
                return token
    return None


def get_db():
    """Get database connection"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialize database with tables"""
    conn = get_db()
    c = conn.cursor()

    # Create coins table
    c.execute("""
        CREATE TABLE IF NOT EXISTS coins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pcgs_no TEXT,
            cert_no TEXT,
            name TEXT NOT NULL,
            year INTEGER,
            denomination TEXT,
            mintage TEXT,
            mint_mark TEXT,
            mint_location TEXT,
            metal_content TEXT,
            diameter REAL,
            edge TEXT,
            weight REAL,
            country TEXT,
            grade TEXT,
            designation TEXT,
            price_guide_value REAL,
            population INTEGER,
            pop_higher INTEGER,
            coin_facts_link TEXT,
            designer TEXT,
            thumbnail_url TEXT,
            fullsize_url TEXT,
            description TEXT,
            mint TEXT,
            condition TEXT,
            price REAL,
            image_url TEXT,
            pcgs_number TEXT
        )
    """)

    # Create indexes for faster searching
    c.execute("CREATE INDEX IF NOT EXISTS idx_year ON coins(year)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_condition ON coins(condition)")

    conn.commit()
    conn.close()


@app.route("/")
def index():
    """Display all coins"""
    conn = get_db()
    coins = conn.execute("SELECT * FROM coins").fetchall()
    conn.close()
    return render_template("index.html", coins=coins)


@app.route("/add_coin", methods=["GET", "POST"])
def add_coin():
    """Add a new coin"""
    if request.method == "POST":
        name = request.form["name"]
        year = request.form["year"]
        mint = request.form["mint"]
        condition = request.form["condition"]
        grade = request.form["grade"]
        description = request.form["description"]
        price = float(request.form["price"])
        image_url = request.form["image_url"]
        pcgs_number = request.form.get("pcgs_number", "")

        conn = get_db()
        conn.execute(
            "INSERT INTO coins (name, year, mint, condition, grade, description, price, image_url, pcgs_number) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                name,
                int(year) if year else None,
                mint,
                condition,
                grade,
                description,
                price,
                image_url,
                pcgs_number,
            ),
        )
        conn.commit()
        conn.close()

        flash(f'Coin "{name}" added successfully!', "success")
        return redirect(url_for("index"))

    return render_template("add_coin.html")


@app.route("/search_pcgs_certno", methods=["GET", "POST"])
def search_pcgs_certno():
    """Search PCGS API by PCGS number"""
    # Get PCGS number from query params (GET) or form (POST)
    pcgs_no = request.args.get("pcgs_no", request.form.get("pcgs_no", "")).strip()

    if not pcgs_no:
        flash("Please enter a PCGS number to search", "warning")
        return redirect(url_for("add_coin"))

    try:

        # Load and verify token
        pcgs_api_key = os.environ.get("PCGS_API_KEY", "")
        if not pcgs_api_key:
            return jsonify(
                {
                    "error": "No PCGS API token found",
                    "success": False,
                    "details": "Please set PCGS_API_KEY environment variable or create pcgs_token.token file",
                }
            ), 401

        headers = {
            "authorization": f"bearer {pcgs_api_key}",
            "accept": "application/json",
        }

        # PCGS API endpoint for coin data using certno (PCGS number)
        url = f"https://api.pcgs.com/publicapi/coindetail/GetCoinFactsByGrade?PCGSNo={pcgs_no}&GradeNo=1&PlusGrade=false&api_key={pcgs_api_key}"
        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code == 200:
            coin_data = response.json()

            if coin_data:
                # Return JSON response for frontend to use (don't redirect)
                return coin_data, 200
            else:
                # PCGS API returned 404 - no coin found with this number
                return jsonify(
                    {
                        "error": f"No coin found for PCGS number: {pcgs_no}",
                        "success": False,
                    }
                ), 404

        else:
            # API returns 403 (no token), 429 (rate limit), or other errors
            return jsonify(
                {
                    "error": f"API error {response.status_code}",
                    "success": False,
                    "details": f"Could not retrieve PCGS data: {response.status_code}",
                }
            ), response.status_code

    except requests.exceptions.RequestException as e:
        return jsonify(
            {
                "error": "Network error",
                "success": False,
                "details": str(e),
            }
        ), 503
    except Exception as e:
        return jsonify(
            {
                "error": "Processing error",
                "success": False,
                "details": str(e),
            }
        ), 500
        flash(f"Error processing PCGS data: {str(e)}", "error")
        return redirect(url_for("add_coin"))


@app.route("/edit_coin/<int:id>", methods=["GET", "POST"])
def edit_coin(id):
    """Edit an existing coin"""
    conn = get_db()

    if request.method == "POST":
        id = request.form["id"]
        name = request.form["name"]
        year = request.form["year"]
        mint = request.form["mint"]
        condition = request.form["condition"]
        grade = request.form["grade"]
        description = request.form["description"]
        price = float(request.form["price"])
        image_url = request.form["image_url"]
        pcgs_number = request.form.get("pcgs_number", "")

        conn.execute(
            "UPDATE coins SET name=?, year=?, mint=?, condition=?, grade=?, description=?, price=?, image_url=?, pcgs_number=? WHERE id=?",
            (
                name,
                int(year) if year else None,
                mint,
                condition,
                grade,
                description,
                price,
                image_url,
                pcgs_number,
                int(id),
            ),
        )
        conn.commit()
        conn.close()

        flash(f'Coin "{name}" updated successfully!', "success")
        return redirect(url_for("index"))

    coin = conn.execute("SELECT * FROM coins WHERE id=?", (id,)).fetchone()
    conn.close()

    if not coin:
        flash("Coin not found!", "error")
        return redirect(url_for("index"))

    return render_template("edit_coin.html", coin=coin)


@app.route("/delete_coin/<int:id>", methods=["POST"])
def delete_coin(id):
    """Delete a coin"""
    conn = get_db()
    coin = conn.execute("SELECT name FROM coins WHERE id=?", (id,)).fetchone()
    conn.execute("DELETE FROM coins WHERE id=?", (id,))
    conn.commit()
    conn.close()

    if coin:
        flash(f'Coin "{coin["name"]}" deleted successfully!', "success")

    return redirect(url_for("index"))


if __name__ == "__main__":
    if LOGGING:
        logging.basicConfig(level=logging.DEBUG)
        logging.getLogger("urllib3").setLevel(logging.DEBUG)
    init_db()
    load_api_token()
    app.run(debug=True, host="0.0.0.0", port=5000)
