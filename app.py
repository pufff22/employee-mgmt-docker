"""Tiny Team HQ - a small employee management app (Flask + SQLite)."""
import os
import sqlite3

from flask import Flask, abort, flash, g, redirect, render_template, request, url_for

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-only-secret")
app.config["DATABASE"] = os.environ.get("DATABASE_PATH", "employees.db")

DEPARTMENTS = ["Engineering", "Design", "HR", "Marketing", "Finance", "Support"]


# ---------- database helpers ----------
def get_db():
    """Open one database connection per request."""
    if "db" not in g:
        g.db = sqlite3.connect(app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(error=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    """Create the employees table if it does not exist yet."""
    db = sqlite3.connect(app.config["DATABASE"])
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            department TEXT NOT NULL,
            role TEXT
        )
        """
    )
    db.commit()
    db.close()


# ---------- form helpers ----------
def read_form():
    return {
        "name": request.form.get("name", "").strip(),
        "email": request.form.get("email", "").strip(),
        "department": request.form.get("department", ""),
        "role": request.form.get("role", "").strip(),
    }


def check_form(data):
    """Return an error message, or None if everything is fine."""
    if not data["name"]:
        return "Please enter a name."
    if "@" not in data["email"]:
        return "Please enter a valid email."
    if data["department"] not in DEPARTMENTS:
        return "Please pick a department."
    return None


# ---------- pages ----------
@app.route("/")
def index():
    search = request.args.get("q", "").strip()
    db = get_db()
    if search:
        like = f"%{search}%"
        rows = db.execute(
            "SELECT * FROM employees "
            "WHERE name LIKE ? OR role LIKE ? OR department LIKE ? "
            "ORDER BY name",
            (like, like, like),
        ).fetchall()
    else:
        rows = db.execute("SELECT * FROM employees ORDER BY name").fetchall()
    return render_template("index.html", employees=rows, search=search)


@app.route("/add", methods=["GET", "POST"])
def add():
    if request.method == "POST":
        data = read_form()
        error = check_form(data)
        if error:
            flash(error)
            return render_template(
                "form.html", employee=data, departments=DEPARTMENTS, title="Add a teammate"
            )
        db = get_db()
        db.execute(
            "INSERT INTO employees (name, email, department, role) VALUES (?, ?, ?, ?)",
            (data["name"], data["email"], data["department"], data["role"]),
        )
        db.commit()
        flash(f"{data['name']} joined the team!")
        return redirect(url_for("index"))
    return render_template(
        "form.html", employee={}, departments=DEPARTMENTS, title="Add a teammate"
    )


@app.route("/edit/<int:emp_id>", methods=["GET", "POST"])
def edit(emp_id):
    db = get_db()
    row = db.execute("SELECT * FROM employees WHERE id = ?", (emp_id,)).fetchone()
    if row is None:
        abort(404)

    if request.method == "POST":
        data = read_form()
        error = check_form(data)
        if error:
            flash(error)
            return render_template(
                "form.html", employee=data, departments=DEPARTMENTS, title="Edit teammate"
            )
        db.execute(
            "UPDATE employees SET name = ?, email = ?, department = ?, role = ? WHERE id = ?",
            (data["name"], data["email"], data["department"], data["role"], emp_id),
        )
        db.commit()
        flash("Changes saved!")
        return redirect(url_for("index"))

    return render_template(
        "form.html", employee=dict(row), departments=DEPARTMENTS, title="Edit teammate"
    )


@app.route("/delete/<int:emp_id>", methods=["POST"])
def delete(emp_id):
    db = get_db()
    db.execute("DELETE FROM employees WHERE id = ?", (emp_id,))
    db.commit()
    flash("Teammate removed.")
    return redirect(url_for("index"))


@app.route("/health")
def health():
    """Used by the pipeline (and monitoring) to check the app is alive."""
    return {"status": "ok"}


init_db()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
