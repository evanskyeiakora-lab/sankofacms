
import os
import re
import uuid

from flask import (
    render_template,
    redirect,
    url_for,
    request,
    flash,
    current_app,
    abort,
)

from flask_login import login_required

from werkzeug.utils import secure_filename

from . import pages_bp
from .forms import PageForm

from app.extensions import db
from app.models import Page
from app.tenant import get_current_client
from app.utils.permissions import roles_required


# ==========================================================
# ALLOWED ROLES
# ==========================================================

PAGE_ROLES = (
    "Super Admin",
    "Administrator",
    "Editor",
)


# ==========================================================
# ALLOWED IMAGE EXTENSIONS
# ==========================================================

ALLOWED_EXTENSIONS = {
    "jpg",
    "jpeg",
    "png",
    "webp",
    "gif",
}


# ==========================================================
# CURRENT CLIENT
# ==========================================================

def require_pages_client():
    """
    Return the active client for the current domain.

    Prevents users from accessing pages belonging
    to another client.
    """

    client = get_current_client()

    if not client:
        abort(404)

    return client


# ==========================================================
# SLUG GENERATOR
# ==========================================================

def generate_slug(title):
    """
    Convert a page title into a URL-friendly slug.
    """

    slug = title.strip().lower()

    slug = re.sub(
        r"[^a-z0-9\s-]",
        "",
        slug,
    )

    slug = re.sub(
        r"[\s_-]+",
        "-",
        slug,
    )

    slug = slug.strip("-")

    return slug or "page"


# ==========================================================
# UNIQUE SLUG
# ==========================================================

def get_unique_slug(title, client_id, page_id=None):
    """
    Generate a unique slug for the current client.
    """

    base_slug = generate_slug(title)
    slug = base_slug
    counter = 2

    while True:

        query = Page.query.filter(
            Page.client_id == client_id,
            Page.slug == slug,
        )

        if page_id is not None:
            query = query.filter(
                Page.id != page_id
            )

        existing_page = query.first()

        if not existing_page:
            return slug

        slug = f"{base_slug}-{counter}"
        counter += 1


# ==========================================================
# IMAGE VALIDATION
# ==========================================================

def allowed_image(filename):
    """
    Check whether the uploaded image extension is allowed.
    """

    if not filename or "." not in filename:
        return False

    extension = filename.rsplit(
        ".",
        1,
    )[1].lower()

    return extension in ALLOWED_EXTENSIONS


# ==========================================================
# SAVE PAGE IMAGE
# ==========================================================

def save_page_image(image_file):
    """
    Save an uploaded page image inside:

    static/uploads/pages/
    """

    if not image_file:
        return None

    original_filename = secure_filename(
        image_file.filename
    )

    if not original_filename:
        return None

    if not allowed_image(original_filename):
        return None

    extension = original_filename.rsplit(
        ".",
        1,
    )[1].lower()

    filename = (
        f"{uuid.uuid4().hex}."
        f"{extension}"
    )

    upload_folder = os.path.join(
        current_app.static_folder,
        "uploads",
        "pages",
    )

    os.makedirs(
        upload_folder,
        exist_ok=True,
    )

    file_path = os.path.join(
        upload_folder,
        filename,
    )

    image_file.save(file_path)

    return filename


# ==========================================================
# DELETE PAGE IMAGE
# ==========================================================

def delete_page_image(filename):
    """
    Delete a page image if it exists.
    """

    if not filename:
        return

    file_path = os.path.join(
        current_app.static_folder,
        "uploads",
        "pages",
        filename,
    )

    if os.path.isfile(file_path):
        try:
            os.remove(file_path)
        except OSError:
            current_app.logger.warning(
                "Unable to delete page image: %s",
                file_path,
            )


# ==========================================================
# PAGE LIST
# ==========================================================

@pages_bp.route("/")
@login_required
@roles_required(*PAGE_ROLES)
def index():

    client = require_pages_client()

    search = request.args.get(
        "search",
        "",
        type=str,
    ).strip()

    page_number = request.args.get(
        "page",
        1,
        type=int,
    )

    query = Page.query.filter(
        Page.client_id == client.id
    )

    if search:

        query = query.filter(
            Page.title.ilike(
                f"%{search}%"
            )
        )

    pages = (
        query
        .order_by(
            Page.created_at.desc(),
            Page.id.desc(),
        )
        .paginate(
            page=page_number,
            per_page=10,
            error_out=False,
        )
    )

    return render_template(
        "admin/pages/index.html",
        pages=pages,
        search=search,
    )


# ==========================================================
# CREATE PAGE
# ==========================================================

@pages_bp.route(
    "/create",
    methods=["GET", "POST"],
)
@login_required
@roles_required(*PAGE_ROLES)
def create():

    client = require_pages_client()

    form = PageForm()

    if form.validate_on_submit():

        try:

            title = form.title.data.strip()

            slug = get_unique_slug(
                title=title,
                client_id=client.id,
            )

            featured_image = None

            if getattr(
                form,
                "featured_image",
                None,
            ) and form.featured_image.data:

                image_file = form.featured_image.data

                if not allowed_image(
                    image_file.filename
                ):

                    flash(
                        "Invalid image format.",
                        "danger",
                    )

                    return render_template(
                        "admin/pages/create.html",
                        form=form,
                    )

                featured_image = save_page_image(
                    image_file
                )

            page = Page(
                client_id=client.id,
                title=title,
                slug=slug,
                page_role=(
                    form.page_role.data
                    if hasattr(form, "page_role")
                    else None
                ),
                content=(
                    form.content.data
                    if hasattr(form, "content")
                    else None
                ),
                featured_image=featured_image,
                meta_title=(
                    form.meta_title.data
                    if hasattr(form, "meta_title")
                    else None
                ),
                meta_description=(
                    form.meta_description.data
                    if hasattr(form, "meta_description")
                    else None
                ),
                is_published=(
                    bool(form.is_published.data)
                    if hasattr(form, "is_published")
                    else False
                ),
            )

            db.session.add(page)
            db.session.commit()

            flash(
                "Page created successfully.",
                "success",
            )

            return redirect(
                url_for("pages.index")
            )

        except Exception:

            db.session.rollback()

            current_app.logger.exception(
                "PAGE CREATION ERROR"
            )

            flash(
                "An error occurred while creating the page.",
                "danger",
            )

    return render_template(
        "admin/pages/create.html",
        form=form,
    )


# ==========================================================
# EDIT PAGE
# ==========================================================

@pages_bp.route(
    "/edit/<int:id>",
    methods=["GET", "POST"],
)
@login_required
@roles_required(*PAGE_ROLES)
def edit(id):

    client = require_pages_client()

    page = Page.query.filter(
        Page.id == id,
        Page.client_id == client.id,
    ).first_or_404()

    form = PageForm(obj=page)

    if form.validate_on_submit():

        old_image = page.featured_image

        try:

            title = form.title.data.strip()

            page.title = title

            page.slug = get_unique_slug(
                title=title,
                client_id=client.id,
                page_id=page.id,
            )

            if hasattr(form, "page_role"):
                page.page_role = form.page_role.data

            if hasattr(form, "content"):
                page.content = form.content.data

            if hasattr(form, "meta_title"):
                page.meta_title = form.meta_title.data

            if hasattr(form, "meta_description"):
                page.meta_description = (
                    form.meta_description.data
                )

            if hasattr(form, "is_published"):
                page.is_published = bool(
                    form.is_published.data
                )

            if getattr(
                form,
                "featured_image",
                None,
            ) and form.featured_image.data:

                image_file = form.featured_image.data

                if not allowed_image(
                    image_file.filename
                ):

                    flash(
                        "Invalid image format.",
                        "danger",
                    )

                    return render_template(
                        "admin/pages/edit.html",
                        form=form,
                        page=page,
                    )

                new_image = save_page_image(
                    image_file
                )

                if new_image:

                    page.featured_image = new_image

            db.session.commit()

            if (
                old_image
                and page.featured_image != old_image
            ):

                delete_page_image(old_image)

            flash(
                "Page updated successfully.",
                "success",
            )

            return redirect(
                url_for("pages.index")
            )

        except Exception:

            db.session.rollback()

            current_app.logger.exception(
                "PAGE UPDATE ERROR"
            )

            flash(
                "An error occurred while updating the page.",
                "danger",
            )

    return render_template(
        "admin/pages/edit.html",
        form=form,
        page=page,
    )


# ==========================================================
# DELETE PAGE
# ==========================================================

@pages_bp.route(
    "/delete/<int:id>",
    methods=["POST"],
)
@login_required
@roles_required(*PAGE_ROLES)
def delete(id):

    client = require_pages_client()

    page = Page.query.filter(
        Page.id == id,
        Page.client_id == client.id,
    ).first_or_404()

    image_filename = page.featured_image

    try:

        db.session.delete(page)
        db.session.commit()

        if image_filename:
            delete_page_image(
                image_filename
            )

        flash(
            "Page deleted successfully.",
            "success",
        )

    except Exception:

        db.session.rollback()

        current_app.logger.exception(
            "PAGE DELETION ERROR"
        )

        flash(
            "An error occurred while deleting the page.",
            "danger",
        )

    return redirect(
        url_for("pages.index")
    )


# ==========================================================
# VIEW PAGE
# ==========================================================

@pages_bp.route(
    "/view/<int:id>",
)
@login_required
@roles_required(*PAGE_ROLES)
def view(id):

    client = require_pages_client()

    page = Page.query.filter(
        Page.id == id,
        Page.client_id == client.id,
    ).first_or_404()

    return render_template(
        "admin/pages/view.html",
        page=page,
    )