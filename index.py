from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)

from database import get_db, get_total_value

index_bp = Blueprint('index_bp', __name__, template_folder='templates')


@index_bp.route("/delete_coin/<int:id>", methods=["POST"])
def delete_coin(id):
    """Delete a coin"""
    conn = get_db()
    coin = conn.execute("SELECT name FROM coins WHERE id=?", (id,)).fetchone()
    conn.execute("DELETE FROM coins WHERE id=?", (id,))
    conn.commit()
    conn.close()

    if coin:
        flash(f'Coin "{coin["name"]}" deleted successfully!', "success")

    return redirect(url_for("index_bp.index"))


@index_bp.route("/edit_coin/<int:id>", methods=["GET", "POST"])
def edit_coin(id):
    """Edit an existing coin"""
    conn = get_db()

    if request.method == "POST":
        id = request.form["id"]
        name = request.form["name"]
        year = request.form.get("year", "")
        denomination = request.form.get("denomination", "")
        mint = request.form.get("mint", "")
        mint_mark = request.form.get("mint_mark", "")
        mint_location = request.form.get("mint_location", "")
        metal_content = request.form.get("metal_content", "")
        diameter = request.form.get("diameter", "")
        edge = request.form.get("edge", "")
        weight = request.form.get("weight", "")
        country = request.form.get("country", "")
        grade = request.form["grade"]
        designation = request.form.get("designation", "")
        price_guide_value = request.form.get("price_guide_value", "")
        population = request.form.get("population", "")
        pop_higher = request.form.get("pop_higher", "")
        coin_facts_link = request.form.get("coin_facts_link", "")
        designer = request.form.get("designer", "")
        thumbnail_url = request.form.get("thumbnail_url", "")
        fullsize_url = request.form.get("fullsize_url", "")
        pcgs_no = request.form.get("pcgs_no", "")
        cert_no = request.form.get("cert_no", "")

        conn.execute(
            "UPDATE coins SET name=?, year=?, denomination=?, mint=?, mint_mark=?, mint_location=?, metal_content=?, diameter=?, edge=?, weight=?, country=?, grade=?, designation=?, price_guide_value=?, population=?, pop_higher=?, coin_facts_link=?, designer=?, thumbnail_url=?, fullsize_url=?, pcgs_no=?, cert_no=? WHERE id=?",
            (
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
                pcgs_no,
                cert_no,
                int(id),
            ),
        )
        conn.commit()
        conn.close()

        flash(f'Coin "{name}" updated successfully!', "success")
        return redirect(url_for("index_bp.index"))

    coin = conn.execute("SELECT * FROM coins WHERE id=?", (id,)).fetchone()
    conn.close()

    if not coin:
        flash("Coin not found!", "error")
        return redirect(url_for("index_bp.index"))

    return render_template("edit_coin.html", coin=coin)


@index_bp.route("/search_all")
def search_all():
    """Unified search across coins, notes, and coin sets"""
    search_term = request.args.get("q", "").strip()

    conn = get_db()
    results = []
    total_value = 0

    if search_term:
        # Search coins
        coin_results = conn.execute(
            "SELECT 'coin' as type, id, pcgs_no, year, name, grade, price_guide_value as value FROM coins WHERE name LIKE ? OR pcgs_no LIKE ? OR year LIKE ?",
            (f"%{search_term}%", f"%{search_term}%", f"{search_term}")
        ).fetchall()
        results.extend([dict(r) for r in coin_results])
        total_value += sum(c.get("value", 0) or 0 for c in coin_results)

        # Search notes
        note_results = conn.execute(
            "SELECT 'note' as type, id, pcgs_no, year, name, grade, price_value_guide as value FROM notes WHERE name LIKE ? OR pcgs_no LIKE ? OR year LIKE ?",
            (f"%{search_term}%", f"%{search_term}%", f"{search_term}")
        ).fetchall()
        results.extend([dict(r) for r in note_results])
        total_value += sum(n.get("value", 0) or 0 for n in note_results)

        # Search coin sets
        set_results = conn.execute(
            "SELECT 'coin_set' as type, id, NULL as pcgs_no, year, '' as name, grade, price_value_guide as value FROM coin_sets WHERE year LIKE ? OR region LIKE ? OR grade LIKE ?",
            (f"{search_term}", f"%{search_term}%", f"{search_term}")
        ).fetchall()
        results.extend([dict(r) for r in set_results])
        total_value += sum(s.get("value", 0) or 0 for s in set_results)

    return jsonify({
        "results": results,
        "total_value": total_value,
        "count": len(results)
    })


@index_bp.route("/")
def index():
    """Home page"""
    total_value = get_total_value()
    return render_template("index.html", total_value=total_value)
