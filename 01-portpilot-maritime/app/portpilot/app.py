"""PortPilot — vessel and cargo manifest manager for SME port operators.

This application is part of the CyberFort cyber range training scenario
"01-portpilot-maritime". It is INTENTIONALLY VULNERABLE. Do not deploy
outside an isolated training environment.
"""

import time

import psycopg2
from flask import (
    Flask,
    Markup,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from portpilot.config import Config


app = Flask(__name__)
app.config.from_object(Config)


def get_db():
    """Open a fresh DB connection. Retries because Postgres may still be booting."""
    for attempt in range(15):
        try:
            return psycopg2.connect(
                host=Config.DB_HOST,
                port=Config.DB_PORT,
                dbname=Config.DB_NAME,
                user=Config.DB_USER,
                password=Config.DB_PASSWORD,
            )
        except psycopg2.OperationalError:
            time.sleep(2)
    raise RuntimeError("database unreachable")


@app.route("/")
def index():
    if "user" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")

        # VULN-1 (CWE-89): user input is concatenated directly into the SQL
        # statement. The intent was "quick query for the MVP".
        query = (
            "SELECT id, username, role FROM users "
            f"WHERE username = '{username}' AND password = '{password}'"
        )

        conn = get_db()
        try:
            with conn.cursor() as cur:
                cur.execute(query)
                row = cur.fetchone()
        finally:
            conn.close()

        if row:
            session["user"] = {"id": row[0], "username": row[1], "role": row[2]}
            return redirect(url_for("dashboard"))
        error = "Invalid credentials"

    return render_template("login.html", error=error)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect(url_for("login"))

    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT imo, name, flag, status, eta FROM vessels ORDER BY eta LIMIT 10"
            )
            vessels = cur.fetchall()
    finally:
        conn.close()

    return render_template("dashboard.html", user=session["user"], vessels=vessels)


@app.route("/vessels")
def vessels():
    if "user" not in session:
        return redirect(url_for("login"))

    query_term = request.args.get("q", "")

    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT imo, name, flag, status, eta FROM vessels "
                "WHERE name ILIKE %s OR imo ILIKE %s ORDER BY name",
                (f"%{query_term}%", f"%{query_term}%"),
            )
            results = cur.fetchall()
    finally:
        conn.close()

    # VULN-2 (CWE-79): Markup() flags the string as safe so Jinja2 skips
    # autoescaping. The intent was "we want bold-able vessel names".
    heading = Markup(f"<h2>Results for: {query_term}</h2>")
    return render_template(
        "vessels.html",
        heading=heading,
        results=results,
        user=session["user"],
    )


@app.route("/manifests")
def manifests():
    if "user" not in session:
        return redirect(url_for("login"))

    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT m.id, v.name, m.cargo_type, m.weight_tonnes, m.consignee "
                "FROM manifests m JOIN vessels v ON v.id = m.vessel_id "
                "WHERE m.owner_user_id = %s ORDER BY m.id DESC",
                (session["user"]["id"],),
            )
            rows = cur.fetchall()
    finally:
        conn.close()

    return render_template("manifests.html", manifests=rows, user=session["user"])


# VULN-3 (CWE-285): the /admin/ blueprint relies on "obscurity" — there is
# no check that session["user"]["role"] == "admin", and no check that a
# session even exists. Any unauthenticated visitor who knows the URL gets
# every manifest in the system, including the confidential ones.
@app.route("/admin/manifests")
def admin_manifests():
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT m.id, v.name, m.cargo_type, m.weight_tonnes, "
                "m.consignee, m.notes "
                "FROM manifests m JOIN vessels v ON v.id = m.vessel_id "
                "ORDER BY m.id"
            )
            rows = cur.fetchall()
    finally:
        conn.close()
    return render_template("admin_manifests.html", manifests=rows)


@app.route("/healthz")
def healthz():
    return {"status": "ok"}, 200


if __name__ == "__main__":
    # debug=True is intentional for the training scenario; it exposes the
    # Werkzeug debugger and stack traces.
    app.run(host="0.0.0.0", port=8080, debug=True)
