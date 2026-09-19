from app.extensions import db
from app.models.mixins import TimestampMixin


class Leader(
    TimestampMixin,
    db.Model
):

    __tablename__ = "leaders"

    # ======================================================
    # PRIMARY KEY
    # ======================================================

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    # ======================================================
    # TENANT
    # ======================================================

    client_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "clients.id"
        ),
        nullable=True,
        index=True
    )

    # ======================================================
    # NAME
    # ======================================================

    name = db.Column(
        db.String(150),
        nullable=False
    )

    # ======================================================
    # POSITION
    # ======================================================

    position = db.Column(
        db.String(150),
        nullable=False
    )

    # ======================================================
    # PHOTO
    # ======================================================

    photo = db.Column(
        db.String(255),
        nullable=True
    )

    # ======================================================
    # BIO
    # ======================================================

    bio = db.Column(
        db.Text,
        nullable=True
    )

    # ======================================================
    # EMAIL
    # ======================================================

    email = db.Column(
        db.String(150),
        nullable=True
    )

    # ======================================================
    # PHONE
    # ======================================================

    phone = db.Column(
        db.String(50),
        nullable=True
    )

    # ======================================================
    # SOCIAL MEDIA
    # ======================================================

    facebook = db.Column(
        db.String(255),
        nullable=True
    )

    twitter = db.Column(
        db.String(255),
        nullable=True
    )

    linkedin = db.Column(
        db.String(255),
        nullable=True
    )

    # ======================================================
    # DISPLAY ORDER
    # ======================================================

    display_order = db.Column(
        db.Integer,
        default=1
    )

    # ======================================================
    # ACTIVE
    # ======================================================

    is_active = db.Column(
        db.Boolean,
        default=True
    )

    # ======================================================
    # REPRESENTATION
    # ======================================================

    def __repr__(self):

        return (
            f"<Leader {self.name}>"
        )