
import os


# ==========================================================
# PROJECT PATHS
# ==========================================================

BASE_DIR = os.path.abspath(
    os.path.dirname(__file__)
)

INSTANCE_DIR = os.path.join(
    BASE_DIR,
    "instance"
)

# Create the instance directory if it does not exist
os.makedirs(
    INSTANCE_DIR,
    exist_ok=True
)


# ==========================================================
# APPLICATION CONFIGURATION
# ==========================================================

class Config:

    # ======================================================
    # ENVIRONMENT
    # ======================================================

    ENVIRONMENT = os.environ.get(
        "APP_ENV",
        "development"
    )

    DEBUG = ENVIRONMENT == "development"

    TESTING = False


    # ======================================================
    # SECURITY
    # ======================================================

    SECRET_KEY = os.environ.get(
        "SECRET_KEY",
        "apex-development-secret-key"
    )

    # Use secure cookies in production
    SESSION_COOKIE_SECURE = (
        ENVIRONMENT == "production"
    )

    SESSION_COOKIE_HTTPONLY = True

    SESSION_COOKIE_SAMESITE = "Lax"

    REMEMBER_COOKIE_SECURE = (
        ENVIRONMENT == "production"
    )

    REMEMBER_COOKIE_HTTPONLY = True

    REMEMBER_COOKIE_SAMESITE = "Lax"


    # ======================================================
    # URL AND HTTPS CONFIGURATION
    # ======================================================

    # Used when Flask generates URLs outside an active request
    PREFERRED_URL_SCHEME = os.environ.get(
        "PREFERRED_URL_SCHEME",
        "http"
    )

    # Enable this in production if your application
    # is running behind a trusted HTTPS reverse proxy.
    ENABLE_PROXY_FIX = (
        ENVIRONMENT == "production"
    )


    # ======================================================
    # DATABASE
    # ======================================================

    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        "sqlite:///" + os.path.join(
            INSTANCE_DIR,
            "acg.db"
        )
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False


    # ======================================================
    # FILE UPLOADS
    # ======================================================

    MAX_CONTENT_LENGTH = (
        5 * 1024 * 1024
    )

    UPLOAD_FOLDER = os.path.join(
        BASE_DIR,
        "app",
        "static",
        "uploads"
    )

    ALLOWED_EXTENSIONS = {
        "jpg",
        "jpeg",
        "png",
        "webp"
    }


    # ======================================================
    # EMAIL CONFIGURATION
    # ======================================================

    MAIL_SERVER = os.environ.get(
        "MAIL_SERVER",
        "smtp.gmail.com"
    )

    MAIL_PORT = int(
        os.environ.get(
            "MAIL_PORT",
            "587"
        )
    )

    MAIL_USE_TLS = (
        os.environ.get(
            "MAIL_USE_TLS",
            "true"
        ).lower() == "true"
    )

    MAIL_USE_SSL = (
        os.environ.get(
            "MAIL_USE_SSL",
            "false"
        ).lower() == "true"
    )

    MAIL_USERNAME = os.environ.get(
        "MAIL_USERNAME"
    )

    MAIL_PASSWORD = os.environ.get(
        "MAIL_PASSWORD"
    )

    MAIL_DEFAULT_SENDER = os.environ.get(
        "MAIL_DEFAULT_SENDER",
        "Apex Citizens of Ghana"
    )


    # ======================================================
    # ADMIN EMAIL
    # ======================================================

    ADMIN_EMAIL = os.environ.get(
        "ADMIN_EMAIL"
    )