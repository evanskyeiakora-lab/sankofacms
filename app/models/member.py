from datetime import datetime

from app.extensions import db


class Member(db.Model):
    __tablename__ = "members"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    client_id = db.Column(
        db.Integer,
        db.ForeignKey("clients.id"),
        nullable=True,
        index=True
    )

    full_name = db.Column(
        db.String(150),
        nullable=False
    )

    position = db.Column(
        db.String(100),
        nullable=False
    )

    biography = db.Column(
        db.Text,
        nullable=True
    )

    photo = db.Column(
        db.String(255),
        nullable=True
    )

    email = db.Column(
        db.String(120),
        nullable=True
    )

    phone = db.Column(
        db.String(30),
        nullable=True
    )

    facebook = db.Column(
        db.String(255),
        nullable=True
    )

    linkedin = db.Column(
        db.String(255),
        nullable=True
    )

    twitter = db.Column(
        db.String(255),
        nullable=True
    )

    display_order = db.Column(
        db.Integer,
        default=1
    )

    is_active = db.Column(
        db.Boolean,
        default=True
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    def __repr__(self):
        return f"<Member {self.full_name}>"