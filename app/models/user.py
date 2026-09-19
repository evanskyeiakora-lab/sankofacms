from datetime import datetime

from flask_login import UserMixin
from werkzeug.security import (
    generate_password_hash,
    check_password_hash,
)

from app.extensions import (
    db,
    login_manager,
)


class User(
    UserMixin,
    db.Model
):

    __tablename__ = "users"

    # ==========================================================
    # PRIMARY KEY
    # ==========================================================

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    # ==========================================================
    # TENANT
    # ==========================================================

    # NULL is allowed only for platform-level Super Admins.
    client_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "clients.id",
            ondelete="SET NULL",
        ),
        nullable=True,
        index=True,
    )

    # ==========================================================
    # PERSONAL INFORMATION
    # ==========================================================

    first_name = db.Column(
        db.String(100),
        nullable=False,
    )

    last_name = db.Column(
        db.String(100),
        nullable=False,
    )

    username = db.Column(
        db.String(100),
        nullable=False,
        unique=True,
        index=True,
    )

    email = db.Column(
        db.String(120),
        nullable=False,
        unique=True,
        index=True,
    )

    phone = db.Column(
        db.String(30),
        nullable=True,
    )

    photo = db.Column(
        db.String(255),
        nullable=True,
    )

    # ==========================================================
    # AUTHENTICATION
    # ==========================================================

    password_hash = db.Column(
        db.String(255),
        nullable=False,
    )

    # ==========================================================
    # ROLE AND STATUS
    # ==========================================================

    role = db.Column(
        db.String(30),
        nullable=False,
        default="Author",
        index=True,
    )

    is_active = db.Column(
        db.Boolean,
        nullable=False,
        default=True,
    )

    # ==========================================================
    # TIMESTAMPS
    # ==========================================================

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=True,
    )

    last_login = db.Column(
        db.DateTime,
        nullable=True,
    )

    # ==========================================================
    # RELATIONSHIP
    # ==========================================================

    client = db.relationship(
        "Client",
        backref=db.backref(
            "users",
            lazy=True,
        ),
    )

    # ==========================================================
    # PASSWORD METHODS
    # ==========================================================

    def set_password(self, password):

        self.password_hash = generate_password_hash(
            password
        )

    def check_password(self, password):

        return check_password_hash(
            self.password_hash,
            password
        )

    # ==========================================================
    # DISPLAY NAME
    # ==========================================================

    @property
    def full_name(self):

        return (
            f"{self.first_name} "
            f"{self.last_name}"
        ).strip()

    # ==========================================================
    # ROLE CHECKS
    # ==========================================================

    @property
    def is_super_admin(self):

        return self.role == "Super Admin"

    @property
    def is_admin(self):

        return self.role in (
            "Super Admin",
            "Administrator",
        )

    @property
    def is_editor(self):

        return self.role == "Editor"

    # ==========================================================
    # TENANT CHECK
    # ==========================================================

    def belongs_to_client(self, client_id):

        if self.is_super_admin:
            return True

        return self.client_id == client_id

    # ==========================================================
    # REPRESENTATION
    # ==========================================================

    def __repr__(self):

        return (
            f"<User {self.username}>"
        )


# ==========================================================
# FLASK-LOGIN USER LOADER
# ==========================================================

@login_manager.user_loader
def load_user(user_id):

    try:

        return db.session.get(
            User,
            int(user_id),
        )

    except (
        TypeError,
        ValueError,
    ):

        return None