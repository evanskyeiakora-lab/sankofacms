from datetime import datetime, timezone

from slugify import slugify

from app.extensions import db
from app.models.mixins import (
    TimestampMixin,
    PublishMixin
)


class News(
    TimestampMixin,
    PublishMixin,
    db.Model
):

    __tablename__ = "news"

    # ==========================================================
    # PRIMARY KEY
    # ==========================================================

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    # ==========================================================
    # CLIENT / TENANT
    # ==========================================================

    client_id = db.Column(
        db.Integer,
        db.ForeignKey("clients.id"),
        nullable=True,
        index=True
    )

    # ==========================================================
    # TITLE
    # ==========================================================

    title = db.Column(
        db.String(255),
        nullable=False
    )

    # ==========================================================
    # SLUG
    # ==========================================================

    slug = db.Column(
        db.String(255),
        nullable=False,
        index=True
    )

    # ==========================================================
    # CONTENT
    # ==========================================================

    content = db.Column(
        db.Text,
        nullable=False
    )

    # ==========================================================
    # FEATURED IMAGE
    # ==========================================================

    featured_image = db.Column(
        db.String(255),
        nullable=True
    )

    # ==========================================================
    # GENERATE UNIQUE SLUG
    # ==========================================================

    def generate_slug(self):

        base_slug = slugify(
            self.title
        )

        slug = base_slug
        counter = 1

        while True:

            query = News.query.filter(
                News.slug == slug,
                News.client_id == self.client_id
            )

            # ----------------------------------------------
            # Ignore the current article when editing
            # ----------------------------------------------

            if self.id is not None:

                query = query.filter(
                    News.id != self.id
                )

            existing = query.first()

            if existing is None:
                break

            slug = (
                f"{base_slug}-{counter}"
            )

            counter += 1

        self.slug = slug

    # ==========================================================
    # PUBLISH
    # ==========================================================

    def publish(self):

        self.is_published = True

        if not self.published_at:

            self.published_at = (
                datetime.now(timezone.utc)
            )

    # ==========================================================
    # UNPUBLISH
    # ==========================================================

    def unpublish(self):

        self.is_published = False

        self.published_at = None

    # ==========================================================
    # REPRESENTATION
    # ==========================================================

    def __repr__(self):

        return (
            f"<News {self.title}>"
        )