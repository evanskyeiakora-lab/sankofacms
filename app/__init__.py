
from flask import Flask, render_template, request
from datetime import datetime

from werkzeug.middleware.proxy_fix import ProxyFix

from config import Config

from .extensions import (
    db,
    migrate,
    login_manager,
    mail,
    csrf
)

from app.context_processors import inject_settings


# ==========================================================
# ERROR HANDLERS
# ==========================================================

def register_error_handlers(app):

    @app.errorhandler(404)
    def page_not_found(error):
        return render_template(
            "errors/404.html"
        ), 404

    @app.errorhandler(403)
    def access_forbidden(error):
        return render_template(
            "errors/403.html"
        ), 403

    @app.errorhandler(500)
    def internal_server_error(error):

        # Roll back any failed database transaction
        db.session.rollback()

        return render_template(
            "errors/500.html"
        ), 500


# ==========================================================
# MAINTENANCE MODE
# ==========================================================

def register_maintenance_mode(app):

    @app.before_request
    def check_maintenance_mode():

        # Allow static files
        if request.endpoint == "static":
            return None

        # Allow authentication routes
        if request.path.startswith("/auth/"):
            return None

        # Allow administration routes
        if request.path.startswith("/admin/"):
            return None

        # Allow the maintenance page itself
        if request.endpoint == "main.maintenance":
            return None

        # Import inside the function to help avoid circular imports
        from app.models import Settings
        from app.tenant import get_current_client

        # Identify the current tenant
        current_client = get_current_client()

        # If no tenant is found, continue normally
        if current_client is None:
            return None

        # Get settings for the current tenant
        settings = (
            Settings.query
            .filter_by(
                client_id=current_client.id
            )
            .first()
        )

        # Maintenance mode is disabled
        if not settings or not settings.maintenance_mode:
            return None

        # Display maintenance page
        return render_template(
            "maintenance.html",
            current_client=current_client,
            settings=settings
        ), 503


# ==========================================================
# APPLICATION FACTORY
# ==========================================================

def create_app():

    app = Flask(__name__)

    # Load application configuration
    app.config.from_object(Config)


    # ======================================================
    # HTTPS / REVERSE PROXY CONFIGURATION
    # ======================================================

    # Only enable ProxyFix in production when the application
    # is behind a trusted reverse proxy.
    #
    # The proxy must be configured to forward the correct
    # X-Forwarded-* headers.

    if app.config.get("ENABLE_PROXY_FIX"):

        app.wsgi_app = ProxyFix(
            app.wsgi_app,
            x_for=1,
            x_proto=1,
            x_host=1
        )


    # ======================================================
    # INITIALIZE EXTENSIONS
    # ======================================================

    db.init_app(app)

    migrate.init_app(
        app,
        db
    )

    login_manager.init_app(app)

    mail.init_app(app)

    csrf.init_app(app)


    # ======================================================
    # FLASK-LOGIN CONFIGURATION
    # ======================================================

    login_manager.login_view = "auth.login"

    login_manager.login_message_category = "warning"


    # ======================================================
    # ERROR HANDLERS
    # ======================================================

    register_error_handlers(app)


    # ======================================================
    # MAINTENANCE MODE
    # ======================================================

    register_maintenance_mode(app)


    # ======================================================
    # IMPORT BLUEPRINTS
    # ======================================================

    from .main import main_bp
    from .auth import auth_bp
    from .admin import admin_bp
    from .news import news_bp
    from .hero import hero_bp
    from .gallery import gallery_bp
    from .members import members_bp
    from .contact import contact_bp
    from .settings import settings_bp
    from .pages import pages_bp
    from .events import events_bp
    from .users import users_bp
    from .leaders import leaders_bp


    # ======================================================
    # REGISTER BLUEPRINTS
    # ======================================================

    app.register_blueprint(
        leaders_bp,
        url_prefix="/admin/leaders"
    )

    app.register_blueprint(main_bp)

    app.register_blueprint(
        auth_bp,
        url_prefix="/auth"
    )

    app.register_blueprint(
        admin_bp,
        url_prefix="/admin"
    )

    app.register_blueprint(news_bp)

    app.register_blueprint(hero_bp)

    app.register_blueprint(gallery_bp)

    app.register_blueprint(members_bp)

    app.register_blueprint(contact_bp)

    app.register_blueprint(settings_bp)

    app.register_blueprint(pages_bp)

    app.register_blueprint(events_bp)

    app.register_blueprint(users_bp)


    # ======================================================
    # GLOBAL CONTEXT PROCESSORS
    # ======================================================

    app.context_processor(
        inject_settings
    )


    @app.context_processor
    def inject_now():

        return {
            "current_year": datetime.now().year
        }


    # ======================================================
    # RETURN APPLICATION
    # ======================================================

    return app