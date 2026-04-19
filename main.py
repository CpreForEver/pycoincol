from flask import Flask
from coin_collection import COINS_bp
from index import index_bp
from notes_collection import NOTES_bp
from database import load_api_token, init_db
import os


app = Flask(__name__)
app.secret_key = os.urandom(24)

app.register_blueprint(COINS_bp)
app.register_blueprint(index_bp)
app.register_blueprint(NOTES_bp)


if __name__ == "__main__":
    load_api_token()
    init_db()
    app.run(debug=True, host="0.0.0.0", port=5000)
