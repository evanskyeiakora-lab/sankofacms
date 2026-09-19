from datetime import datetime

from app.extensions import db


class MembershipApplication(db.Model):

    __tablename__ = "membership_applications"

    # ==========================================================
    # PRIMARY KEY
    # ==========================================================

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    # ==========================================================
    # TENANT / CLIENT
    # ==========================================================

    client_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "clients.id",
            ondelete="SET NULL",
        ),
        nullable=True,
        index=True,
    )

    client = db.relationship(
        "Client",
        backref=db.backref(
            "membership_applications",
            lazy=True,
        ),
    )

    # ==========================================================
    # APPLICANT INFORMATION
    # ==========================================================

    full_name = db.Column(
        db.String(150),
        nullable=False,
    )

    email = db.Column(
        db.String(120),
        nullable=False,
    )

    phone = db.Column(
        db.String(30),
        nullable=False,
    )

    location = db.Column(
        db.String(150),
        nullable=True,
    )

    interest = db.Column(
        db.Text,
        nullable=True,
    )

    # ==========================================================
    # APPLICATION STATUS
    # ==========================================================

    status = db.Column(
        db.String(30),
        default="Pending",
        nullable=False,
    )

    # ==========================================================
    # MEMBER CONVERSION
    # ==========================================================

    is_converted = db.Column(
        db.Boolean,
        default=False,
        nullable=False,
    )

    member_id = db.Column(
        db.Integer,
        nullable=True,
    )

    # ==========================================================
    # TIMESTAMPS
    # ==========================================================

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
    )

    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    # ==========================================================
    # REPRESENTATION
    # ==========================================================

    def __repr__(self):

        return (
            f"<MembershipApplication {self.full_name}>"
        )