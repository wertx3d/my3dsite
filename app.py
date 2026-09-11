from flask import Flask, render_template, request, redirect, url_for
import os
import uuid
import sqlite3

app = Flask(__name__)
UPLOAD_FOLDER = "static/models"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def init_db():
    conn = sqlite3.connect("models.db")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS models (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            filename TEXT
        )
    """)
    conn.commit()
    conn.close()

@app.route("/")
def index():
    conn = sqlite3.connect("models.db")
    conn.row_factory = sqlite3.Row
    models = conn.execute("SELECT * FROM models ORDER BY id DESC").fetchall()
    conn.close()
    return render_template("index.html", models=models)

@app.route("/upload", methods=["POST"])
def upload():
    name = request.form.get("name")
    file = request.files.get("model")
    if file and name:
        ext = file.filename.rsplit(".", 1)[-1].lower()
        filename = uuid.uuid4().hex + "." + ext
        file.save(os.path.join(UPLOAD_FOLDER, filename))
        conn = sqlite3.connect("models.db")
        conn.execute("INSERT INTO models (name, filename) VALUES (?, ?)", (name, filename))
        conn.commit()
        conn.close()
    return redirect(url_for("index"))

init_db()
