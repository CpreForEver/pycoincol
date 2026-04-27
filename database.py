import os
import sqlite3

LOGGING = True

# Database path relative to current directory
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "coins.db")


def load_api_token():
    """Load PCGS API token from file and set environment variable"""
    token_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pcgs_token.token")
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

    # Create notes table for bank notes
    c.execute("""
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pcgs_no TEXT,
            cert_no TEXT,
            name TEXT NOT NULL,
            year INTEGER,
            denomination TEXT,
            region TEXT,
            grade TEXT,
            details TEXT,
            population INTEGER,
            pop_higher INTEGER,
            serial_no TEXT,
            height TEXT,
            width TEXT,
            catalog_no1 TEXT,
            catalog_no2 TEXT,
            catalog1_long_desc TEXT,
            catalog2_long_desc TEXT,
            catalog1_short_desc TEXT,
            catalog2_short_desc TEXT,
            signers TEXT,
            qualifiers TEXT,
            plate_no TEXT,
            value_view_link TEXT,
            price_value_guide REAL,
            has_obverse_image INTEGER,
            has_reverse_image INTEGER,
            image_ready INTEGER,
            image_description TEXT,
            description TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Create indexes for notes table
    c.execute("CREATE INDEX IF NOT EXISTS idx_notes_year ON notes(year)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_notes_denomination ON notes(denomination)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_notes_grade ON notes(grade)")

    # Create coin_sets table for coin sets
    c.execute("""
        CREATE TABLE IF NOT EXISTS coin_sets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            year INTEGER,
            region TEXT,
            grade TEXT,
            details TEXT,
            population INTEGER,
            pop_higher INTEGER,
            serial_no TEXT,
            thumbnail_url TEXT,
            popup_url TEXT,
            image_description TEXT,
            width INTEGER,
            height INTEGER,
            has_obverse_image INTEGER,
            has_reverse_image INTEGER,
            image_ready INTEGER,
            price_value_guide REAL
        )
    """)

    # Create indexes for coin_sets table
    c.execute("CREATE INDEX IF NOT EXISTS idx_sets_year ON coin_sets(year)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_sets_region ON coin_sets(region)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_sets_grade ON coin_sets(grade)")

    conn.commit()
    conn.close()


def get_total_value():
    """Calculate total value of all coins, notes, and sets by summing price_value_guide fields"""
    conn = get_db()
    c = conn.cursor()

    # Sum price_guide_value from coins
    coin_total = c.execute("SELECT SUM(price_guide_value) FROM coins").fetchone()[0]

    # Sum price_value_guide from notes
    note_total = c.execute("SELECT SUM(price_value_guide) FROM notes").fetchone()[0]

    # Sum price_value_guide from coin_sets
    set_total = c.execute("SELECT SUM(price_value_guide) FROM coin_sets").fetchone()[0]

    conn.close()

    total = (coin_total or 0) + (note_total or 0) + (set_total or 0)
    return round(total, 2)


def add_note(data):
    """Add a new bank note to the database"""
    conn = get_db()
    c = conn.cursor()

    try:
        c.execute("""
            INSERT INTO notes (
                pcgs_no, cert_no, name, year, denomination, region, grade, details,
                population, pop_higher, serial_no, height, width, catalog_no1,
                catalog_no2, catalog1_long_desc, catalog2_long_desc,
                catalog1_short_desc, catalog2_short_desc, signers, qualifiers,
                plate_no, value_view_link, price_value_guide, has_obverse_image,
                has_reverse_image, image_ready, image_description, description
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data.get("pcgs_no"), data.get("cert_no"), data.get("name"),
            data.get("year"), data.get("denomination"), data.get("region"),
            data.get("grade"), data.get("details"), data.get("population"),
            data.get("pop_higher"), data.get("serial_no"), data.get("height"),
            data.get("width"), data.get("catalog_no1"), data.get("catalog_no2"),
            data.get("catalog1_long_desc"), data.get("catalog2_long_desc"),
            data.get("catalog1_short_desc"), data.get("catalog2_short_desc"),
            data.get("signers"), data.get("qualifiers"), data.get("plate_no"),
            data.get("value_view_link"), data.get("price_value_guide"),
            data.get("has_obverse_image"), data.get("has_reverse_image"),
            data.get("image_ready"), data.get("image_description"),
            data.get("description")
        ))
        conn.commit()
        return c.lastrowid
    except Exception as e:
        conn.rollback()
        conn.close()
        raise e
    finally:
        conn.close()


def get_note(id):
    """Get a bank note by ID"""
    conn = get_db()
    note = conn.execute("SELECT * FROM notes WHERE id = ?", (id,)).fetchone()
    conn.close()
    return note


def get_note_by_pcgs_no(pcgs_no):
    """Get a bank note by PCGS number"""
    conn = get_db()
    note = conn.execute("SELECT * FROM notes WHERE pcgs_no = ?", (pcgs_no,)).fetchone()
    conn.close()
    return note


def update_note(id, data):
    """Update an existing bank note"""
    conn = get_db()
    c = conn.cursor()

    try:
        # Update only provided fields
        fields = []
        values = []

        if "name" in data:
            fields.append("name = ?")
            values.append(data["name"])
        if "year" in data:
            fields.append("year = ?")
            values.append(data["year"])
        if "denomination" in data:
            fields.append("denomination = ?")
            values.append(data["denomination"])
        if "region" in data:
            fields.append("region = ?")
            values.append(data["region"])
        if "grade" in data:
            fields.append("grade = ?")
            values.append(data["grade"])
        if "details" in data:
            fields.append("details = ?")
            values.append(data["details"])
        if "population" in data:
            fields.append("population = ?")
            values.append(data["population"])
        if "pop_higher" in data:
            fields.append("pop_higher = ?")
            values.append(data["pop_higher"])
        if "serial_no" in data:
            fields.append("serial_no = ?")
            values.append(data["serial_no"])
        if "height" in data:
            fields.append("height = ?")
            values.append(data["height"])
        if "width" in data:
            fields.append("width = ?")
            values.append(data["width"])
        if "catalog_no1" in data:
            fields.append("catalog_no1 = ?")
            values.append(data["catalog_no1"])
        if "catalog_no2" in data:
            fields.append("catalog_no2 = ?")
            values.append(data["catalog_no2"])
        if "catalog1_long_desc" in data:
            fields.append("catalog1_long_desc = ?")
            values.append(data["catalog1_long_desc"])
        if "catalog2_long_desc" in data:
            fields.append("catalog2_long_desc = ?")
            values.append(data["catalog2_long_desc"])
        if "catalog1_short_desc" in data:
            fields.append("catalog1_short_desc = ?")
            values.append(data["catalog1_short_desc"])
        if "catalog2_short_desc" in data:
            fields.append("catalog2_short_desc = ?")
            values.append(data["catalog2_short_desc"])
        if "signers" in data:
            fields.append("signers = ?")
            values.append(data["signers"])
        if "qualifiers" in data:
            fields.append("qualifiers = ?")
            values.append(data["qualifiers"])
        if "plate_no" in data:
            fields.append("plate_no = ?")
            values.append(data["plate_no"])
        if "value_view_link" in data:
            fields.append("value_view_link = ?")
            values.append(data["value_view_link"])
        if "has_obverse_image" in data:
            fields.append("has_obverse_image = ?")
            values.append(data["has_obverse_image"])
        if "has_reverse_image" in data:
            fields.append("has_reverse_image = ?")
            values.append(data["has_reverse_image"])
        if "image_ready" in data:
            fields.append("image_ready = ?")
            values.append(data["image_ready"])
        if "image_description" in data:
            fields.append("image_description = ?")
            values.append(data["image_description"])
        if "description" in data:
            fields.append("description = ?")
            values.append(data["description"])
        if "price_value_guide" in data:
            fields.append("price_value_guide = ?")
            values.append(data["price_value_guide"])

        if fields:
            fields.append("updated_at = CURRENT_TIMESTAMP")
            values.append(id)

            c.execute(f"UPDATE notes SET {', '.join(fields)} WHERE id = ?", values)
            conn.commit()
            return c.rowcount
        return 0
    except Exception as e:
        conn.rollback()
        conn.close()
        raise e
    finally:
        conn.close()


def delete_note(id):
    """Delete a bank note by ID"""
    conn = get_db()
    c = conn.cursor()

    try:
        c.execute("DELETE FROM notes WHERE id = ?", (id,))
        conn.commit()
        return c.rowcount
    except Exception as e:
        conn.rollback()
        conn.close()
        raise e
    finally:
        conn.close()


def get_all_notes(filters=None):
    """Get all bank notes with optional filtering"""
    conn = get_db()

    # Build query with optional filters
    conditions = []
    params = []

    filters = filters or {}
    if filters.get("year") is not None:
        conditions.append("year = ?")
        params.append(filters["year"])
    if filters.get("denomination") is not None:
        conditions.append("denomination = ?")
        params.append(filters["denomination"])
    if filters.get("grade") is not None:
        conditions.append("grade = ?")
        params.append(filters["grade"])

    query = "SELECT * FROM notes WHERE 1=1"
    if conditions:
        query += " AND " + " AND ".join(conditions)

    notes = conn.execute(query, params).fetchall()
    conn.close()
    return notes


def add_set(data):
    """Add a new coin set to the database"""
    conn = get_db()
    c = conn.cursor()

    try:
        c.execute("""
            INSERT INTO coin_sets (
                year, region, grade, details, population, pop_higher,
                serial_no, thumbnail_url, popup_url, image_description,
                width, height, has_obverse_image, has_reverse_image,
                image_ready, price_value_guide
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data.get("year"), data.get("region"), data.get("grade"),
            data.get("details"), data.get("population"), data.get("pop_higher"),
            data.get("serial_no"), data.get("thumbnail_url"), data.get("popup_url"),
            data.get("image_description"), data.get("width"), data.get("height"),
            data.get("has_obverse_image"), data.get("has_reverse_image"),
            data.get("image_ready"), data.get("price_value_guide")
        ))
        conn.commit()
        return c.lastrowid
    except Exception as e:
        conn.rollback()
        conn.close()
        raise e
    finally:
        conn.close()


def get_set(id):
    """Get a coin set by ID"""
    conn = get_db()
    set_data = conn.execute("SELECT * FROM coin_sets WHERE id = ?", (id,)).fetchone()
    conn.close()
    return set_data


def get_set_by_year(year):
    """Get a coin set by year"""
    conn = get_db()
    set_data = conn.execute("SELECT * FROM coin_sets WHERE year = ?", (year,)).fetchone()
    conn.close()
    return set_data


def get_all_sets(filters=None):
    """Get all coin sets with optional filtering"""
    conn = get_db()

    # Build query with optional filters
    conditions = []
    params = []

    filters = filters or {}
    if filters.get("year") is not None:
        conditions.append("year = ?")
        params.append(filters["year"])
    if filters.get("region") is not None:
        conditions.append("region = ?")
        params.append(filters["region"])
    if filters.get("grade") is not None:
        conditions.append("grade = ?")
        params.append(filters["grade"])

    query = "SELECT * FROM coin_sets WHERE 1=1"
    if conditions:
        query += " AND " + " AND ".join(conditions)

    sets = conn.execute(query, params).fetchall()
    conn.close()
    return sets


def update_set(id, data):
    """Update an existing coin set"""
    conn = get_db()
    c = conn.cursor()

    try:
        # Update only provided fields
        fields = []
        values = []

        if "year" in data:
            fields.append("year = ?")
            values.append(data["year"])
        if "region" in data:
            fields.append("region = ?")
            values.append(data["region"])
        if "grade" in data:
            fields.append("grade = ?")
            values.append(data["grade"])
        if "details" in data:
            fields.append("details = ?")
            values.append(data["details"])
        if "population" in data:
            fields.append("population = ?")
            values.append(data["population"])
        if "pop_higher" in data:
            fields.append("pop_higher = ?")
            values.append(data["pop_higher"])
        if "serial_no" in data:
            fields.append("serial_no = ?")
            values.append(data["serial_no"])
        if "thumbnail_url" in data:
            fields.append("thumbnail_url = ?")
            values.append(data["thumbnail_url"])
        if "popup_url" in data:
            fields.append("popup_url = ?")
            values.append(data["popup_url"])
        if "image_description" in data:
            fields.append("image_description = ?")
            values.append(data["image_description"])
        if "width" in data:
            fields.append("width = ?")
            values.append(data["width"])
        if "height" in data:
            fields.append("height = ?")
            values.append(data["height"])
        if "has_obverse_image" in data:
            fields.append("has_obverse_image = ?")
            values.append(data["has_obverse_image"])
        if "has_reverse_image" in data:
            fields.append("has_reverse_image = ?")
            values.append(data["has_reverse_image"])
        if "image_ready" in data:
            fields.append("image_ready = ?")
            values.append(data["image_ready"])
        if "price_value_guide" in data:
            fields.append("price_value_guide = ?")
            values.append(data["price_value_guide"])

        if fields:
            fields.append("updated_at = CURRENT_TIMESTAMP")
            values.append(id)

            c.execute(f"UPDATE coin_sets SET {', '.join(fields)} WHERE id = ?", values)
            conn.commit()
            return c.rowcount
        return 0
    except Exception as e:
        conn.rollback()
        conn.close()
        raise e
    finally:
        conn.close()


def delete_set(id):
    """Delete a coin set by ID"""
    conn = get_db()
    c = conn.cursor()

    try:
        c.execute("DELETE FROM coin_sets WHERE id = ?", (id,))
        conn.commit()
        return c.rowcount
    except Exception as e:
        conn.rollback()
        conn.close()
        raise e
    finally:
        conn.close()
