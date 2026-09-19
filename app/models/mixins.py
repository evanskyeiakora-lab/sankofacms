from datetime import datetime, timezone

from app.extensions import db


class TimestampMixin:
    """
    Adds created_at and updated_at timestamps.
    """

    created_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )


class PublishMixin:
    """
    Adds publishing fields for CMS content.
    """

    is_published = db.Column(
        db.Boolean,
        default=True,
        nullable=False
    )

    published_at = db.Column(
        db.DateTime,
        nullable=True
    )