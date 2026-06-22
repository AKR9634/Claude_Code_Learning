from datetime import date, datetime

from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash

from database.db import get_db, init_db, seed_db

app = Flask(__name__)
app.secret_key = "dev-secret-change-me"  # TODO: move to env var before deploying


# ------------------------------------------------------------------ #
# Helpers                                                             #
# ------------------------------------------------------------------ #

def _parse_iso_date(value, default):
    """Try to parse `value` as YYYY-MM-DD.

    Returns (date, used_default_bool):
      - on success: (parsed_date, False)
      - on missing/empty/invalid input: (default, True)

    Never raises — invalid dates fall back silently to the default.
    """
    if not value:
        return default, True
    try:
        return datetime.strptime(value, "%Y-%m-%d").date(), False
    except ValueError:
        return default, True


# ------------------------------------------------------------------ #
# Database initialization                                              #
# ------------------------------------------------------------------ #

with app.app_context():
    init_db()
    seed_db()


# ------------------------------------------------------------------ #
# Routes                                                              #
# ------------------------------------------------------------------ #

@app.route("/")
def landing():
    return render_template("landing.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        # --- Validation ---
        if not name or not email or not password:
            return render_template("register.html", error="All fields are required."), 400

        if "@" not in email or "." not in email:
            return render_template("register.html", error="Please enter a valid email address."), 400

        if len(password) < 8:
            return render_template("register.html", error="Password must be at least 8 characters."), 400

        # --- Uniqueness check + insert ---
        conn = get_db()
        try:
            existing = conn.execute(
                "SELECT id FROM users WHERE email = ?", (email,)
            ).fetchone()
            if existing:
                return render_template("register.html", error="An account with that email already exists."), 400

            password_hash = generate_password_hash(password)
            cursor = conn.execute(
                "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
                (name, email, password_hash),
            )
            conn.commit()
            user_id = cursor.lastrowid
        finally:
            conn.close()

        # --- Log the user in ---
        session["user_id"] = user_id
        session["user_name"] = name
        return redirect(url_for("profile"))

    # GET — render the empty form
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        # --- Validation ---
        if not email or not password:
            return render_template("login.html", error="Please enter your email and password."), 400

        # --- Credential lookup ---
        conn = get_db()
        try:
            row = conn.execute(
                "SELECT id, name, password_hash FROM users WHERE email = ?", (email,)
            ).fetchone()
        finally:
            conn.close()

        if row is None or not check_password_hash(row["password_hash"], password):
            return render_template("login.html", error="Invalid email or password."), 401

        # --- Log the user in ---
        session["user_id"] = row["id"]
        session["user_name"] = row["name"]
        return redirect(url_for("profile"))

    # GET — render the empty form
    return render_template("login.html")


@app.route("/terms")
def terms():
    return render_template("terms.html")


@app.route("/privacy")
def privacy():
    return render_template("privacy.html")


# ------------------------------------------------------------------ #
# Placeholder routes — students will implement these                  #
# ------------------------------------------------------------------ #

@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return redirect(url_for("landing"))


@app.route("/profile")
def profile():
    if "user_id" not in session:
        return redirect(url_for("login"))

    # --- Parse optional start_date / end_date query params ---
    today = date.today()
    default_start = today.replace(day=1)
    default_end = today

    start_date, start_defaulted = _parse_iso_date(
        request.args.get("start_date"), default_start
    )
    end_date, end_defaulted = _parse_iso_date(
        request.args.get("end_date"), default_end
    )

    # "This month" only when BOTH were defaulted.
    is_default_range = start_defaulted and end_defaulted

    # Silently swap if the user inverted the range.
    if start_date > end_date:
        start_date, end_date = end_date, start_date

    start_iso = start_date.isoformat()
    end_iso = end_date.isoformat()

    # --- Single connection: load user + filtered expenses ---
    conn = get_db()
    try:
        user = conn.execute(
            "SELECT name, email, created_at FROM users WHERE id = ?",
            (session["user_id"],),
        ).fetchone()

        expenses = conn.execute(
            """
            SELECT date, category, amount, description
            FROM expenses
            WHERE user_id = ? AND date BETWEEN ? AND ?
            ORDER BY date DESC, id DESC
            """,
            (session["user_id"], start_iso, end_iso),
        ).fetchall()
    finally:
        conn.close()

    return render_template(
        "profile.html",
        user=user,
        start_date=start_iso,
        end_date=end_iso,
        expenses=expenses,
        is_default_range=is_default_range,
    )


@app.route("/expenses/add")
def add_expense():
    return "Add expense — coming in Step 7"


@app.route("/expenses/<int:id>/edit")
def edit_expense(id):
    return "Edit expense — coming in Step 8"


@app.route("/expenses/<int:id>/delete")
def delete_expense(id):
    return "Delete expense — coming in Step 9"


if __name__ == "__main__":
    app.run(debug=True, port=5001)
