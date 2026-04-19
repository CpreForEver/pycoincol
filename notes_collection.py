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

NOTES_bp = Blueprint('notes_bp', __name__, template_folder='templates')


@NOTES_bp.route("/notes")
def notes():
    """Display all bank notes"""
    conn = get_db()
    notes = conn.execute("SELECT * FROM notes ORDER BY price_value_guide DESC LIMIT 10").fetchall()
    conn.close()
    return render_template("notes.html", notes=notes)


@NOTES_bp.route("/api/notes", methods=["GET"])
def api_notes():
    """API endpoint to get all notes or search results"""
    search_term = request.args.get("q", "").strip()
    conn = get_db()

    if search_term:
        notes = conn.execute(
            "SELECT * FROM notes WHERE name LIKE ? OR pcgs_no LIKE ? OR year LIKE ? ORDER BY price_value_guide DESC",
            (f"%{search_term}%", f"%{search_term}%", f"{search_term}")
        ).fetchall()
    else:
        notes = conn.execute("SELECT * FROM notes ORDER BY price_value_guide DESC").fetchmany(100)

    conn.close()
    return jsonify([dict(note) for note in notes])


@NOTES_bp.route("/add_note", methods=["GET", "POST"])
def add_note():
    """Add a new bank note"""
    if request.method == "POST":
        pcgs_no = request.form.get("pcgs_no", "")
        cert_no = request.form.get("cert_no", "")
        serial_no = request.form.get("serial_no", "")
        name = request.form["name"]
        year = request.form["year"]
        denomination = request.form["denomination"]
        region = request.form["region"]
        grade = request.form["grade"]
        details = request.form.get("details", "")
        population = request.form.get("population", "")
        pop_higher = request.form.get("pop_higher", "")
        height = request.form.get("height", "")
        width = request.form.get("width", "")
        catalog_no1 = request.form.get("catalog_no1", "")
        catalog_no2 = request.form.get("catalog_no2", "")
        catalog1_long_desc = request.form.get("catalog1_long_desc", "")
        catalog2_long_desc = request.form.get("catalog2_long_desc", "")
        catalog1_short_desc = request.form.get("catalog1_short_desc", "")
        catalog2_short_desc = request.form.get("catalog2_short_desc", "")
        signers = request.form.get("signers", "")
        qualifiers = request.form.get("qualifiers", "")
        plate_no = request.form.get("plate_no", "")
        value_view_link = request.form.get("value_view_link", "")
        price_value_guide = request.form.get("price_value_guide", "")
        has_obverse_image = request.form.get("has_obverse_image", "")
        has_reverse_image = request.form.get("has_reverse_image", "")
        image_ready = request.form.get("image_ready", "")
        image_description = request.form.get("image_description", "")
        description = request.form.get("description", "")

        conn = get_db()
        conn.execute(
            "INSERT INTO notes (pcgs_no, cert_no, serial_no, name, year, denomination, region, grade, details, population, pop_higher, height, width, catalog_no1, catalog_no2, catalog1_long_desc, catalog2_long_desc, catalog1_short_desc, catalog2_short_desc, signers, qualifiers, plate_no, value_view_link, price_value_guide, has_obverse_image, has_reverse_image, image_ready, image_description, description, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                pcgs_no or None,
                cert_no or None,
                serial_no or None,
                name,
                int(year) if year else None,
                denomination,
                region,
                grade,
                details,
                int(population) if population else None,
                int(pop_higher) if pop_higher else None,
                height,
                width,
                catalog_no1 or None,
                catalog_no2 or None,
                catalog1_long_desc or None,
                catalog2_long_desc or None,
                catalog1_short_desc or None,
                catalog2_short_desc or None,
                signers or None,
                qualifiers or None,
                plate_no or None,
                value_view_link or None,
                float(price_value_guide) if price_value_guide else None,
                1 if has_obverse_image else None,
                1 if has_reverse_image else None,
                1 if image_ready else None,
                image_description or None,
                description or None,
                "2026-04-19T00:00:00",  # Placeholder timestamp
                "2026-04-19T00:00:00",  # Placeholder timestamp
            ),
        )
        conn.commit()
        conn.close()

        flash(f'Bank note "{name}" added successfully!', "success")
        return redirect(url_for("notes_bp.notes"))

    return render_template("add_note.html")


@NOTES_bp.route("/search_pcgs_notes", methods=["GET", "POST"])
def search_pcgs_notes():
    """Search PCGS API for bank notes"""
    pcgs_no = request.args.get("pcgs_no", request.form.get("pcgs_no", "")).strip()

    if not pcgs_no:
        flash("Please enter a PCGS number to search", "warning")
        return redirect(url_for("notes_bp.notes"))

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
            "accept": "application/json",
        }

        url = f"https://api.pcgs.com/publicapi/notedetail/GetCoinFactsByGrade?PCGSNo={pcgs_no}&GradeNo=1&PlusGrade=false&api_key={pcgs_api_key}"
        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code == 200:
            note_data = response.json()

            if note_data:
                return note_data, 200
            else:
                return jsonify(
                    {
                        "error": f"No bank note found for PCGS number: {pcgs_no}",
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


@NOTES_bp.route("/edit_note/<int:note_id>", methods=["GET", "POST"])
def edit_note(note_id):
    """Edit an existing bank note"""
    conn = get_db()
    conn.row_factory = sqlite3.Row
    note = conn.execute("SELECT * FROM notes WHERE id = ?", (note_id,)).fetchone()

    if not note:
        flash("Bank note not found", "error")
        return redirect(url_for("notes_bp.notes"))

    if request.method == "POST":
        pcgs_no = request.form.get("pcgs_no", "")
        cert_no = request.form.get("cert_no", "")
        serial_no = request.form.get("serial_no", "")
        name = request.form["name"]
        year = request.form["year"]
        denomination = request.form["denomination"]
        region = request.form["region"]
        grade = request.form["grade"]
        details = request.form.get("details", "")
        population = request.form.get("population", "")
        pop_higher = request.form.get("pop_higher", "")
        height = request.form.get("height", "")
        width = request.form.get("width", "")
        catalog_no1 = request.form.get("catalog_no1", "")
        catalog_no2 = request.form.get("catalog_no2", "")
        catalog1_long_desc = request.form.get("catalog1_long_desc", "")
        catalog2_long_desc = request.form.get("catalog2_long_desc", "")
        catalog1_short_desc = request.form.get("catalog1_short_desc", "")
        catalog2_short_desc = request.form.get("catalog2_short_desc", "")
        signers = request.form.get("signers", "")
        qualifiers = request.form.get("qualifiers", "")
        plate_no = request.form.get("plate_no", "")
        value_view_link = request.form.get("value_view_link", "")
        price_value_guide = request.form.get("price_value_guide", "")
        has_obverse_image = request.form.get("has_obverse_image", "")
        has_reverse_image = request.form.get("has_reverse_image", "")
        image_ready = request.form.get("image_ready", "")
        image_description = request.form.get("image_description", "")
        description = request.form.get("description", "")

        conn.execute(
            "UPDATE notes SET pcgs_no=?, cert_no=?, serial_no=?, name=?, year=?, denomination=?, region=?, grade=?, details=?, population=?, pop_higher=?, height=?, width=?, catalog_no1=?, catalog_no2=?, catalog1_long_desc=?, catalog2_long_desc=?, catalog1_short_desc=?, catalog2_short_desc=?, signers=?, qualifiers=?, plate_no=?, value_view_link=?, price_value_guide=?, has_obverse_image=?, has_reverse_image=?, image_ready=?, image_description=?, description=? WHERE id=?",
            (
                pcgs_no or None,
                cert_no or None,
                serial_no or None,
                name,
                int(year) if year else None,
                denomination,
                region,
                grade,
                details,
                int(population) if population else None,
                int(pop_higher) if pop_higher else None,
                height,
                width,
                catalog_no1 or None,
                catalog_no2 or None,
                catalog1_long_desc or None,
                catalog2_long_desc or None,
                catalog1_short_desc or None,
                catalog2_short_desc or None,
                signers or None,
                qualifiers or None,
                plate_no or None,
                value_view_link or None,
                float(price_value_guide) if price_value_guide else None,
                1 if has_obverse_image else None,
                1 if has_reverse_image else None,
                1 if image_ready else None,
                image_description or None,
                description or None,
                note_id,
            ),
        )
        conn.commit()
        conn.close()

        flash(f'Bank note "{name}" updated successfully!', "success")
        return redirect(url_for("notes_bp.notes"))

    return render_template("edit_note.html", note=note)


@NOTES_bp.route("/delete_note/<int:note_id>", methods=["GET"])
def delete_note(note_id):
    """Delete a bank note"""
    conn = get_db()
    note = conn.execute("SELECT name FROM notes WHERE id = ?", (note_id,)).fetchone()

    if note:
        conn.execute("DELETE FROM notes WHERE id = ?", (note_id,))
        conn.commit()
        flash(f'Bank note "{note["name"]}" deleted successfully!', "success")

    conn.close()
    return redirect(url_for("notes_bp.notes"))


@NOTES_bp.route("/export_note_csv", methods=["GET"])
def export_note_csv():
    """Export all notes to CSV"""
    conn = get_db()
    notes = conn.execute("SELECT * FROM notes ORDER BY price_value_guide DESC").fetchall()
    conn.close()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(
        [
            "id",
            "pcgs_no",
            "cert_no",
            "serial_no",
            "name",
            "year",
            "denomination",
            "region",
            "grade",
            "details",
            "population",
            "pop_higher",
            "height",
            "width",
            "catalog_no1",
            "catalog_no2",
            "catalog1_long_desc",
            "catalog2_long_desc",
            "catalog1_short_desc",
            "catalog2_short_desc",
            "signers",
            "qualifiers",
            "plate_no",
            "value_view_link",
            "price_value_guide",
            "has_obverse_image",
            "has_reverse_image",
            "image_ready",
            "image_description",
            "description",
            "created_at",
            "updated_at",
        ]
    )
    for note in notes:
        writer.writerow(
            [
                note["id"],
                note["pcgs_no"],
                note["cert_no"],
                note["serial_no"],
                note["name"],
                note["year"],
                note["denomination"],
                note["region"],
                note["grade"],
                note["details"],
                note["population"],
                note["pop_higher"],
                note["height"],
                note["width"],
                note["catalog_no1"],
                note["catalog_no2"],
                note["catalog1_long_desc"],
                note["catalog2_long_desc"],
                note["catalog1_short_desc"],
                note["catalog2_short_desc"],
                note["signers"],
                note["qualifiers"],
                note["plate_no"],
                note["value_view_link"],
                note["price_value_guide"],
                note["has_obverse_image"],
                note["has_reverse_image"],
                note["image_ready"],
                note["image_description"],
                note["description"],
                note["created_at"],
                note["updated_at"],
            ]
        )

    output.seek(0)
    data = output.getvalue()
    output = io.BytesIO(data.encode("utf-8"))
    return send_file(
        output,
        mimetype="text/csv",
        as_attachment=True,
        download_name="pycoincol_notes.csv",
    )


@NOTES_bp.route("/import_note_csv", methods=["POST"])
def import_note_csv():
    """Import notes from CSV file"""
    if "file" not in request.files:
        flash("No file part", "error")
        return redirect(url_for("notes_bp.notes"))

    file = request.files["file"]

    if file.filename == "":
        flash("No selected file", "error")
        return redirect(url_for("notes_bp.notes"))

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
                if len(row) >= 32:  # Minimum required fields
                    pcgs_no = row[1] if len(row) > 1 else ""
                    cert_no = row[2] if len(row) > 2 else ""
                    serial_no = row[3] if len(row) > 3 else ""
                    name = row[4] if len(row) > 4 else ""
                    year = row[5] if len(row) > 5 and row[5] else None
                    denomination = row[6] if len(row) > 6 else ""
                    region = row[7] if len(row) > 7 else ""
                    grade = row[8] if len(row) > 8 else ""
                    details = row[9] if len(row) > 9 else ""
                    population = row[10] if len(row) > 10 and row[10] else None
                    pop_higher = row[11] if len(row) > 11 and row[11] else None
                    height = row[12] if len(row) > 12 else ""
                    width = row[13] if len(row) > 13 else ""
                    catalog_no1 = row[14] if len(row) > 14 else ""
                    catalog_no2 = row[15] if len(row) > 15 else ""
                    catalog1_long_desc = row[16] if len(row) > 16 else ""
                    catalog2_long_desc = row[17] if len(row) > 17 else ""
                    catalog1_short_desc = row[18] if len(row) > 18 else ""
                    catalog2_short_desc = row[19] if len(row) > 19 else ""
                    signers = row[20] if len(row) > 20 else ""
                    qualifiers = row[21] if len(row) > 21 else ""
                    plate_no = row[22] if len(row) > 22 else ""
                    value_view_link = row[23] if len(row) > 23 else ""
                    price_value_guide = row[24] if len(row) > 24 and row[24] else None
                    has_obverse_image = row[25] if len(row) > 25 else ""
                    has_reverse_image = row[26] if len(row) > 26 else ""
                    image_ready = row[27] if len(row) > 27 else ""
                    image_description = row[28] if len(row) > 28 else ""
                    description = row[29] if len(row) > 29 else ""

                    conn.execute(
                        "INSERT INTO notes (pcgs_no, cert_no, serial_no, name, year, denomination, region, grade, details, population, pop_higher, height, width, catalog_no1, catalog_no2, catalog1_long_desc, catalog2_long_desc, catalog1_short_desc, catalog2_short_desc, signers, qualifiers, plate_no, value_view_link, price_value_guide, has_obverse_image, has_reverse_image, image_ready, image_description, description, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                        (
                            pcgs_no or None,
                            cert_no or None,
                            serial_no or None,
                            name,
                            int(year) if year else None,
                            denomination,
                            region,
                            grade,
                            details,
                            int(population) if population else None,
                            int(pop_higher) if pop_higher else None,
                            height,
                            width,
                            catalog_no1 or None,
                            catalog_no2 or None,
                            catalog1_long_desc or None,
                            catalog2_long_desc or None,
                            catalog1_short_desc or None,
                            catalog2_short_desc or None,
                            signers or None,
                            qualifiers or None,
                            plate_no or None,
                            value_view_link or None,
                            float(price_value_guide) if price_value_guide else None,
                            1 if has_obverse_image else None,
                            1 if has_reverse_image else None,
                            1 if image_ready else None,
                            image_description or None,
                            description or None,
                            "2026-04-19T00:00:00",
                            "2026-04-19T00:00:00",
                        ),
                    )
                    imported += 1

            conn.commit()
            conn.close()

        except Exception as e:
            flash(f"Error importing CSV: {str(e)}", "error")
            errors += 1

    if imported > 0:
        flash(f"Successfully imported {imported} bank notes!", "success")
    else:
        flash("No valid bank notes found in file or all bank notes already exist", "warning")

    return redirect(url_for("notes_bp.notes"))


@NOTES_bp.route("/api/export_template_csv", methods=["GET"])
def export_template_csv():
    """Export CSV template for importing notes"""
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(
        [
            "id",
            "pcgs_no",
            "cert_no",
            "serial_no",
            "name",
            "year",
            "denomination",
            "region",
            "grade",
            "details",
            "population",
            "pop_higher",
            "height",
            "width",
            "catalog_no1",
            "catalog_no2",
            "catalog1_long_desc",
            "catalog2_long_desc",
            "catalog1_short_desc",
            "catalog2_short_desc",
            "signers",
            "qualifiers",
            "plate_no",
            "value_view_link",
            "price_value_guide",
            "has_obverse_image",
            "has_reverse_image",
            "image_ready",
            "image_description",
            "description",
            "created_at",
            "updated_at",
        ]
    )

    output.seek(0)
    data = output.getvalue()
    output = io.BytesIO(data.encode("utf-8"))

    return send_file(
        output,
        mimetype="text/csv",
        as_attachment=True,
        download_name="pycoincol_notes_template.csv",
    )


