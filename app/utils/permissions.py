from functools import wraps

from flask import abort

from flask_login import (
    current_user,
    login_required
)


# ==========================================================
# Role-Based Permission Decorator
# ==========================================================

def roles_required(*allowed_roles):
    """
    Restrict access to users with one of the specified roles.

    Example:

        @roles_required(
            "Super Admin",
            "Administrator",
            "Editor"
        )

    A user only needs to have one of the specified roles.
    """

    def decorator(view):

        @wraps(view)
        @login_required
        def wrapped(*args, **kwargs):

            # --------------------------------------------------
            # Check user's role
            # --------------------------------------------------

            if current_user.role not in allowed_roles:
                abort(403)

            # --------------------------------------------------
            # Permission granted
            # --------------------------------------------------

            return view(*args, **kwargs)

        return wrapped

    return decorator


# ==========================================================
# Administrator Permission
# ==========================================================

def admin_required(view):
    """
    Allow users who have administrator privileges.

    This preserves the existing Apex CMS behavior by checking
    current_user.is_admin.
    """

    @wraps(view)
    @login_required
    def wrapped(*args, **kwargs):

        if not current_user.is_admin:
            abort(403)

        return view(*args, **kwargs)

    return wrapped


# ==========================================================
# Super Administrator Permission
# ==========================================================

def super_admin_required(view):
    """
    Allow Super Admins only.
    """

    @wraps(view)
    @login_required
    def wrapped(*args, **kwargs):

        if not current_user.is_super_admin:
            abort(403)

        return view(*args, **kwargs)

    return wrapped