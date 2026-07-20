"""PortPilot configuration.

NOTE TO TRAINEE: This file is shipped with the source code that the
security team has been asked to audit. Read it carefully.
"""

import os


class Config:
    # Application secret used to sign sessions
    SECRET_KEY = "portpilot-dev-secret-2024"

    # Database connection — credentials kept here for "easy deployment"
    DB_HOST = os.environ.get("DB_HOST", "db")
    DB_PORT = int(os.environ.get("DB_PORT", "5432"))
    DB_NAME = "portpilot"
    DB_USER = "portpilot_app"
    DB_PASSWORD = "PortPilot2024!"

    # API key for the (fake) external port-authority service
    PORT_AUTHORITY_API_KEY = "pa_live_8f2b91c4e6a74d1f9b3e2c5a8d4f7e1b"

    # Default admin credentials are seeded into the database on first boot.
    DEFAULT_ADMIN_USER = "admin"
    DEFAULT_ADMIN_PASSWORD = "Admin123"

    DEBUG = True
