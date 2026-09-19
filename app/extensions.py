from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail
from flask_wtf.csrf import CSRFProtect


# ==========================================================
# DATABASE
# ==========================================================

db = SQLAlchemy()


# ==========================================================
# MIGRATIONS
# ==========================================================

migrate = Migrate()


# ==========================================================
# LOGIN
# ==========================================================

login_manager = LoginManager()


# ==========================================================
# MAIL
# ==========================================================

mail = Mail()


# ==========================================================
# CSRF PROTECTION
# ==========================================================

csrf = CSRFProtect()