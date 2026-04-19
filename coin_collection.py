#!/usr/bin/env python3
import os
import io
import csv
from flask import (
    Blueprint,
    request,
    redirect,
    url_for,
    flash,
    jsonify,
    send_file,
    render_template,
)
import requests

from database import get_db, load_api_token

COINS_bp = Blueprint('coins_bp', __name__, template_folder='templates')


@COINS_bp.route("/coins")
def coins():
    """Display all coins"""
    conn = get_db()
    coins = conn.execute("SELECT * FROM coins ORDER BY price_guide_value DESC LIMIT 10").fetchall()
    conn.close()
    return render_template("coins.html", coins=coins)


@COINS_bp.route("/api/coins", methods=["GET"])
def api_coins():
    """API endpoint to get all coins or search results"""
    search_term = request.args.get("q", "").strip()
    conn = get_db()
    
    if search_term:
        coins = conn.execute(
            "SELECT * FROM coins WHERE name LIKE ? OR pcgs_no LIKE ? OR year LIKE ? ORDER BY price_guide_value DESC",
            (f"%{search_term}%", f"%{search_term}%", f"{search_term}")
        ).fetchall()
    else:
        coins = conn.execute("SELECT * FROM coins ORDER BY price_guide_value DESC").fetchmany(100)
    
    conn.close()
    return jsonify([dict(coin) for coin in coins])


@COINS_bp.route("/add_coin", methods=["GET", "POST"])
def add_coin():
    """Add a new coin"""
    if request.method == "POST":
        name = request.form["name"]
        year = request.form["year"]
        denomination = request.form["denomination"]
        mint = request.form["mint"]
        mint_mark = request.form["mint_mark"]
        mint_location = request.form["mint_location"]
        metal_content = request.form["metal_content"]
        diameter = request.form.get("diameter", "")
        edge = request.form["edge"]
        weight = request.form.get("weight", "")
        country = request.form["country"]
        grade = request.form["grade"]
        designation = request.form["designation"]
        price_guide_value = request.form.get("price_guide_value", "")
        population = request.form.get("population", "")
        pop_higher = request.form.get("pop_higher", "")
        coin_facts_link = request.form.get("coin_facts_link", "")
        designer = request.form["designer"]
        thumbnail_url = request.form.get("thumbnail_url", "")
        fullsize_url = request.form.get("fullsize_url", "")
        pcgs_no = request.form.get("pcgs_no", "")
        cert_no = request.form.get("cert_no", "")

        conn = get_db()
        conn.execute(
            "INSERT INTO coins (pcgs_no, cert_no, name, year, denomination, mint, mint_mark, mint_location, metal_content, diameter, edge, weight, country, grade, designation, price_guide_value, population, pop_higher, coin_facts_link, designer, thumbnail_url, fullsize_url) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                pcgs_no,
                cert_no,
                name,
                int(year) if year else None,
                denomination,
                mint,
                mint_mark,
                mint_location,
                metal_content,
                float(diameter) if diameter else None,
                edge,
                float(weight) if weight else None,
                country,
                grade,
                designation,
                float(price_guide_value) if price_guide_value else None,
                int(population) if population else None,
                int(pop_higher) if pop_higher else None,
                coin_facts_link,
                designer,
                thumbnail_url,
                fullsize_url,
            ),
        )
        conn.commit()
        conn.close()

        flash(f'Coin "{name}" added successfully!', "success")
        return redirect(url_for("coins_bp.coins"))

    return render_template("add_coin.html")


@COINS_bp.route("/search_pcgs_certno", methods=["GET", "POST"])
def search_pcgs_certno():
    """Search PCGS API by PCGS number"""
    pcgs_no = request.args.get("pcgs_no", request.form.get("pcgs_no", "")).strip()

    if not pcgs_no:
        flash("Please enter a PCGS number to search", "warning")
        return redirect(url_for("coins_bp.coins"))

    try:
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
            "accept": "COINS_bplication/json",
        }

        url = f"https://api.pcgs.com/publicapi/coindetail/GetCoinFactsByGrade?PCGSNo={pcgs_no}&GradeNo=1&PlusGrade=false&api_key={pcgs_api_key}"
        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code == 200:
            coin_data = response.json()

            if coin_data:
                return coin_data, 200
            else:
                return jsonify(
                    {
                        "error": f"No coin found for PCGS number: {pcgs_no}",
                        "success": False,
                    }
                ), 404

        else:
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

@COINS_bp.route("/export_csv", methods=["GET"])
def export_csv():
    """Export all coins to CSV"""
    conn = get_db()
    coins = conn.execute("SELECT * FROM coins ORDER BY price DESC").fetchall()
    conn.close()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(
        [
            "id",
            "pcgs_no",
            "cert_no",
            "name",
            "year",
            "denomination",
            "mint",
            "mint_mark",
            "mint_location",
            "metal_content",
            "diameter",
            "edge",
            "weight",
            "country",
            "grade",
            "designation",
            "price_guide_value",
            "population",
            "pop_higher",
            "coin_facts_link",
            "designer",
            "thumbnail_url",
            "fullsize_url",
            "description",
            "price",
            "image_url",
            "pcgs_number",
        ]
    )
    for coin in coins:
        writer.writerow(
            [
                coin["id"],
                coin["pcgs_no"],
                coin["cert_no"],
                coin["name"],
                coin["year"],
                coin["denomination"],
                coin["mint"],
                coin["mint_mark"],
                coin["mint_location"],
                coin["metal_content"],
                coin["diameter"],
                coin["edge"],
                coin["weight"],
                coin["country"],
                coin["grade"],
                coin["designation"],
                coin["price_guide_value"],
                coin["population"],
                coin["pop_higher"],
                coin["coin_facts_link"],
                coin["designer"],
                coin["thumbnail_url"],
                coin["fullsize_url"],
                coin["description"],
                coin["price"],
                coin["image_url"],
                coin["pcgs_number"],
            ]
        )

    output.seek(0)
    data = output.getvalue()
    output = io.BytesIO(data.encode("utf-8"))
    return send_file(
        output,
        mimetype="text/csv",
        as_attachment=True,
        download_name="pycoincol_collection.csv",
    )


@COINS_bp.route("/import_csv", methods=["POST"])
def import_csv():
    """Import coins from CSV file"""
    if "file" not in request.files:
        flash("No file part", "error")
        return redirect(url_for("coins_bp.coins"))

    file = request.files["file"]

    if file.filename == "":
        flash("No selected file", "error")
        return redirect(url_for("coins_bp.coins"))

    if file:

        file_content = file.stream.read().decode("utf-8")
        file_stream = io.StringIO(file_content)
        csv_file = csv.reader(file_stream)
        imported = 0
        errors = 0
        # skip first row
        next(csv_file)
        try:
            conn = get_db()
            for row in csv_file:

                if len(row) >= 22:  # Minimum required fields
                    pcgs_no = row[1] if len(row) > 1 else ""
                    cert_no = row[2] if len(row) > 2 else ""
                    name = row[3] if len(row) > 3 else ""
                    year = row[4] if len(row) > 4 and row[4] else None
                    denomination = row[5] if len(row) > 5 else ""
                    mint = row[6] if len(row) > 6 else ""
                    mint_mark = row[7] if len(row) > 7 else ""
                    mint_location = row[8] if len(row) > 8 else ""
                    metal_content = row[9] if len(row) > 9 else ""
                    diameter = row[10] if len(row) > 10 and row[10] else None
                    edge = row[11] if len(row) > 11 else ""
                    weight = row[12] if len(row) > 12 and row[12] else None
                    country = row[13] if len(row) > 13 else ""
                    grade = row[14] if len(row) > 14 else ""
                    designation = row[15] if len(row) > 15 else ""
                    price_guide_value = row[16] if len(row) > 16 and row[16] else None
                    population = row[17] if len(row) > 17 and row[17] else None
                    pop_higher = row[18] if len(row) > 18 and row[18] else None
                    coin_facts_link = row[19] if len(row) > 19 and row[19] else ""
                    designer = row[20] if len(row) > 20 else ""
                    thumbnail_url = row[21] if len(row) > 21 else None
                    fullsize_url = row[22] if len(row) > 22 else None

                    conn.execute(
                        "INSERT INTO coins (pcgs_no, cert_no, name, year, denomination, mint, mint_mark, mint_location, metal_content, diameter, edge, weight, country, grade, designation, price_guide_value, population, pop_higher, coin_facts_link, designer, thumbnail_url, fullsize_url) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                        (
                            pcgs_no,
                            cert_no,
                            name,
                            int(year) if year else None,
                            denomination,
                            mint,
                            mint_mark,
                            mint_location,
                            metal_content,
                            float(diameter) if diameter else None,
                            edge,
                            float(weight) if weight else None,
                            country,
                            grade,
                            designation,
                            float(price_guide_value) if price_guide_value else None,
                            int(population) if population else None,
                            int(pop_higher) if pop_higher else None,
                            coin_facts_link,
                            designer,
                            thumbnail_url,
                            fullsize_url,
                         ),
                    )
                    imported += 1

            conn.commit()
            conn.close()

        except Exception as e:
            flash(f"Error importing CSV: {str(e)}", "error")
            errors += 1

    if imported > 0:
        flash(f"Successfully imported {imported} coins!", "success")
    else:
        flash("No valid coins found in file or all coins already exist", "warning")

    return redirect(url_for("coins_bp.coins"))


@COINS_bp.route("/export_template_csv", methods=["GET"])
def export_template_csv():
    """Export CSV template for importing"""
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(
        [
            "id",
            "pcgs_no",
            "cert_no",
            "name",
            "year",
            "denomination",
            "mint",
            "mint_mark",
            "mint_location",
            "metal_content",
            "diameter",
            "edge",
            "weight",
            "country",
            "grade",
            "designation",
            "price_guide_value",
            "population",
            "pop_higher",
            "coin_facts_link",
            "designer",
            "thumbnail_url",
            "fullsize_url",
            "description",
            "price",
            "image_url",
            "pcgs_number",
        ]
    )

    output.seek(0)
    data = output.getvalue()
    output = io.BytesIO(data.encode("utf-8"))

    return send_file(
        output,
        mimetype="text/csv",
        as_attachment=True,
        download_name="pycoincol_template.csv",
    )


