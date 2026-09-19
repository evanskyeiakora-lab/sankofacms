
from flask import (
    render_template,
    request,
    redirect,
    url_for,
    flash,
    abort,
    current_app,
)

from flask_login import login_required

from sqlalchemy import or_

from . import contact_bp
from .forms import ContactForm

from app.extensions import db
from app.models import ContactMessage

from app.tenant import get_current_client

from app.utils.permissions import roles_required


# ==========================================================
# CONSTANTS
# ==========================================================

CONTACT_ROLES = (
    "Super Admin",
    "Administrator",
    "Moderator",
)


# ==========================================================
# TENANT HELPER
# ==========================================================

def get_required_client():
    """
    Get the organization associated with the current domain.
    """

    client = get_current_client()

    if not client:

        abort(
            404,
            description="Organization not found.",
        )

    return client


# ==========================================================
# PUBLIC CONTACT FORM
# ==========================================================

@contact_bp.route(
    "/contact/",
    methods=["GET", "POST"],
)
def contact():

    client = get_required_client()

    form = ContactForm()

    if form.validate_on_submit():

        message = ContactMessage(
            client_id=client.id,

            name=form.name.data.strip(),

            email=form.email.data.strip(),

            phone=(
                form.phone.data.strip()
                if form.phone.data
                else None
            ),

            subject=form.subject.data.strip(),

            message=form.message.data.strip(),

            ip_address=request.remote_addr,

            user_agent=request.user_agent.string,

            is_read=False,
        )

        try:

            db.session.add(message)

            db.session.commit()

            flash(
                "Thank you for contacting us. "
                "We have received your message.",
                "success",
            )

            return redirect(
                url_for("contact.contact")
            )

        except Exception:

            db.session.rollback()

            current_app.logger.exception(
                "CONTACT MESSAGE CREATION ERROR"
            )

            flash(
                "Sorry, your message could not be sent. "
                "Please try again.",
                "danger",
            )

    return render_template(
        "contact/index.html",
        form=form,
    )


# ==========================================================
# ADMIN CONTACT INBOX
# ==========================================================

@contact_bp.route(
    "/admin/contact/",
)
@roles_required(*CONTACT_ROLES)
def admin_index():

    client = get_required_client()

    search = request.args.get(
        "search",
        "",
        type=str,
    ).strip()

    page = request.args.get(
        "page",
        1,
        type=int,
    )

    # ------------------------------------------------------
    # TENANT-SCOPED QUERY
    # ------------------------------------------------------

    query = (
        ContactMessage.query
        .filter(
            ContactMessage.client_id == client.id
        )
    )

    # ------------------------------------------------------
    # SEARCH
    # ------------------------------------------------------

    if search:

        search_term = f"%{search}%"

        query = query.filter(
            or_(
                ContactMessage.name.ilike(search_term),

                ContactMessage.email.ilike(search_term),

                ContactMessage.subject.ilike(search_term),

                ContactMessage.phone.ilike(search_term),
            )
        )

    # ------------------------------------------------------
    # PAGINATION
    # ------------------------------------------------------

    messages = (
        query
        .order_by(
            ContactMessage.is_read.asc(),

            ContactMessage.created_at.desc(),
        )
        .paginate(
            page=page,
            per_page=20,
            error_out=False,
        )
    )

    # ------------------------------------------------------
    # COUNTERS
    # ------------------------------------------------------

    total_messages = (
        ContactMessage.query
        .filter(
            ContactMessage.client_id == client.id
        )
        .count()
    )

    unread_messages = (
        ContactMessage.query
        .filter(
            ContactMessage.client_id == client.id,

            ContactMessage.is_read.is_(False),
        )
        .count()
    )

    return render_template(
        "admin/contact/index.html",

        messages=messages,

        search=search,

        total_messages=total_messages,

        unread_messages=unread_messages,
    )


# ==========================================================
# VIEW MESSAGE
# ==========================================================

@contact_bp.route(
    "/admin/contact/<int:id>",
)
@roles_required(*CONTACT_ROLES)
def detail(id):

    client = get_required_client()

    # ------------------------------------------------------
    # TENANT-SCOPED MESSAGE LOOKUP
    # ------------------------------------------------------

    message = (
        ContactMessage.query
        .filter(
            ContactMessage.id == id,

            ContactMessage.client_id == client.id,
        )
        .first_or_404()
    )

    # ------------------------------------------------------
    # MARK AS READ
    # ------------------------------------------------------

    if not message.is_read:

        message.is_read = True

        db.session.commit()

    return render_template(
        "admin/contact/detail.html",

        message=message,
    )


# ==========================================================
# MARK MESSAGE AS READ
# ==========================================================

@contact_bp.route(
    "/admin/contact/<int:id>/read",
    methods=["POST"],
)
@roles_required(*CONTACT_ROLES)
def mark_read(id):

    client = get_required_client()

    message = (
        ContactMessage.query
        .filter(
            ContactMessage.id == id,

            ContactMessage.client_id == client.id,
        )
        .first_or_404()
    )

    message.is_read = True

    db.session.commit()

    flash(
        "Message marked as read.",
        "success",
    )

    return redirect(
        request.referrer
        or url_for("contact.admin_index")
    )


# ==========================================================
# MARK MESSAGE AS UNREAD
# ==========================================================

@contact_bp.route(
    "/admin/contact/<int:id>/unread",
    methods=["POST"],
)
@roles_required(*CONTACT_ROLES)
def mark_unread(id):

    client = get_required_client()

    message = (
        ContactMessage.query
        .filter(
            ContactMessage.id == id,

            ContactMessage.client_id == client.id,
        )
        .first_or_404()
    )

    message.is_read = False

    db.session.commit()

    flash(
        "Message marked as unread.",
        "success",
    )

    return redirect(
        request.referrer
        or url_for("contact.admin_index")
    )


# ==========================================================
# DELETE MESSAGE
# ==========================================================

@contact_bp.route(
    "/admin/contact/<int:id>/delete",
    methods=["POST"],
)
@roles_required(*CONTACT_ROLES)
def remove(id):

    client = get_required_client()

    # ------------------------------------------------------
    # TENANT-SCOPED LOOKUP
    # ------------------------------------------------------

    message = (
        ContactMessage.query
        .filter(
            ContactMessage.id == id,

            ContactMessage.client_id == client.id,
        )
        .first_or_404()
    )

    try:

        db.session.delete(message)

        db.session.commit()

        flash(
            "Message deleted successfully.",
            "success",
        )

    except Exception:

        db.session.rollback()

        current_app.logger.exception(
            "CONTACT MESSAGE DELETE ERROR"
        )

        flash(
            "Unable to delete message.",
            "danger",
        )

    return redirect(
        url_for("contact.admin_index")
    )
