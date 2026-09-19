
import os
import uuid

from flask import (
    render_template,
    redirect,
    url_for,
    request,
    current_app,
    flash,
    abort,
)

from flask_login import login_required
from werkzeug.utils import secure_filename

from . import hero_bp
from .forms import HeroForm

from app.extensions import db
from app.models import HeroSlide
from app.tenant import get_current_client
from app.utils.permissions import roles_required


# ==========================================================
# ALLOWED ROLES
# ==========================================================

HERO_ROLES = (
    "Super Admin",
    "Administrator",
    "Editor",
)


# ==========================================================
# UPLOAD CONFIGURATION
# ==========================================================

ALLOWED_EXTENSIONS = {
    "jpg",
    "jpeg",
    "png",
    "webp",
}


def hero_upload_folder():
    """
    Return the folder where hero images are stored.
    """

    folder = os.path.join(
        current_app.static_folder,
        "uploads",
        "hero",
    )

    os.makedirs(folder, exist_ok=True)

    return folder


def allowed_file(filename):
    """
    Check whether the uploaded file has an allowed extension.
    """

    if not filename or "." not in filename:
        return False

    extension = filename.rsplit(".", 1)[1].lower()

    return extension in ALLOWED_EXTENSIONS


def save_hero_image(image_file):
    """
    Save an uploaded hero image and return its filename.
    """

    if not image_file:
        return None

    original_filename = secure_filename(
        image_file.filename or ""
    )

    if not allowed_file(original_filename):
        return None

    extension = original_filename.rsplit(
        ".",
        1
    )[1].lower()

    filename = (
        f"{uuid.uuid4().hex}.{extension}"
    )

    filepath = os.path.join(
        hero_upload_folder(),
        filename,
    )

    image_file.save(filepath)

    return filename


def delete_hero_image(filename):
    """
    Delete an existing hero image if it exists.
    """

    if not filename:
        return

    filepath = os.path.join(
        hero_upload_folder(),
        filename,
    )

    if os.path.isfile(filepath):
        try:
            os.remove(filepath)
        except OSError:
            current_app.logger.exception(
                "Could not delete hero image: %s",
                filepath,
            )


def require_hero_client():
    """
    Return the current tenant/client.

    Super Admin users still need a client context when
    managing tenant-specific hero slides.
    """

    client = get_current_client()

    if not client:
        abort(404, description="Client not found.")

    return client


def get_client_slide(slide_id, client_id):
    """
    Get a hero slide belonging to the current client.
    """

    return (
        HeroSlide.query
        .filter(
            HeroSlide.id == slide_id,
            HeroSlide.client_id == client_id,
        )
        .first_or_404()
    )


# ==========================================================
# HERO SLIDER LIST
# ==========================================================

@hero_bp.route("/")
@login_required
@roles_required(*HERO_ROLES)
def index():

    client = require_hero_client()

    page = request.args.get(
        "page",
        1,
        type=int,
    )

    slides = (
        HeroSlide.query
        .filter(
            HeroSlide.client_id == client.id,
        )
        .order_by(
            HeroSlide.display_order.asc(),
            HeroSlide.created_at.desc(),
            HeroSlide.id.asc(),
        )
        .paginate(
            page=page,
            per_page=10,
            error_out=False,
        )
    )

    return render_template(
        "admin/hero/index.html",
        slides=slides,
    )


# ==========================================================
# CREATE HERO SLIDE
# ==========================================================

@hero_bp.route(
    "/create",
    methods=["GET", "POST"],
)
@login_required
@roles_required(*HERO_ROLES)
def create():

    client = require_hero_client()

    form = HeroForm()

    if form.validate_on_submit():

        image_file = form.image.data

        # --------------------------------------------------
        # IMAGE IS REQUIRED
        # --------------------------------------------------

        if not image_file or not getattr(
            image_file,
            "filename",
            "",
        ):

            form.image.errors.append(
                "Please upload a hero image."
            )

            return render_template(
                "admin/hero/create.html",
                form=form,
            )

        # --------------------------------------------------
        # SAVE IMAGE
        # --------------------------------------------------

        filename = save_hero_image(image_file)

        if not filename:

            form.image.errors.append(
                "Invalid image file."
            )

            return render_template(
                "admin/hero/create.html",
                form=form,
            )

        try:

            # --------------------------------------------------
            # CREATE SLIDE
            # --------------------------------------------------

            slide = HeroSlide(
                client_id=client.id,
                title=form.title.data,
                subtitle=form.subtitle.data,
                image=filename,
                button_text=form.button_text.data,
                button_url=form.button_url.data,
                display_order=(
                    form.display_order.data or 1
                ),
                is_active=bool(
                    form.is_active.data
                ),
            )

            db.session.add(slide)
            db.session.commit()

            flash(
                "Hero slide created successfully.",
                "success",
            )

            return redirect(
                url_for("hero.index")
            )

        except Exception:

            db.session.rollback()

            delete_hero_image(filename)

            current_app.logger.exception(
                "HERO SLIDE CREATION ERROR"
            )

            flash(
                "An error occurred while creating the hero slide.",
                "danger",
            )

    return render_template(
        "admin/hero/create.html",
        form=form,
    )


# ==========================================================
# EDIT HERO SLIDE
# ==========================================================

@hero_bp.route(
    "/edit/<int:id>",
    methods=["GET", "POST"],
)
@login_required
@roles_required(*HERO_ROLES)
def edit(id):

    client = require_hero_client()

    slide = get_client_slide(
        id,
        client.id,
    )

    form = HeroForm()

    if request.method == "GET":

        form.title.data = slide.title
        form.subtitle.data = slide.subtitle
        form.button_text.data = slide.button_text
        form.button_url.data = slide.button_url
        form.display_order.data = slide.display_order
        form.is_active.data = slide.is_active

    if form.validate_on_submit():

        old_image = slide.image
        new_filename = None

        try:

            # --------------------------------------------------
            # CHECK FOR NEW IMAGE
            # --------------------------------------------------

            image_file = form.image.data

            has_new_image = bool(
                image_file
                and getattr(
                    image_file,
                    "filename",
                    "",
                )
            )

            if has_new_image:

                new_filename = save_hero_image(
                    image_file
                )

                if not new_filename:

                    form.image.errors.append(
                        "Invalid image file."
                    )

                    return render_template(
                        "admin/hero/edit.html",
                        form=form,
                        slide=slide,
                    )

                slide.image = new_filename

            # --------------------------------------------------
            # UPDATE SLIDE DETAILS
            # --------------------------------------------------

            slide.title = form.title.data
            slide.subtitle = form.subtitle.data
            slide.button_text = form.button_text.data
            slide.button_url = form.button_url.data

            slide.display_order = (
                form.display_order.data or 1
            )

            slide.is_active = bool(
                form.is_active.data
            )

            db.session.commit()

            # --------------------------------------------------
            # DELETE OLD IMAGE AFTER SUCCESSFUL COMMIT
            # --------------------------------------------------

            if new_filename and old_image != new_filename:
                delete_hero_image(old_image)

            flash(
                "Hero slide updated successfully.",
                "success",
            )

            return redirect(
                url_for("hero.index")
            )

        except Exception:

            db.session.rollback()

            if new_filename:
                delete_hero_image(new_filename)

            current_app.logger.exception(
                "HERO SLIDE UPDATE ERROR"
            )

            flash(
                "An error occurred while updating the hero slide.",
                "danger",
            )

    return render_template(
        "admin/hero/edit.html",
        form=form,
        slide=slide,
    )


# ==========================================================
# DELETE HERO SLIDE
# ==========================================================

@hero_bp.route(
    "/delete/<int:id>",
    methods=["POST"],
)
@login_required
@roles_required(*HERO_ROLES)
def delete(id):

    client = require_hero_client()

    slide = get_client_slide(
        id,
        client.id,
    )

    image_filename = slide.image

    try:

        db.session.delete(slide)
        db.session.commit()

        delete_hero_image(image_filename)

        flash(
            "Hero slide deleted successfully.",
            "success",
        )

    except Exception:

        db.session.rollback()

        current_app.logger.exception(
            "HERO SLIDE DELETE ERROR"
        )

        flash(
            "An error occurred while deleting the hero slide.",
            "danger",
        )

    return redirect(
        url_for("hero.index")
    )