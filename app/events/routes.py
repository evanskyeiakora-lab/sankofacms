from datetime import datetime

from flask import (
    render_template,
    redirect,
    url_for,
    request,
    flash,
    current_app,
)

from flask_login import login_required

from . import events_bp
from .forms import EventForm

from app.extensions import db
from app.models import Event
from app.tenant import get_current_client

from app.utils.file_upload import (
    replace_image,
    delete_image,
)

from app.utils.permissions import roles_required
from app.utils.constants import EVENTS_FOLDER


# ==========================================================
# ALLOWED ROLES
# ==========================================================

EVENT_ROLES = (
    "Super Admin",
    "Administrator",
    "Editor",
    "Author",
)


# ==========================================================
# CURRENT CLIENT
# ==========================================================

def require_events_client():

    client = get_current_client()

    if not client:

        flash(
            "No active client was found for this domain.",
            "danger",
        )

        return None

    return client


# ==========================================================
# GET EVENT
# TENANT-SAFE
# ==========================================================

def get_event(event_id, client):

    return (
        Event.query
        .filter(
            Event.id == event_id,
            Event.client_id == client.id,
        )
        .first_or_404()
    )


# ==========================================================
# EVENTS LIST
# ==========================================================

@events_bp.route("/")
@login_required
@roles_required(*EVENT_ROLES)
def index():

    client = require_events_client()

    if not client:
        return redirect(url_for("main.home"))

    search = (
        request.args
        .get("search", "")
        .strip()
    )

    page = request.args.get(
        "page",
        1,
        type=int,
    )

    query = (
        Event.query
        .filter(
            Event.client_id == client.id
        )
    )

    # ------------------------------------------------------
    # SEARCH
    # ------------------------------------------------------

    if search:

        query = query.filter(
            Event.title.ilike(
                f"%{search}%"
            )
        )

    # ------------------------------------------------------
    # PAGINATION
    # ------------------------------------------------------

    events = (
        query
        .order_by(
            Event.start_date.asc(),
            Event.start_time.asc(),
            Event.display_order.asc(),
            Event.id.asc(),
        )
        .paginate(
            page=page,
            per_page=10,
            error_out=False,
        )
    )

    return render_template(
        "admin/events/index.html",
        events=events,
        search=search,
    )


# ==========================================================
# CREATE EVENT
# ==========================================================

@events_bp.route(
    "/create",
    methods=["GET", "POST"],
)
@login_required
@roles_required(*EVENT_ROLES)
def create():

    client = require_events_client()

    if not client:
        return redirect(url_for("main.home"))

    form = EventForm()

    if form.validate_on_submit():

        try:

            # --------------------------------------------------
            # CREATE EVENT
            # --------------------------------------------------

            event = Event(
                client_id=client.id,

                title=form.title.data.strip(),

                description=form.description.data,

                venue=(
                    form.venue.data.strip()
                    if form.venue.data
                    else None
                ),

                organizer=(
                    form.organizer.data.strip()
                    if form.organizer.data
                    else None
                ),

                start_date=form.start_date.data,

                end_date=form.end_date.data,

                start_time=form.start_time.data,

                end_time=form.end_time.data,

                registration_link=(
                    form.registration_link.data.strip()
                    if form.registration_link.data
                    else None
                ),

                is_featured=bool(
                    form.is_featured.data
                ),

                is_published=bool(
                    form.is_published.data
                ),

                display_order=(
                    form.display_order.data
                    if form.display_order.data is not None
                    else 0
                ),
            )

            # --------------------------------------------------
            # GENERATE SLUG
            # --------------------------------------------------

            event.generate_slug()

            # --------------------------------------------------
            # PUBLISHED DATE
            # --------------------------------------------------

            if event.is_published:

                event.published_at = datetime.utcnow()

            else:

                event.published_at = None

            # --------------------------------------------------
            # FEATURED IMAGE
            # --------------------------------------------------

            uploaded_image = (
                form.featured_image.data
            )

            if (
                uploaded_image
                and hasattr(
                    uploaded_image,
                    "filename",
                )
                and uploaded_image.filename
            ):

                event.featured_image = replace_image(
                    None,
                    uploaded_image,
                    EVENTS_FOLDER,
                )

            # --------------------------------------------------
            # SAVE
            # --------------------------------------------------

            db.session.add(event)

            db.session.commit()

            flash(
                "Event created successfully.",
                "success",
            )

            return redirect(
                url_for("events.index")
            )

        except Exception as error:

            db.session.rollback()

            current_app.logger.exception(
                "EVENT CREATION ERROR"
            )

            print(
                "\n================================"
            )
            print(
                "EVENT CREATION ERROR"
            )
            print(
                "ERROR TYPE:",
                type(error).__name__,
            )
            print(
                "ERROR:",
                str(error),
            )
            print(
                "================================\n"
            )

            flash(
                "An error occurred while creating the event.",
                "danger",
            )

    elif request.method == "POST":

        current_app.logger.warning(
            "EVENT FORM VALIDATION ERRORS: %s",
            form.errors,
        )

    return render_template(
        "admin/events/create.html",
        form=form,
    )


# ==========================================================
# EDIT EVENT
# ==========================================================

@events_bp.route(
    "/edit/<int:id>",
    methods=["GET", "POST"],
)
@login_required
@roles_required(*EVENT_ROLES)
def edit(id):

    client = require_events_client()

    if not client:
        return redirect(url_for("main.home"))

    event = get_event(
        id,
        client,
    )

    # IMPORTANT:
    # Do NOT use EventForm(obj=event).
    # The existing image filename would be placed
    # inside the FileField as a string.

    form = EventForm()

    # ======================================================
    # GET
    # Populate normal fields manually
    # ======================================================

    if request.method == "GET":

        form.title.data = event.title

        form.description.data = event.description

        form.venue.data = event.venue

        form.organizer.data = event.organizer

        form.start_date.data = event.start_date

        form.end_date.data = event.end_date

        form.start_time.data = event.start_time

        form.end_time.data = event.end_time

        form.registration_link.data = (
            event.registration_link
        )

        form.is_featured.data = bool(
            event.is_featured
        )

        form.is_published.data = bool(
            event.is_published
        )

        form.display_order.data = (
            event.display_order
        )

    # ======================================================
    # POST
    # ======================================================

    if form.validate_on_submit():

        try:

            # --------------------------------------------------
            # BASIC INFORMATION
            # --------------------------------------------------

            event.title = (
                form.title.data.strip()
            )

            event.description = (
                form.description.data
            )

            event.venue = (
                form.venue.data.strip()
                if form.venue.data
                else None
            )

            event.organizer = (
                form.organizer.data.strip()
                if form.organizer.data
                else None
            )

            # --------------------------------------------------
            # DATE
            # --------------------------------------------------

            event.start_date = (
                form.start_date.data
            )

            event.end_date = (
                form.end_date.data
            )

            # --------------------------------------------------
            # TIME
            # --------------------------------------------------

            event.start_time = (
                form.start_time.data
            )

            event.end_time = (
                form.end_time.data
            )

            # --------------------------------------------------
            # REGISTRATION
            # --------------------------------------------------

            event.registration_link = (
                form.registration_link.data.strip()
                if form.registration_link.data
                else None
            )

            # --------------------------------------------------
            # FEATURED
            # --------------------------------------------------

            event.is_featured = bool(
                form.is_featured.data
            )

            # --------------------------------------------------
            # DISPLAY ORDER
            # --------------------------------------------------

            event.display_order = (
                form.display_order.data
                if form.display_order.data is not None
                else 0
            )

            # --------------------------------------------------
            # PUBLICATION STATUS
            # --------------------------------------------------

            new_published_status = bool(
                form.is_published.data
            )

            if (
                new_published_status
                and not event.is_published
            ):

                event.published_at = (
                    datetime.utcnow()
                )

            elif not new_published_status:

                event.published_at = None

            event.is_published = (
                new_published_status
            )

            # --------------------------------------------------
            # REGENERATE SLUG
            # --------------------------------------------------

            event.generate_slug()

            # --------------------------------------------------
            # NEW FEATURED IMAGE
            # --------------------------------------------------

            uploaded_image = (
                form.featured_image.data
            )

            if (
                uploaded_image
                and hasattr(
                    uploaded_image,
                    "filename",
                )
                and uploaded_image.filename
            ):

                event.featured_image = replace_image(
                    event.featured_image,
                    uploaded_image,
                    EVENTS_FOLDER,
                )

            # --------------------------------------------------
            # SAVE
            # --------------------------------------------------

            db.session.commit()

            flash(
                "Event updated successfully.",
                "success",
            )

            return redirect(
                url_for("events.index")
            )

        except Exception as error:

            db.session.rollback()

            current_app.logger.exception(
                "EVENT UPDATE ERROR"
            )

            print(
                "\n================================"
            )
            print(
                "EVENT UPDATE ERROR"
            )
            print(
                "ERROR TYPE:",
                type(error).__name__,
            )
            print(
                "ERROR:",
                str(error),
            )
            print(
                "================================\n"
            )

            flash(
                "An error occurred while updating the event.",
                "danger",
            )

    elif request.method == "POST":

        current_app.logger.warning(
            "EVENT FORM VALIDATION ERRORS: %s",
            form.errors,
        )

    return render_template(
        "admin/events/edit.html",
        form=form,
        event=event,
    )


# ==========================================================
# DELETE EVENT
# ==========================================================

@events_bp.route(
    "/delete/<int:id>",
    methods=["POST"],
)
@login_required
@roles_required(*EVENT_ROLES)
def delete(id):

    client = require_events_client()

    if not client:
        return redirect(url_for("main.home"))

    event = get_event(
        id,
        client,
    )

    try:

        # --------------------------------------------------
        # DELETE FEATURED IMAGE
        # --------------------------------------------------

        if event.featured_image:

            delete_image(
                event.featured_image,
                EVENTS_FOLDER,
            )

        # --------------------------------------------------
        # DELETE DATABASE RECORD
        # --------------------------------------------------

        db.session.delete(event)

        db.session.commit()

        flash(
            "Event deleted successfully.",
            "success",
        )

    except Exception as error:

        db.session.rollback()

        current_app.logger.exception(
            "EVENT DELETE ERROR"
        )

        print(
            "\n================================"
        )
        print(
            "EVENT DELETE ERROR"
        )
        print(
            "ERROR TYPE:",
            type(error).__name__,
        )
        print(
            "ERROR:",
            str(error),
        )
        print(
            "================================\n"
        )

        flash(
            "An error occurred while deleting the event.",
            "danger",
        )

    return redirect(
        url_for("events.index")
    )