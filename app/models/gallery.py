from app.extensions import db

from app.models.mixins import (
    TimestampMixin,
    PublishMixin
)

from app.utils.slug import generate_unique_slug


class Gallery(
    TimestampMixin,
    PublishMixin,
    db.Model
):

    __tablename__ = "gallery"


    # ======================================================
    # ID
    # ======================================================

    id = db.Column(
        db.Integer,
        primary_key=True
    )

        # ======================================================
    # CLIENT / TENANT
    # ======================================================

    client_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "clients.id",
            name="fk_gallery_client_id_clients"
        ),
        nullable=True,
        index=True
    )


    # ======================================================
    # TITLE
    # ======================================================

    title = db.Column(
        db.String(255),
        nullable=False,
        index=True
    )


    # ======================================================
    # SLUG
    # ======================================================

    slug = db.Column(
        db.String(255),
        unique=True,
        nullable=False,
        index=True
    )


    # ======================================================
    # DESCRIPTION
    # ======================================================

    description = db.Column(
        db.Text,
        nullable=True
    )


    # ======================================================
    # IMAGE
    # ======================================================

    image = db.Column(
        db.String(255),
        nullable=False
    )


    # ======================================================
    # CATEGORY
    # ======================================================

    category = db.Column(
        db.String(100),
        nullable=False,
        default="General",
        index=True
    )


    # ======================================================
    # DISPLAY ORDER
    # ======================================================

    display_order = db.Column(
        db.Integer,
        nullable=False,
        default=0,
        index=True
    )


    # ======================================================
    # FEATURED
    # ======================================================

    is_featured = db.Column(
        db.Boolean,
        default=False,
        nullable=False,
        index=True
    )


    # ======================================================
    # GENERATE SLUG
    # ======================================================

    def generate_slug(self):

        self.slug = generate_unique_slug(
            Gallery,
            self.title,
            self.id
        )


    # ======================================================
    # IMAGE URL
    # ======================================================

    @property
    def image_url(self):

        if self.image:

            return (
                f"uploads/gallery/{self.image}"
            )

        return "images/no-image.jpg"


    # ======================================================
    # REPRESENTATION
    # ======================================================

    def __repr__(self):

        return f"<Gallery {self.title}>"