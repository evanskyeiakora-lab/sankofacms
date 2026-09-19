from app.extensions import db
from app.models.mixins import TimestampMixin


class Settings(TimestampMixin, db.Model):
    __tablename__ = "settings"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    # ==========================
    # Client
    # ==========================
    client_id = db.Column(
        db.Integer,
        db.ForeignKey("clients.id"),
        unique=True,
        nullable=True
    )

    # ==========================
    # General
    # ==========================
    site_name = db.Column(
        db.String(255),
        nullable=False,
        default="Apex Citizens of Ghana"
    )

    tagline = db.Column(
        db.String(255),
        nullable=True
    )

    about = db.Column(
        db.Text,
        nullable=True
    )

    # ==========================
    # Branding
    # ==========================
    logo = db.Column(
        db.String(255),
        nullable=True
    )

    favicon = db.Column(
        db.String(255),
        nullable=True
    )

    # ==========================
    # Contact
    # ==========================
    email = db.Column(
        db.String(255),
        nullable=True
    )

    phone = db.Column(
        db.String(100),
        nullable=True
    )

    whatsapp = db.Column(
        db.String(100),
        nullable=True
    )

    address = db.Column(
        db.Text,
        nullable=True
    )

    # ==========================
    # Social Media
    # ==========================
    facebook = db.Column(
        db.String(500),
        nullable=True
    )

    instagram = db.Column(
        db.String(500),
        nullable=True
    )

    twitter = db.Column(
        db.String(500),
        nullable=True
    )

    youtube = db.Column(
        db.String(500),
        nullable=True
    )

    linkedin = db.Column(
        db.String(500),
        nullable=True
    )

    # ==========================
    # Footer
    # ==========================
    footer_text = db.Column(
        db.String(500),
        nullable=True
    )

    copyright_text = db.Column(
        db.String(255),
        nullable=True
    )

    # ==========================
    # Google Maps
    # ==========================
    google_map = db.Column(
        db.Text,
        nullable=True
    )

    # ==========================
    # SEO
    # ==========================
    meta_title = db.Column(
        db.String(255),
        nullable=True
    )

    meta_description = db.Column(
        db.Text,
        nullable=True
    )

    meta_keywords = db.Column(
        db.Text,
        nullable=True
    )

    # ==========================
    # System
    # ==========================
    maintenance_mode = db.Column(
        db.Boolean,
        default=False
    )

    def __repr__(self):
        return f"<Settings {self.site_name}>"