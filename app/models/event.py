from datetime import datetime, timezone
from slugify import slugify

from app.extensions import db
from app.models.mixins import (
    TimestampMixin,
    PublishMixin
)


class Event(
    TimestampMixin,
    PublishMixin,
    db.Model
):

    __tablename__ = "events"

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
        db.ForeignKey(
            "clients.id",
            name="fk_events_client_id_clients"
        ),
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
        unique=True,
        nullable=False,
        index=True
    )

    # ==========================================================
    # DESCRIPTION
    # ==========================================================

    description = db.Column(
        db.Text,
        nullable=True
    )

    # ==========================================================
    # VENUE
    # ==========================================================

    venue = db.Column(
        db.String(255),
        nullable=True
    )

    # ==========================================================
    # ORGANIZER
    # ==========================================================

    organizer = db.Column(
        db.String(255),
        nullable=True
    )

    # ==========================================================
    # START DATE
    # ==========================================================

    start_date = db.Column(
        db.Date,
        nullable=False
    )

    # ==========================================================
    # END DATE
    # ==========================================================

    end_date = db.Column(
        db.Date,
        nullable=True
    )

    # ==========================================================
    # START TIME
    # ==========================================================

    start_time = db.Column(
        db.Time,
        nullable=True
    )

    # ==========================================================
    # END TIME
    # ==========================================================

    end_time = db.Column(
        db.Time,
        nullable=True
    )

    # ==========================================================
    # REGISTRATION LINK
    # ==========================================================

    registration_link = db.Column(
        db.String(500),
        nullable=True
    )

    # ==========================================================
    # FEATURED IMAGE
    # ==========================================================

    featured_image = db.Column(
        db.String(255),
        nullable=True
    )

    # ==========================================================
    # FEATURED EVENT
    # ==========================================================

    is_featured = db.Column(
        db.Boolean,
        default=False,
        nullable=False
    )

    # ==========================================================
    # DISPLAY ORDER
    # ==========================================================

    display_order = db.Column(
        db.Integer,
        default=1,
        nullable=False
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

            query = Event.query.filter(
                Event.slug == slug
            )

            # Ignore current event when editing
            if self.id is not None:

                query = query.filter(
                    Event.id != self.id
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
            f"<Event {self.title}>"
        )