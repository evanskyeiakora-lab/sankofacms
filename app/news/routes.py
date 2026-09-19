from datetime import datetime
import os
import uuid

from flask import (
    render_template,
    redirect,
    url_for,
    flash,
    request,
    current_app,
)

from flask_login import login_required

from werkzeug.utils import secure_filename

from app.extensions import db
from app.models import News
from app.tenant import get_current_client
from app.utils.permissions import roles_required

from . import news_bp

# ==========================================================
# ALLOWED ROLES
# ==========================================================

NEWS_ROLES = [
    "Super Admin",
    "Administrator",
    "Editor",
]


# ==========================================================
# CLIENT HELPER
# ==========================================================

def require_news_client():
    client = get_current_client()

    if not client:
        flash(
            "No active client was found for this domain.",
            "danger"
        )
        return None

    return client


# ==========================================================
# NEWS HELPER
# ==========================================================

def get_news_article(article_id, client):
    return (
        News.query
        .filter(
            News.id == article_id,
            News.client_id == client.id
        )
        .first_or_404()
    )


# ==========================================================
# UPLOAD HELPER
# ==========================================================

def save_featured_image(file):
    """
    Save uploaded news image and return filename.
    """

    if not file or not file.filename:
        return None

    filename = secure_filename(file.filename)

    if not filename:
        return None

    extension = os.path.splitext(filename)[1].lower()

    allowed_extensions = {
        ".jpg",
        ".jpeg",
        ".png",
        ".webp",
    }

    if extension not in allowed_extensions:
        raise ValueError(
            "Only JPG, JPEG, PNG and WEBP images are allowed."
        )

    unique_name = (
        f"{uuid.uuid4().hex}{extension}"
    )

    upload_folder = os.path.join(
        current_app.root_path,
        "static",
        "uploads",
        "news"
    )

    os.makedirs(
        upload_folder,
        exist_ok=True
    )

    file.save(
        os.path.join(
            upload_folder,
            unique_name
        )
    )

    return unique_name


# ==========================================================
# NEWS LIST
# ==========================================================

@news_bp.route("/")
@login_required
@roles_required(*NEWS_ROLES)
def index():

    client = require_news_client()

    if not client:
        return redirect(url_for("main.home"))

    page = request.args.get(
        "page",
        1,
        type=int
    )

    search = request.args.get(
        "search",
        "",
        type=str
    ).strip()

    query = (
        News.query
        .filter(
            News.client_id == client.id
        )
    )

    if search:
        query = query.filter(
            News.title.ilike(
                f"%{search}%"
            )
        )

    articles = (
        query
        .order_by(
            News.created_at.desc()
        )
        .paginate(
            page=page,
            per_page=10,
            error_out=False
        )
    )

    return render_template(
        "admin/news/index.html",
        news=articles,
        articles=articles,
        search=search
    )


# ==========================================================
# CREATE NEWS
# ==========================================================

@news_bp.route("/create", methods=["GET", "POST"])
@login_required
@roles_required(*NEWS_ROLES)
def create():

    client = require_news_client()

    if not client:
        return redirect(url_for("main.home"))

    from app.news.forms import NewsForm

    form = NewsForm()

    if form.validate_on_submit():

        try:

            # ----------------------------------------------
            # IMAGE
            # ----------------------------------------------

            image_filename = None

            if form.featured_image.data:
                image_filename = save_featured_image(
                    form.featured_image.data
                )

            # ----------------------------------------------
            # PUBLICATION STATUS
            # ----------------------------------------------

            is_published = bool(
                form.is_published.data
            )

            published_at = (
                datetime.utcnow()
                if is_published
                else None
            )

            # ----------------------------------------------
            # CREATE ARTICLE
            # ----------------------------------------------

            article = News(
                client_id=client.id,
                title=form.title.data.strip(),
                content=form.content.data,
                featured_image=image_filename,
                is_published=is_published,
                published_at=published_at,
            )

            # ----------------------------------------------
            # SLUG
            # ----------------------------------------------

            if hasattr(article, "generate_slug"):
                article.generate_slug()

            db.session.add(article)
            db.session.commit()

            flash(
                "News article created successfully.",
                "success"
            )

            return redirect(
                url_for("news.index")
            )

        except Exception as e:

            db.session.rollback()

            current_app.logger.exception(
                "NEWS CREATION ERROR"
            )

            print(
                "\n=============================="
            )
            print(
                "NEWS CREATION ERROR"
            )
            print(
                "ERROR TYPE:",
                type(e).__name__
            )
            print(
                "ERROR:",
                str(e)
            )
            print(
                "==============================\n"
            )

            flash(
                "An error occurred while creating the news article.",
                "danger"
            )

    return render_template(
        "admin/news/create.html",
        form=form
    )


# ==========================================================
# EDIT NEWS
# ==========================================================

@news_bp.route(
    "/edit/<int:article_id>",
    methods=["GET", "POST"]
)
@login_required
@roles_required(*NEWS_ROLES)
def edit(article_id):

    client = require_news_client()

    if not client:
        return redirect(url_for("main.home"))

    article = get_news_article(
        article_id,
        client
    )

    from app.news.forms import NewsForm

    form = NewsForm(
        obj=article
    )

    if request.method == "GET":

        form.title.data = article.title
        form.content.data = article.content

        form.is_published.data = bool(
            article.is_published
        )

    if form.validate_on_submit():

        try:

            # ----------------------------------------------
            # UPDATE BASIC INFORMATION
            # ----------------------------------------------

            article.title = form.title.data.strip()
            article.content = form.content.data

            # ----------------------------------------------
            # PUBLICATION STATUS
            # ----------------------------------------------

            new_status = bool(
                form.is_published.data
            )

            if new_status and not article.is_published:

                article.published_at = datetime.utcnow()

            elif not new_status:

                article.published_at = None

            article.is_published = new_status

            # ----------------------------------------------
            # IMAGE
            # ----------------------------------------------

            if form.featured_image.data:

                new_image = save_featured_image(
                    form.featured_image.data
                )

                if new_image:

                    old_image = article.featured_image

                    article.featured_image = new_image

                    # Delete old image if it exists
                    if old_image:

                        old_path = os.path.join(
                            current_app.root_path,
                            "static",
                            "uploads",
                            "news",
                            old_image
                        )

                        if os.path.exists(old_path):

                            try:
                                os.remove(old_path)
                            except OSError:
                                pass

            # ----------------------------------------------
            # SLUG
            # ----------------------------------------------

            if hasattr(article, "generate_slug"):
                article.generate_slug()

            article.updated_at = datetime.utcnow()

            db.session.commit()

            flash(
                "News article updated successfully.",
                "success"
            )

            return redirect(
                url_for("news.index")
            )

        except Exception as e:

            db.session.rollback()

            current_app.logger.exception(
                "NEWS UPDATE ERROR"
            )

            print(
                "\n=============================="
            )
            print(
                "NEWS UPDATE ERROR"
            )
            print(
                "ERROR TYPE:",
                type(e).__name__
            )
            print(
                "ERROR:",
                str(e)
            )
            print(
                "==============================\n"
            )

            flash(
                "An error occurred while updating the news article.",
                "danger"
            )

    return render_template(
        "admin/news/edit.html",
        form=form,
        article=article
    )


# ==========================================================
# DELETE NEWS
# ==========================================================

@news_bp.route(
    "/delete/<int:article_id>",
    methods=["POST"]
)
@login_required
@roles_required(*NEWS_ROLES)
def delete(article_id):

    client = require_news_client()

    if not client:
        return redirect(url_for("main.home"))

    article = get_news_article(
        article_id,
        client
    )

    try:

        # ----------------------------------------------
        # DELETE IMAGE
        # ----------------------------------------------

        if article.featured_image:

            image_path = os.path.join(
                current_app.root_path,
                "static",
                "uploads",
                "news",
                article.featured_image
            )

            if os.path.exists(image_path):

                try:
                    os.remove(image_path)
                except OSError:
                    pass

        # ----------------------------------------------
        # DELETE ARTICLE
        # ----------------------------------------------

        db.session.delete(article)
        db.session.commit()

        flash(
            "News article deleted successfully.",
            "success"
        )

    except Exception as e:

        db.session.rollback()

        current_app.logger.exception(
            "NEWS DELETE ERROR"
        )

        print(
            "\n=============================="
        )
        print(
            "NEWS DELETE ERROR"
        )
        print(
            "ERROR TYPE:",
            type(e).__name__
        )
        print(
            "ERROR:",
            str(e)
        )
        print(
            "==============================\n"
        )

        flash(
            "An error occurred while deleting the news article.",
            "danger"
        )

    return redirect(
        url_for("news.index")
    )