"""SmartGrid Meter Admin portal configuration.

NOTE TO TRAINEE: this is the source the security team has been asked to
audit. Read it carefully.
"""

import os


class Config:
    # Application secret
    SECRET_KEY = "smartgrid-meter-secret"

    # MQTT broker — also accessible from outside the container network on
    # the docker host's port 1883 with anonymous auth enabled.
    MQTT_HOST = os.environ.get("MQTT_HOST", "mqtt")
    MQTT_PORT = 1883
    MQTT_USER = "ops"
    MQTT_PASSWORD = "OpsTopSecret#2024"

    # Modbus TCP simulator (the "meter")
    MODBUS_HOST = os.environ.get("MODBUS_HOST", "modbus")
    MODBUS_PORT = 5020

    # API key for the regional grid operator's billing API
    BILLING_API_KEY = "bk_live_4f8e2c91ad7b6f0e5d3a8c4f9b1e7d2a"

    # Default operator credentials for first-boot. The team intends to
    # rotate these but has not done so yet.
    DEFAULT_OPERATOR_USER = "admin"
    DEFAULT_OPERATOR_PASSWORD = "admin"

    # Firmware upload landing directory
    UPLOAD_DIR = "/srv/admin/meter_admin/uploads"

    DEBUG = True
