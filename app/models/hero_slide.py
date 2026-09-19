from app.extensions import db
from app.models.mixins import TimestampMixin


class HeroSlide(
    TimestampMixin,
    db.Model
):

    __tablename__ = "hero_slides"

    # ======================================================
    # ID
    # ======================================================

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    # ======================================================
    # CLIENT
    # ======================================================

    client_id = db.Column(
        db.Integer,
        db.ForeignKey("clients.id"),
        nullable=True,
        index=True
    )

    client = db.relationship(
        "Client",
        backref=db.backref(
            "hero_slides",
            lazy=True
        )
    )

    # ======================================================
    # TITLE
    # ======================================================

    title = db.Column(
        db.String(255),
        nullable=False
    )

    # ======================================================
    # SUBTITLE
    # ======================================================

    subtitle = db.Column(
        db.Text,
        nullable=True
    )

    # ======================================================
    # HERO IMAGE
    # ======================================================

    image = db.Column(
        db.String(255),
        nullable=False
    )

    # ======================================================
    # BUTTON TEXT
    # ======================================================

    button_text = db.Column(
        db.String(100),
        nullable=True
    )

    # ======================================================
    # BUTTON URL
    # ======================================================

    button_url = db.Column(
        db.String(255),
        nullable=True
    )

    # ======================================================
    # DISPLAY ORDER
    # ======================================================

    display_order = db.Column(
        db.Integer,
        default=1,
        nullable=False,
        index=True
    )

    # ======================================================
    # ACTIVE
    # ======================================================

    is_active = db.Column(
        db.Boolean,
        default=True,
        nullable=False,
        index=True
    )

    # ======================================================
    # REPRESENTATION
    # ======================================================

    def __repr__(self):

        return f"<HeroSlide {self.title}>"