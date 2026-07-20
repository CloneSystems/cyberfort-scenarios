"""SmartGrid Meter Admin portal.

Web UI used by an SME energy operator to monitor a fleet of smart meters
over MQTT and to read register values directly from each meter via
Modbus TCP. INTENTIONALLY VULNERABLE for cyber-range training.
"""

import os
import time

from flask import (
    Flask,
    Markup,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from pymodbus.client.sync import ModbusTcpClient

from meter_admin.config import Config


app = Flask(__name__)
app.config.from_object(Config)

# In-memory user store. The product was shipped with one hard-wired
# operator account whose credentials match the documented defaults.
USERS = {
    Config.DEFAULT_OPERATOR_USER: Config.DEFAULT_OPERATOR_PASSWORD,
    "field_eng": "fieldeng",
}

# Latest telemetry sample is updated by the MQTT subscriber thread.
LATEST_TELEMETRY = {}


@app.route("/")
def index():
    if "user" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        # VULN-1: the product ships with operator account "admin/admin"
        # and no forced password change at first login.
        if USERS.get(username) == password:
            session["user"] = username
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
    return render_template(
        "dashboard.html",
        user=session["user"],
        telemetry=LATEST_TELEMETRY,
    )


@app.route("/meter/<int:meter_id>/registers")
def meter_registers(meter_id):
    if "user" not in session:
        return redirect(url_for("login"))

    # Live-read registers from the meter over Modbus TCP. The Modbus
    # protocol has no authentication, which is fine on a dedicated OT
    # subnet — but this lab exposes port 5020 to the trainee network.
    values = []
    try:
        client = ModbusTcpClient(Config.MODBUS_HOST, port=Config.MODBUS_PORT)
        client.connect()
        rr = client.read_holding_registers(address=0, count=10, unit=meter_id)
        if rr and not rr.isError():
            values = list(rr.registers)
        client.close()
    except Exception as exc:
        values = [f"error: {exc}"]
    return render_template(
        "registers.html",
        meter_id=meter_id,
        values=values,
        user=session["user"],
    )


# VULN-4: file upload accepts ANY file extension and saves it under the
# web-accessible uploads directory. Combined with a misconfigured Apache
# this is straight-line RCE; even in this scenario it lets the trainee
# drop a Python file that the team later executes.
@app.route("/firmware", methods=["GET", "POST"])
def firmware():
    if "user" not in session:
        return redirect(url_for("login"))
    message = None
    if request.method == "POST":
        f = request.files.get("file")
        if f:
            os.makedirs(Config.UPLOAD_DIR, exist_ok=True)
            target = os.path.join(Config.UPLOAD_DIR, f.filename)
            f.save(target)
            message = Markup(f"Uploaded <code>{f.filename}</code>")
    listing = []
    if os.path.isdir(Config.UPLOAD_DIR):
        listing = sorted(os.listdir(Config.UPLOAD_DIR))
    return render_template(
        "firmware.html",
        message=message,
        listing=listing,
        user=session["user"],
    )


@app.route("/healthz")
def healthz():
    return {"status": "ok"}, 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)


# ----- background MQTT subscriber -----
# Subscribes to "smartgrid/+/telemetry" and stuffs the most recent
# message per meter into LATEST_TELEMETRY for the dashboard.
def _mqtt_subscriber():
    import paho.mqtt.client as mqtt
    import json

    def on_connect(client, userdata, flags, rc):
        client.subscribe("smartgrid/+/telemetry")

    def on_message(client, userdata, msg):
        try:
            payload = json.loads(msg.payload.decode())
            meter_id = msg.topic.split("/")[1]
            LATEST_TELEMETRY[meter_id] = payload
        except Exception:
            pass

    client = mqtt.Client(client_id="meter-admin")
    client.on_connect = on_connect
    client.on_message = on_message
    for _ in range(20):
        try:
            client.connect(Config.MQTT_HOST, Config.MQTT_PORT, keepalive=30)
            break
        except Exception:
            time.sleep(2)
    else:
        return
    client.loop_forever()


import threading
threading.Thread(target=_mqtt_subscriber, daemon=True).start()
