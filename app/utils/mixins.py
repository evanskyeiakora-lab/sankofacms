from datetime import datetime

from app.extensions import db


class TimestampMixin:
    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )


class PublishMixin:
    status = db.Column(
        db.String(20),
        default="draft"
    )

    published_at = db.Column(
        db.DateTime,
        nullable=True
    )


class SEOFieldsMixin:
    meta_title = db.Column(
        db.String(255)
    )

    meta_description = db.Column(
        db.Text
    )

    meta_keywords = db.Column(
        db.Text
    )