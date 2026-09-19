from flask import Blueprint


# ==========================================================
# ADMIN BLUEPRINT
# ==========================================================

admin_bp = Blueprint(
    "admin",
    __name__
)


# ==========================================================
# GLOBAL ADMIN TEMPLATE VARIABLES
# ==========================================================

@admin_bp.app_context_processor
def inject_pending_applications_count():

    # Import inside the function to avoid circular imports
    from app.models import MembershipApplication


    # Count all pending membership applications
    pending_applications_count = (
        MembershipApplication.query
        .filter_by(
            status="Pending"
        )
        .count()
    )


    # Make the variable available to all templates
    return {
        "pending_applications_count":
        pending_applications_count
    }


# ==========================================================
# IMPORT ADMIN ROUTES
# ==========================================================

from . import routes