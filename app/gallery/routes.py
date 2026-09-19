from datetime import datetime, timezone

from flask import (
    render_template,
    redirect,
    url_for,
    flash,
    request,
    current_app,
)

from flask_login import login_required

from . import gallery_bp
from .forms import GalleryForm

from app.extensions import db
from app.models import Gallery
from app.tenant import get_current_client

from app.utils.file_upload import (
    replace_image,
    delete_image,
)

from app.utils.permissions import roles_required
from app.utils.constants import GALLERY_FOLDER


# ==========================================================
# ALLOWED ROLES
# ==========================================================

GALLERY_ROLES = (
    "Super Admin",
    "Administrator",
    "Editor",
    "Author",
)


# ==========================================================
# CURRENT CLIENT
# ==========================================================

def require_gallery_client():

    client = get_current_client()

    if not client:

        flash(
            "No active client was found for this domain.",
            "danger",
        )

        return None

    return client


# ==========================================================
# GET GALLERY ITEM
# TENANT-SAFE
# ==========================================================

def get_gallery_item(gallery_id, client):

    return (
        Gallery.query
        .filter(
            Gallery.id == gallery_id,
            Gallery.client_id == client.id,
        )
        .first_or_404()
    )


# ==========================================================
# GALLERY LIST
# ==========================================================

@gallery_bp.route("/")
@login_required
@roles_required(*GALLERY_ROLES)
def index():

    client = require_gallery_client()

    if not client:
        return redirect(url_for("main.home"))

    # ------------------------------------------------------
    # SEARCH
    # ------------------------------------------------------

    search = (
        request.args
        .get("search", "")
        .strip()
    )

    # ------------------------------------------------------
    # CATEGORY
    # ------------------------------------------------------

    category = (
        request.args
        .get("category", "")
        .strip()
    )

    # ------------------------------------------------------
    # PAGE
    # ------------------------------------------------------

    page = request.args.get(
        "page",
        1,
        type=int,
    )

    # ------------------------------------------------------
    # BASE QUERY
    # ------------------------------------------------------

    query = (
        Gallery.query
        .filter(
            Gallery.client_id == client.id
        )
    )

    # ------------------------------------------------------
    # SEARCH
    # ------------------------------------------------------

    if search:

        query = query.filter(
            Gallery.title.ilike(
                f"%{search}%"
            )
        )

    # ------------------------------------------------------
    # CATEGORY FILTER
    # ------------------------------------------------------

    if category:

        query = query.filter(
            Gallery.category == category
        )

    # ------------------------------------------------------
    # PAGINATION
    # ------------------------------------------------------

    galleries = (
        query
        .order_by(
            Gallery.display_order.asc(),
            Gallery.created_at.desc(),
            Gallery.id.desc(),
        )
        .paginate(
            page=page,
            per_page=12,
            error_out=False,
        )
    )

    # ------------------------------------------------------
    # AVAILABLE CATEGORIES
    # ------------------------------------------------------

    categories = [
        "General",
        "Church Service",
        "Conference",
        "Youth Ministry",
        "Women's Ministry",
        "Men's Ministry",
        "Children",
        "Outreach",
        "Community",
    ]

    # ------------------------------------------------------
    # RENDER
    # ------------------------------------------------------

    return render_template(
        "admin/gallery/index.html",
        galleries=galleries,
        search=search,
        category=category,
        categories=categories,
    )


# ==========================================================
# CREATE GALLERY ITEM
# ==========================================================

@gallery_bp.route(
    "/create",
    methods=["GET", "POST"],
)
@login_required
@roles_required(*GALLERY_ROLES)
def create():

    client = require_gallery_client()

    if not client:
        return redirect(url_for("main.home"))

    form = GalleryForm()

    # ======================================================
    # FORM SUBMISSION
    # ======================================================

    if form.validate_on_submit():

        # --------------------------------------------------
        # IMAGE REQUIRED
        # --------------------------------------------------

        image_file = form.image.data

        if (
            not image_file
            or not getattr(
                image_file,
                "filename",
                "",
            )
        ):

            flash(
                "Please select a gallery image.",
                "danger",
            )

            return render_template(
                "admin/gallery/create.html",
                form=form,
            )

        uploaded_filename = None

        try:

            # --------------------------------------------------
            # SAVE IMAGE
            # --------------------------------------------------

            uploaded_filename = replace_image(
                None,
                image_file,
                GALLERY_FOLDER,
            )

            # --------------------------------------------------
            # CREATE DATABASE OBJECT
            # --------------------------------------------------

            gallery = Gallery(
                client_id=client.id,

                title=form.title.data.strip(),

                description=(
                    form.description.data.strip()
                    if form.description.data
                    else None
                ),

                category=form.category.data,

                display_order=(
                    form.display_order.data
                    if form.display_order.data is not None
                    else 0
                ),

                is_featured=bool(
                    form.is_featured.data
                ),

                is_published=bool(
                    form.is_published.data
                ),

                image=uploaded_filename,
            )

            # --------------------------------------------------
            # SLUG
            # --------------------------------------------------

            gallery.generate_slug()

            # --------------------------------------------------
            # PUBLISHED DATE
            # --------------------------------------------------

            if gallery.is_published:

                gallery.published_at = (
                    datetime.now(timezone.utc)
                )

            else:

                gallery.published_at = None

            # --------------------------------------------------
            # SAVE DATABASE
            # --------------------------------------------------

            db.session.add(gallery)

            db.session.commit()

            flash(
                "Gallery image created successfully.",
                "success",
            )

            return redirect(
                url_for("gallery.index")
            )

        except Exception as error:

            db.session.rollback()

            # --------------------------------------------------
            # CLEAN UP IMAGE IF DATABASE SAVE FAILED
            # --------------------------------------------------

            if uploaded_filename:

                try:

                    delete_image(
                        uploaded_filename,
                        GALLERY_FOLDER,
                    )

                except Exception as cleanup_error:

                    current_app.logger.exception(
                        "GALLERY IMAGE CLEANUP ERROR: %s",
                        cleanup_error,
                    )

            # --------------------------------------------------
            # LOG ERROR
            # --------------------------------------------------

            current_app.logger.exception(
                "GALLERY CREATION ERROR"
            )

            print(
                "\n================================"
            )
            print(
                "GALLERY CREATION ERROR"
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
                "An error occurred while creating the gallery image.",
                "danger",
            )

    elif request.method == "POST":

        current_app.logger.warning(
            "GALLERY FORM VALIDATION ERRORS: %s",
            form.errors,
        )

    # ======================================================
    # RENDER
    # ======================================================

    return render_template(
        "admin/gallery/create.html",
        form=form,
    )


# ==========================================================
# EDIT GALLERY ITEM
# ==========================================================

@gallery_bp.route(
    "/edit/<int:id>",
    methods=["GET", "POST"],
)
@login_required
@roles_required(*GALLERY_ROLES)
def edit(id):

    client = require_gallery_client()

    if not client:
        return redirect(url_for("main.home"))

    gallery = get_gallery_item(
        id,
        client,
    )

    # IMPORTANT:
    # Do not use GalleryForm(obj=gallery).
    # The existing image filename must not be placed
    # into the FileField.

    form = GalleryForm()

    # ======================================================
    # GET
    # ======================================================

    if request.method == "GET":

        form.title.data = gallery.title

        form.description.data = gallery.description

        form.category.data = gallery.category

        form.display_order.data = (
            gallery.display_order
        )

        form.is_featured.data = bool(
            gallery.is_featured
        )

        form.is_published.data = bool(
            gallery.is_published
        )

    # ======================================================
    # POST
    # ======================================================

    if form.validate_on_submit():

        old_image = gallery.image

        new_image = None

        try:

            # --------------------------------------------------
            # BASIC INFORMATION
            # --------------------------------------------------

            gallery.title = (
                form.title.data.strip()
            )

            gallery.description = (
                form.description.data.strip()
                if form.description.data
                else None
            )

            gallery.category = (
                form.category.data
            )

            gallery.display_order = (
                form.display_order.data
                if form.display_order.data is not None
                else 0
            )

            gallery.is_featured = bool(
                form.is_featured.data
            )

            # --------------------------------------------------
            # PUBLICATION STATUS
            # --------------------------------------------------

            new_published_status = bool(
                form.is_published.data
            )

            if (
                new_published_status
                and not gallery.is_published
            ):

                gallery.published_at = (
                    datetime.now(timezone.utc)
                )

            elif not new_published_status:

                gallery.published_at = None

            gallery.is_published = (
                new_published_status
            )

            # --------------------------------------------------
            # SLUG
            # --------------------------------------------------

            gallery.generate_slug()

            # --------------------------------------------------
            # NEW IMAGE
            # --------------------------------------------------

            image_file = form.image.data

            if (
                image_file
                and getattr(
                    image_file,
                    "filename",
                    "",
                )
            ):

                new_image = replace_image(
                    old_image,
                    image_file,
                    GALLERY_FOLDER,
                )

                gallery.image = new_image

            # --------------------------------------------------
            # SAVE
            # --------------------------------------------------

            db.session.commit()

            flash(
                "Gallery image updated successfully.",
                "success",
            )

            return redirect(
                url_for("gallery.index")
            )

        except Exception as error:

            db.session.rollback()

            current_app.logger.exception(
                "GALLERY UPDATE ERROR"
            )

            print(
                "\n================================"
            )
            print(
                "GALLERY UPDATE ERROR"
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
                "An error occurred while updating the gallery image.",
                "danger",
            )

    elif request.method == "POST":

        current_app.logger.warning(
            "GALLERY FORM VALIDATION ERRORS: %s",
            form.errors,
        )

    # ======================================================
    # RENDER
    # ======================================================

    return render_template(
        "admin/gallery/edit.html",
        form=form,
        gallery=gallery,
    )


# ==========================================================
# DELETE GALLERY ITEM
# ==========================================================

@gallery_bp.route(
    "/delete/<int:id>",
    methods=["POST"],
)
@login_required
@roles_required(*GALLERY_ROLES)
def delete(id):

    client = require_gallery_client()

    if not client:
        return redirect(url_for("main.home"))

    gallery = get_gallery_item(
        id,
        client,
    )

    try:

        # --------------------------------------------------
        # SAVE IMAGE NAME BEFORE DELETE
        # --------------------------------------------------

        image_filename = gallery.image

        # --------------------------------------------------
        # DELETE DATABASE RECORD
        # --------------------------------------------------

        db.session.delete(gallery)

        db.session.commit()

        # --------------------------------------------------
        # DELETE IMAGE
        # --------------------------------------------------

        if image_filename:

            try:

                delete_image(
                    image_filename,
                    GALLERY_FOLDER,
                )

            except Exception as image_error:

                current_app.logger.exception(
                    "GALLERY IMAGE DELETE ERROR: %s",
                    image_error,
                )

        flash(
            "Gallery image deleted successfully.",
            "success",
        )

    except Exception as error:

        db.session.rollback()

        current_app.logger.exception(
            "GALLERY DELETE ERROR"
        )

        print(
            "\n================================"
        )
        print(
            "GALLERY DELETE ERROR"
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
            "An error occurred while deleting the gallery image.",
            "danger",
        )

    return redirect(
        url_for("gallery.index")
    )