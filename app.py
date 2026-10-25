
import os
import sqlite3
import secrets
from flask_wtf.csrf import CSRFProtect
from pathlib import Path


from flask import (
    Flask, request, redirect, url_for, session,
    render_template_string, send_from_directory, abort
)
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

from database import get_db, init_db

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024
app.secret_key = os.environ.get("TRUSTVAULT_SECRET", secrets.token_hex(32))
csrf = CSRFProtect(app)
@app.errorhandler(413)
def handle_file_too_large(error):
    return "File too large. Maximum upload size is 10 MB.", 413

BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "static" / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_EXTENSIONS = {"pdf"}

init_db()

PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>TrustVault</title>
    <style>
        body { font-family: Arial; background: #f1f5f9; padding: 35px 15px; }
        .card { background: white; max-width: 650px; margin: auto;
                padding: 25px; border-radius: 12px; }
        input, button { padding: 10px; margin: 7px 0; }
        input { max-width: 100%; }
        button { background: #1d4ed8; color: white; border: 0;
                 border-radius: 5px; cursor: pointer; }
        a { color: #1d4ed8; }
        .message { color: #166534; }
        .error { color: #b91c1c; }
        li { margin: 12px 0; }
    </style>
</head>
<body>
<div class="card">
    <h1>TrustVault</h1>
    <h3>{{ title }}</h3>

    {% if message %}
        <p class="{{ category }}">{{ message }}</p>
    {% endif %}

    {% if page == "auth" %}
        <form method="POST">
            <input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
            <input name="username" placeholder="Username"
                   minlength="3" maxlength="50" required>
            <br>
            <input name="password" type="password" placeholder="Password"
                   minlength="8" maxlength="128" required>
            <br>
            <button type="submit">{{ title }}</button>
        </form>
        {% if title == "Login" %}
            <p>New user? <a href="/register">Register</a></p>
        {% else %}
            <p>Already registered? <a href="/login">Login</a></p>
        {% endif %}
    {% else %}
        <p>Welcome, {{ username }}!</p>
        <p>Role: {{ role }}</p>

        <h3>Upload a PDF</h3>
        <form action="/upload" method="POST" enctype="multipart/form-data">
            <input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
            <input type="file" name="document" accept=".pdf,application/pdf" required>
            <br>
            <button type="submit">Upload PDF</button>
        </form>

        <h3>Your Documents</h3>
        {% if documents %}
            <ul>
            {% for doc in documents %}
                <li>
                    {{ doc["filename"] }}
                    — <a href="/download/{{ doc['id'] }}">Download</a>
                </li>
            {% endfor %}
            </ul>
        {% else %}
            <p>No documents uploaded yet.</p>
        {% endif %}

        <p><a href="/logout">Logout</a></p>
    {% endif %}
</div>
</body>
</html>
"""


def render_page(page, title, username="", role="", documents=None,
                message="", category=""):
    return render_template_string(
        PAGE, page=page, title=title, username=username, role=role,
        documents=documents or [], message=message, category=category
    )


def log_action(conn, user_id, action, document_id=None):
    conn.execute(
        "INSERT INTO audit_logs (user_id, action, document_id) VALUES (?, ?, ?)",
        (user_id, action, document_id)
    )


def current_user():
    user_id = session.get("user_id")
    if user_id is None:
        return None

    conn = get_db()
    user = conn.execute(
        "SELECT id, username, role FROM users WHERE id = ?",
        (user_id,)
    ).fetchone()
    conn.close()
    return user


@app.route("/")
def home():
    user = current_user()
    if user is None:
        session.clear()
        return redirect(url_for("login"))

    conn = get_db()
    documents = conn.execute(
        "SELECT id, filename FROM documents WHERE owner_id = ? ORDER BY id DESC",
        (user["id"],)
    ).fetchall()
    conn.close()

    return render_page(
        "home", "Dashboard", user["username"], user["role"], documents
    )


@app.route("/register", methods=["GET", "POST"])
def register():
    message = ""
    category = "error"

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if not 3 <= len(username) <= 50:
            message = "Username must be 3–50 characters."
        elif not 8 <= len(password) <= 128:
            message = "Password must be 8–128 characters."
        else:
            conn = get_db()
            try:
                conn.execute(
                    "INSERT INTO users (username, password_hash, role) VALUES (?, ?, 'Viewer')",
                    (username, generate_password_hash(password))
                )
                conn.commit()
                message = "Account created! Please log in."
                category = "message"
            except sqlite3.IntegrityError:
                message = "Username already exists."
            finally:
                conn.close()

    return render_page("auth", "Register", message=message, category=category)


@app.route("/login", methods=["GET", "POST"])
def login():
    message = ""

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        conn = get_db()
        user = conn.execute(
            "SELECT id, password_hash FROM users WHERE username = ?",
            (username,)
        ).fetchone()
        conn.close()

        if user and check_password_hash(user["password_hash"], password):
            session.clear()
            session["user_id"] = user["id"]
            return redirect(url_for("home"))

        message = "Invalid username or password."

    return render_page("auth", "Login", message=message, category="error")


@app.route("/upload", methods=["POST"])
def upload():
    user = current_user()
    if user is None:
        session.clear()
        return redirect(url_for("login"))

    file = request.files.get("document")

    if file is None or not file.filename:
        abort(400, "Please choose a PDF file.")

    original_name = secure_filename(file.filename)

    if not original_name or Path(original_name).suffix.lower() != ".pdf":
        abort(400, "Only PDF files are allowed.")

    # Verify the file starts with the PDF signature.
    if file.stream.read(5) != b"%PDF-":
        abort(400, "The uploaded file is not a valid PDF.")
    file.stream.seek(0)

    # Limit uploads to 10 MB.
    file.stream.seek(0, os.SEEK_END)
    size = file.stream.tell()
    file.stream.seek(0)
    if size > 10 * 1024 * 1024:
        abort(413, "Maximum file size is 10 MB.")

    stored_name = secrets.token_hex(16) + ".pdf"
    destination = UPLOAD_DIR / stored_name
    file.save(destination)

    
    conn = get_db()
    try:
        cursor = conn.execute(
            "INSERT INTO documents (filename, stored_filename, owner_id) VALUES (?, ?, ?)",
            (original_name, stored_name, user["id"])
        )
        document_id = cursor.lastrowid
        log_action(conn, user["id"], "UPLOAD", document_id)
        conn.commit()
    except Exception:
        conn.rollback()
        destination.unlink(missing_ok=True)
        raise
    finally:
        conn.close()

    return redirect(url_for("home"))



@app.route("/download/<int:document_id>")
def download(document_id):
    user = current_user()
    if user is None:
        session.clear()
        return redirect(url_for("login"))

    conn = get_db()
    doc = conn.execute(
        "SELECT id, filename, stored_filename, owner_id "
        "FROM documents WHERE id = ?",
        (document_id,)
    ).fetchone()

    if doc is None:
        conn.close()
        abort(404)

    # Only the document owner can download it for now.
    if doc["owner_id"] != user["id"]:
        conn.close()
        abort(403)

    log_action(conn, user["id"], "DOWNLOAD", document_id)
    conn.commit()
    conn.close()

    return send_from_directory(
        UPLOAD_DIR, doc["stored_filename"],
        as_attachment=True, download_name=doc["filename"]
    )


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)
