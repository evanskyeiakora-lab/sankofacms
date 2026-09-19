from datetime import datetime

from app.extensions import db


class Page(db.Model):
    __tablename__ = "pages"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    # ======================================================
    # CLIENT / TENANT
    # ======================================================

    client_id = db.Column(
        db.Integer,
        db.ForeignKey("clients.id"),
        nullable=True,
        index=True
    )

    # ======================================================
    # PAGE INFORMATION
    # ======================================================

    title = db.Column(
        db.String(200),
        nullable=False
    )

    slug = db.Column(
        db.String(200),
        unique=True,
        nullable=False,
        index=True
    )

    page_role = db.Column(
        db.String(50),
        default="normal",
        nullable=False,
        index=True
    )

    content = db.Column(
        db.Text,
        nullable=False
    )

    featured_image = db.Column(
        db.String(255)
    )

    # ======================================================
    # SEO
    # ======================================================

    meta_title = db.Column(
        db.String(255)
    )

    meta_description = db.Column(
        db.Text
    )

    # ======================================================
    # PUBLISHING
    # ======================================================

    is_published = db.Column(
        db.Boolean,
        default=True
    )

    # ======================================================
    # TIMESTAMPS
    # ======================================================

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    # ======================================================
    # REPRESENTATION
    # ======================================================

    def __repr__(self):
        return f"<Page {self.title}>"