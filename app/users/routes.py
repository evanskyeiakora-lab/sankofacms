
from flask import (
    render_template,
    request,
    redirect,
    url_for,
    flash,
    current_app,
)

from flask_login import (
    login_required,
    current_user,
)

from . import users_bp

from .forms import (
    UserForm,
    EditUserForm,
    ChangePasswordForm,
)

from .services import UserService

from app.extensions import db
from app.models import User, Client

from app.tenant import get_current_client

from app.utils.helpers import flash_success
from app.utils.permissions import admin_required


# ==========================================================
# CONSTANTS
# ==========================================================

USER_ROLES = (
    "Super Admin",
    "Administrator",
    "Editor",
    "Author",
)


# ==========================================================
# AUTHORIZATION HELPERS
# ==========================================================

def is_super_admin():
    """
    Check whether the current user is a Super Admin.
    """

    return bool(
        current_user.is_authenticated
        and current_user.is_super_admin
    )


def get_client():
    """
    Get the active organization from the current domain.
    """

    return get_current_client()


def require_client():
    """
    Require an active organization for tenant users.
    """

    client = get_client()

    if not client:

        flash(
            "No active organization was found for this domain.",
            "danger",
        )

        return None

    return client


# ==========================================================
# ORGANIZATION HELPERS
# ==========================================================

def client_label(client):
    """
    Return a readable organization label.

    Adjust the field if your Client model uses
    a different organization-name column.
    """

    return (
        getattr(client, "name", None)
        or getattr(client, "title", None)
        or getattr(client, "organization_name", None)
        or f"Organization {client.id}"
    )


def configure_client_choices(form):
    """
    Configure organization choices.

    Super Admin:
        Can select any organization.

    Regular Administrator:
        Can only use the current organization.
    """

    if is_super_admin():

        clients = (
            Client.query
            .order_by(Client.id.asc())
            .all()
        )

        form.client_id.choices = [
            (
                client.id,
                client_label(client),
            )
            for client in clients
        ]

    else:

        client = get_client()

        if client:

            form.client_id.choices = [
                (
                    client.id,
                    client_label(client),
                )
            ]

        else:

            form.client_id.choices = []


def restrict_super_admin_role(form):
    """
    Remove the Super Admin role from forms
    used by non-Super-Admins.
    """

    if not is_super_admin():

        form.role.choices = [
            choice
            for choice in form.role.choices
            if choice[0] != "Super Admin"
        ]

    return form


def configure_form(form):
    """
    Apply all common form configuration.
    """

    configure_client_choices(form)
    restrict_super_admin_role(form)

    return form


# ==========================================================
# ORGANIZATION RESOLUTION
# ==========================================================

def resolve_client_id(form, selected_role):
    """
    Resolve the organization for a user.

    Super Admin:
        May select an organization.
        A platform-level Super Admin can have client_id=None.

    Regular Administrator:
        Automatically uses the current organization.
        Cannot assign another organization.
    """

    # ------------------------------------------------------
    # SUPER ADMIN
    # ------------------------------------------------------

    if is_super_admin():

        selected_client_id = form.client_id.data

        # Platform-level Super Admin
        if selected_role == "Super Admin":

            if not selected_client_id:
                return None

        if not selected_client_id:

            raise ValueError(
                "Please select an organization for this user."
            )

        client = db.session.get(
            Client,
            selected_client_id,
        )

        if not client:

            raise ValueError(
                "The selected organization does not exist."
            )

        return client.id

    # ------------------------------------------------------
    # REGULAR ADMINISTRATOR
    # ------------------------------------------------------

    client = require_client()

    if not client:

        raise ValueError(
            "No active organization was found."
        )

    selected_client_id = form.client_id.data

    # Prevent a regular administrator from assigning
    # a user to another organization.
    if (
        selected_client_id
        and selected_client_id != client.id
    ):

        raise ValueError(
            "You cannot assign users to another organization."
        )

    # Automatically assign the current organization.
    return client.id


# ==========================================================
# USER ACCESS
# ==========================================================

def get_managed_user(user_id):
    """
    Retrieve a user within the current user's scope.

    Super Admin:
        Can access users from all organizations.

    Regular Administrator:
        Can access users only from the current organization.
    """

    if is_super_admin():

        return (
            User.query
            .filter(
                User.id == user_id
            )
            .first_or_404()
        )

    client = require_client()

    if not client:
        return None

    return (
        User.query
        .filter(
            User.id == user_id,
            User.client_id == client.id,
        )
        .first_or_404()
    )


def can_manage_user(user):
    """
    Confirm that the current user can manage the target user.
    """

    if is_super_admin():
        return True

    client = get_client()

    if not client:
        return False

    return user.client_id == client.id


# ==========================================================
# USERS LIST
# ==========================================================

@users_bp.route("/")
@admin_required
def index():

    page = request.args.get(
        "page",
        1,
        type=int,
    )

    search = (
        request.args
        .get("search", "")
        .strip()
    )

    # ------------------------------------------------------
    # BASE QUERY
    # ------------------------------------------------------

    if is_super_admin():

        query = User.query

    else:

        client = require_client()

        if not client:

            return redirect(
                url_for("main.home")
            )

        query = (
            User.query
            .filter(
                User.client_id == client.id
            )
        )

    # ------------------------------------------------------
    # SEARCH
    # ------------------------------------------------------

    if search:

        search_term = f"%{search}%"

        query = query.filter(
            (
                User.first_name.ilike(search_term)
                |
                User.last_name.ilike(search_term)
                |
                User.username.ilike(search_term)
                |
                User.email.ilike(search_term)
            )
        )

    # ------------------------------------------------------
    # PAGINATION
    # ------------------------------------------------------

    users = (
        query
        .order_by(
            User.first_name.asc(),
            User.last_name.asc(),
            User.id.asc(),
        )
        .paginate(
            page=page,
            per_page=10,
            error_out=False,
        )
    )

    return render_template(
        "admin/users/index.html",
        users=users,
        search=search,
    )


# ==========================================================
# CREATE USER
# ==========================================================

@users_bp.route(
    "/create",
    methods=["GET", "POST"],
)
@admin_required
def create():

    form = UserForm()

    configure_form(form)

    # ------------------------------------------------------
    # REGULAR ADMINISTRATOR
    # Automatically select current organization.
    # ------------------------------------------------------

    if not is_super_admin():

        client = get_client()

        if client:

            form.client_id.data = client.id

    # ------------------------------------------------------
    # FORM SUBMISSION
    # ------------------------------------------------------

    if form.validate_on_submit():

        # --------------------------------------------------
        # SERVER-SIDE ROLE PROTECTION
        # --------------------------------------------------

        if (
            form.role.data == "Super Admin"
            and not is_super_admin()
        ):

            flash(
                "Only a Super Admin can create a Super Admin account.",
                "danger",
            )

            return render_template(
                "admin/users/create.html",
                form=form,
            )

        try:

            assigned_client_id = resolve_client_id(
                form,
                form.role.data,
            )

            UserService.create_user(
                form,
                client_id=assigned_client_id,
            )

            flash_success(
                "User created successfully."
            )

            return redirect(
                url_for("users.index")
            )

        except ValueError as error:

            db.session.rollback()

            flash(
                str(error),
                "danger",
            )

        except Exception:

            db.session.rollback()

            current_app.logger.exception(
                "USER CREATION ERROR"
            )

            flash(
                "An unexpected error occurred while creating the user.",
                "danger",
            )

    elif request.method == "POST":

        current_app.logger.warning(
            "USER CREATION FORM ERRORS: %s",
            form.errors,
        )

    return render_template(
        "admin/users/create.html",
        form=form,
    )


# ==========================================================
# EDIT USER
# ==========================================================

@users_bp.route(
    "/<int:id>/edit",
    methods=["GET", "POST"],
)
@admin_required
def edit(id):

    user = get_managed_user(id)

    if user is None:

        return redirect(
            url_for("users.index")
        )

    # ------------------------------------------------------
    # SUPER ADMIN PROTECTION
    # ------------------------------------------------------

    if (
        user.is_super_admin
        and not is_super_admin()
    ):

        flash(
            "Only a Super Admin can edit a Super Admin account.",
            "danger",
        )

        return redirect(
            url_for("users.index")
        )

    # ------------------------------------------------------
    # FORM
    # ------------------------------------------------------

    # Do not use EditUserForm(obj=user).
    # This prevents the existing photo filename
    # from being placed in the FileField.

    form = EditUserForm()

    configure_form(form)

    # ------------------------------------------------------
    # POPULATE FORM ON GET
    # ------------------------------------------------------

    if request.method == "GET":

        form.first_name.data = user.first_name
        form.last_name.data = user.last_name
        form.username.data = user.username
        form.email.data = user.email
        form.phone.data = user.phone
        form.role.data = user.role
        form.client_id.data = user.client_id
        form.is_active.data = bool(
            user.is_active
        )

    # ------------------------------------------------------
    # FORM SUBMISSION
    # ------------------------------------------------------

    if form.validate_on_submit():

        # --------------------------------------------------
        # ROLE PROTECTION
        # --------------------------------------------------

        if (
            form.role.data == "Super Admin"
            and not is_super_admin()
        ):

            flash(
                "Only a Super Admin can assign the Super Admin role.",
                "danger",
            )

            return render_template(
                "admin/users/edit.html",
                form=form,
                user=user,
            )

        try:

            assigned_client_id = resolve_client_id(
                form,
                form.role.data,
            )

            # --------------------------------------------------
            # REGULAR ADMINISTRATOR TENANT CHECK
            # --------------------------------------------------

            if not is_super_admin():

                client = require_client()

                if (
                    not client
                    or user.client_id != client.id
                ):

                    flash(
                        "You cannot modify this user.",
                        "danger",
                    )

                    return redirect(
                        url_for("users.index")
                    )

                assigned_client_id = client.id

            # --------------------------------------------------
            # UPDATE USER
            # --------------------------------------------------

            UserService.update_user(
                user,
                form,
                client_id=assigned_client_id,
                allow_role_change=True,
            )

            flash_success(
                "User updated successfully."
            )

            return redirect(
                url_for("users.index")
            )

        except ValueError as error:

            db.session.rollback()

            flash(
                str(error),
                "danger",
            )

        except Exception:

            db.session.rollback()

            current_app.logger.exception(
                "USER UPDATE ERROR"
            )

            flash(
                "An unexpected error occurred while updating the user.",
                "danger",
            )

    elif request.method == "POST":

        current_app.logger.warning(
            "USER UPDATE FORM ERRORS: %s",
            form.errors,
        )

    return render_template(
        "admin/users/edit.html",
        form=form,
        user=user,
    )


# ==========================================================
# DELETE USER
# ==========================================================

@users_bp.route(
    "/<int:id>/delete",
    methods=["POST"],
)
@admin_required
def delete(id):

    user = get_managed_user(id)

    if user is None:

        return redirect(
            url_for("users.index")
        )

    # ------------------------------------------------------
    # TENANT CHECK
    # ------------------------------------------------------

    if not can_manage_user(user):

        flash(
            "You cannot delete this user.",
            "danger",
        )

        return redirect(
            url_for("users.index")
        )

    # ------------------------------------------------------
    # SUPER ADMIN PROTECTION
    # ------------------------------------------------------

    if (
        user.is_super_admin
        and not is_super_admin()
    ):

        flash(
            "Only a Super Admin can delete a Super Admin account.",
            "danger",
        )

        return redirect(
            url_for("users.index")
        )

    try:

        UserService.delete_user(user)

        flash_success(
            "User deleted successfully."
        )

    except ValueError as error:

        db.session.rollback()

        flash(
            str(error),
            "danger",
        )

    except Exception:

        db.session.rollback()

        current_app.logger.exception(
            "USER DELETE ERROR"
        )

        flash(
            "An unexpected error occurred while deleting the user.",
            "danger",
        )

    return redirect(
        url_for("users.index")
    )


# ==========================================================
# MY PROFILE
# ==========================================================

@users_bp.route(
    "/profile",
    methods=["GET", "POST"],
)
@login_required
def profile():

    form = EditUserForm()

    configure_form(form)

    # ------------------------------------------------------
    # LOCK ROLE AND ORGANIZATION
    # ------------------------------------------------------

    form.role.data = current_user.role
    form.client_id.data = current_user.client_id

    # ------------------------------------------------------
    # POPULATE FORM ON GET
    # ------------------------------------------------------

    if request.method == "GET":

        form.first_name.data = current_user.first_name
        form.last_name.data = current_user.last_name
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.phone.data = current_user.phone
        form.is_active.data = bool(
            current_user.is_active
        )

    # ------------------------------------------------------
    # FORM SUBMISSION
    # ------------------------------------------------------

    if form.validate_on_submit():

        try:

            # Prevent role or organization changes
            # through the profile form.

            form.role.data = current_user.role
            form.client_id.data = current_user.client_id

            UserService.update_user(
                current_user,
                form,
                client_id=current_user.client_id,
                allow_role_change=False,
            )

            flash_success(
                "Profile updated successfully."
            )

            return redirect(
                url_for("users.profile")
            )

        except ValueError as error:

            db.session.rollback()

            flash(
                str(error),
                "danger",
            )

        except Exception:

            db.session.rollback()

            current_app.logger.exception(
                "PROFILE UPDATE ERROR"
            )

            flash(
                "An unexpected error occurred while updating your profile.",
                "danger",
            )

    elif request.method == "POST":

        current_app.logger.warning(
            "PROFILE FORM ERRORS: %s",
            form.errors,
        )

    return render_template(
        "admin/users/profile.html",
        form=form,
    )


# ==========================================================
# CHANGE PASSWORD
# ==========================================================

@users_bp.route(
    "/change-password",
    methods=["GET", "POST"],
)
@login_required
def change_password():

    form = ChangePasswordForm()

    if form.validate_on_submit():

        # --------------------------------------------------
        # VERIFY CURRENT PASSWORD
        # --------------------------------------------------

        if not current_user.check_password(
            form.current_password.data
        ):

            flash(
                "Current password is incorrect.",
                "danger",
            )

            return render_template(
                "admin/users/change_password.html",
                form=form,
            )

        try:

            UserService.change_password(
                current_user,
                form.password.data,
            )

            flash_success(
                "Password changed successfully."
            )

            return redirect(
                url_for("users.profile")
            )

        except Exception:

            db.session.rollback()

            current_app.logger.exception(
                "PASSWORD CHANGE ERROR"
            )

            flash(
                "An unexpected error occurred while changing your password.",
                "danger",
            )

    elif request.method == "POST":

        current_app.logger.warning(
            "PASSWORD FORM ERRORS: %s",
            form.errors,
        )

    return render_template(
        "admin/users/change_password.html",
        form=form,
    )


# ==========================================================
# USER DETAILS
# ==========================================================

@users_bp.route(
    "/<int:id>"
)
@admin_required
def detail(id):

    user = get_managed_user(id)

    if user is None:

        return redirect(
            url_for("users.index")
        )

    return render_template(
        "admin/users/detail.html",
        user=user,
    )