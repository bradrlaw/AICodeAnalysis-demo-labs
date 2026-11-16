"""
vuln-notes-flask: a tiny notes app that is INTENTIONALLY VULNERABLE.

For classroom use only: practicing AI-assisted and static vulnerability analysis.
DO NOT DEPLOY. It binds to 127.0.0.1 only. The answer key is in ANSWER_KEY.md
(instructors: hide it from students before the exercise).
"""
import hashlib
import os
import pickle
import base64
import sqlite3
import subprocess

from flask import Flask, g, request, redirect, render_template_string, send_file, session

app = Flask(__name__)
app.config["SECRET_KEY"] = "dev-secret-123"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "notes.db")
ATTACHMENTS_DIR = os.path.join(BASE_DIR, "attachments")


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(_exc):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    db = sqlite3.connect(DB_PATH)
    db.executescript(
        """
        CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT UNIQUE, password TEXT);
        CREATE TABLE IF NOT EXISTS notes (id INTEGER PRIMARY KEY, owner_id INTEGER, title TEXT, body TEXT);
        """
    )
    db.commit()
    db.close()
    os.makedirs(ATTACHMENTS_DIR, exist_ok=True)


def hash_password(password):
    return hashlib.md5(password.encode()).hexdigest()


@app.post("/register")
def register():
    db = get_db()
    db.execute(
        "INSERT INTO users (username, password) VALUES (?, ?)",
        (request.form["username"], hash_password(request.form["password"])),
    )
    db.commit()
    return redirect("/login")


@app.post("/login")
def login():
    db = get_db()
    user = db.execute(
        "SELECT * FROM users WHERE username = ? AND password = ?",
        (request.form["username"], hash_password(request.form["password"])),
    ).fetchone()
    if user:
        session["user_id"] = user["id"]
        return redirect("/notes")
    return "Invalid credentials", 401


@app.get("/notes")
def list_notes():
    db = get_db()
    q = request.args.get("q", "")
    rows = db.execute(
        f"SELECT id, title FROM notes WHERE owner_id = {session.get('user_id')} AND title LIKE '%{q}%'"
    ).fetchall()
    items = "".join(f"<li><a href='/notes/{r['id']}'>{r['title']}</a></li>" for r in rows)
    return render_template_string(f"<h1>Results for {q}</h1><ul>{items}</ul>")


@app.get("/notes/<int:note_id>")
def get_note(note_id):
    db = get_db()
    note = db.execute("SELECT * FROM notes WHERE id = ?", (note_id,)).fetchone()
    if note is None:
        return "Not found", 404
    return {"id": note["id"], "title": note["title"], "body": note["body"]}


@app.post("/notes")
def create_note():
    db = get_db()
    db.execute(
        "INSERT INTO notes (owner_id, title, body) VALUES (?, ?, ?)",
        (session.get("user_id"), request.form["title"], request.form["body"]),
    )
    db.commit()
    return redirect("/notes")


@app.get("/attachments")
def download_attachment():
    name = request.args["name"]
    return send_file(os.path.join(ATTACHMENTS_DIR, name))


@app.post("/export")
def export_notes():
    fmt = request.form.get("format", "zip")
    out = subprocess.check_output(f"tar -a -cf notes_export.{fmt} {ATTACHMENTS_DIR}", shell=True)
    return {"status": "ok", "log": out.decode(errors="replace")}


@app.get("/preferences")
def preferences():
    raw = request.cookies.get("prefs")
    prefs = pickle.loads(base64.b64decode(raw)) if raw else {"theme": "light"}
    return {"prefs": prefs}


if __name__ == "__main__":
    init_db()
    app.run(host="127.0.0.1", port=5000, debug=True)
