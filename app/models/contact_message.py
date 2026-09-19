
from app.extensions import db
from app.models.mixins import TimestampMixin


class ContactMessage(
    TimestampMixin,
    db.Model,
):

    __tablename__ = "contact_messages"

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    # ======================================================
    # ORGANIZATION
    # ======================================================

    client_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "clients.id",
            ondelete="SET NULL",
        ),
        nullable=True,
        index=True,
    )

    # ======================================================
    # CONTACT INFORMATION
    # ======================================================

    name = db.Column(
        db.String(150),
        nullable=False,
        index=True,
    )

    email = db.Column(
        db.String(255),
        nullable=False,
        index=True,
    )

    phone = db.Column(
        db.String(50),
        nullable=True,
    )

    subject = db.Column(
        db.String(255),
        nullable=False,
        index=True,
    )

    message = db.Column(
        db.Text,
        nullable=False,
    )

    # ======================================================
    # MESSAGE STATUS
    # ======================================================

    is_read = db.Column(
        db.Boolean,
        default=False,
        nullable=False,
        index=True,
    )

    replied = db.Column(
        db.Boolean,
        default=False,
        nullable=False,
        index=True,
    )

    # ======================================================
    # REQUEST INFORMATION
    # ======================================================

    ip_address = db.Column(
        db.String(45),
        nullable=True,
    )

    user_agent = db.Column(
        db.Text,
        nullable=True,
    )

    # ======================================================
    # REPRESENTATION
    # ======================================================

    def __repr__(self):

        return f"<ContactMessage {self.name}>"