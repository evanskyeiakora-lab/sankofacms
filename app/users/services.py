
from flask_login import current_user

from app.extensions import db
from app.models import User

from app.utils.file_upload import save_image
from app.utils.constants import USERS_FOLDER


class UserService:
    """
    Business logic for user management.

    Tenant rules:
    - Super Admins may manage users across organizations.
    - Other administrators may manage users belonging
      to their own organization only.
    """

    # =====================================================
    # CREATE USER
    # =====================================================

    @staticmethod
    def create_user(form, client_id=None):

        if (
            form.role.data == "Super Admin"
            and not current_user.is_super_admin
        ):
            raise ValueError(
                "Only a Super Admin can create a Super Admin account."
            )

        username = form.username.data.strip()
        email = form.email.data.strip().lower()

        if User.query.filter_by(username=username).first():
            raise ValueError(
                "Username already exists."
            )

        if User.query.filter_by(email=email).first():
            raise ValueError(
                "Email address already exists."
            )

        # A non-Super-Admin must belong to an organization.
        if form.role.data != "Super Admin" and not client_id:
            raise ValueError(
                "Please select an organization for this user."
            )

        # Super Admins can be platform-level users.
        if form.role.data == "Super Admin":
            assigned_client_id = client_id
        else:
            assigned_client_id = client_id

        filename = None

        uploaded_photo = form.photo.data

        if (
            uploaded_photo
            and getattr(uploaded_photo, "filename", "")
        ):
            filename = save_image(
                uploaded_photo,
                USERS_FOLDER
            )

        user = User(
            client_id=assigned_client_id,
            first_name=form.first_name.data.strip(),
            last_name=form.last_name.data.strip(),
            username=username,
            email=email,
            phone=(
                form.phone.data.strip()
                if form.phone.data
                else None
            ),
            photo=filename,
            role=form.role.data,
            is_active=bool(form.is_active.data),
        )

        user.set_password(form.password.data)

        db.session.add(user)
        db.session.commit()

        return user

    # =====================================================
    # UPDATE USER
    # =====================================================

    @staticmethod
    def update_user(
        user,
        form,
        client_id=None,
        allow_role_change=True
    ):

        username = form.username.data.strip()
        email = form.email.data.strip().lower()

        existing_username = (
            User.query
            .filter(
                User.username == username,
                User.id != user.id
            )
            .first()
        )

        if existing_username:
            raise ValueError(
                "Username already exists."
            )

        existing_email = (
            User.query
            .filter(
                User.email == email,
                User.id != user.id
            )
            .first()
        )

        if existing_email:
            raise ValueError(
                "Email address already exists."
            )

        # =================================================
        # ROLE PROTECTION
        # =================================================

        if allow_role_change:

            requested_role = form.role.data

            if (
                requested_role == "Super Admin"
                and not current_user.is_super_admin
            ):
                raise ValueError(
                    "Only a Super Admin can assign the Super Admin role."
                )

            if (
                user.is_super_admin
                and requested_role != "Super Admin"
            ):

                total_super_admins = (
                    User.query
                    .filter_by(role="Super Admin")
                    .count()
                )

                if total_super_admins <= 1:
                    raise ValueError(
                        "The last Super Admin cannot be demoted."
                    )

            if (
                user.id == current_user.id
                and user.is_super_admin
                and requested_role != "Super Admin"
            ):
                raise ValueError(
                    "You cannot remove the Super Admin role "
                    "from your own account."
                )

            user.role = requested_role

        # =================================================
        # ORGANIZATION
        # =================================================

        if client_id is not None:
            user.client_id = client_id

        if (
            user.role != "Super Admin"
            and not user.client_id
        ):
            raise ValueError(
                "A non-Super-Admin user must belong to an organization."
            )

        # =================================================
        # PERSONAL INFORMATION
        # =================================================

        user.first_name = form.first_name.data.strip()
        user.last_name = form.last_name.data.strip()
        user.username = username
        user.email = email

        user.phone = (
            form.phone.data.strip()
            if form.phone.data
            else None
        )

        # =================================================
        # ACTIVE STATUS
        # =================================================

        if (
            user.id == current_user.id
            and user.is_super_admin
            and not form.is_active.data
        ):
            raise ValueError(
                "You cannot deactivate your own Super Admin account."
            )

        user.is_active = bool(form.is_active.data)

        # =================================================
        # PROFILE PHOTO
        # =================================================

        uploaded_photo = form.photo.data

        if (
            uploaded_photo
            and getattr(uploaded_photo, "filename", "")
        ):

            filename = save_image(
                uploaded_photo,
                USERS_FOLDER
            )

            if filename:
                user.photo = filename

        # =================================================
        # PASSWORD
        # =================================================

        if form.password.data:
            user.set_password(form.password.data)

        db.session.commit()

        return user

    # =====================================================
    # DELETE USER
    # =====================================================

    @staticmethod
    def delete_user(user):

        if current_user.id == user.id:
            raise ValueError(
                "You cannot delete your own account."
            )

        if user.is_super_admin:

            total_super_admins = (
                User.query
                .filter_by(role="Super Admin")
                .count()
            )

            if total_super_admins <= 1:
                raise ValueError(
                    "The last Super Admin cannot be deleted."
                )

        db.session.delete(user)
        db.session.commit()

    # =====================================================
    # CHANGE PASSWORD
    # =====================================================

    @staticmethod
    def change_password(user, password):

        user.set_password(password)

        db.session.commit()

        return user

    # =====================================================
    # ACTIVATE USER
    # =====================================================

    @staticmethod
    def activate(user):

        user.is_active = True

        db.session.commit()

        return user

    # =====================================================
    # DEACTIVATE USER
    # =====================================================

    @staticmethod
    def deactivate(user):

        if current_user.id == user.id:
            raise ValueError(
                "You cannot deactivate your own account."
            )

        if user.is_super_admin:

            total_super_admins = (
                User.query
                .filter_by(role="Super Admin")
                .count()
            )

            if total_super_admins <= 1:
                raise ValueError(
                    "The last Super Admin cannot be deactivated."
                )

        user.is_active = False

        db.session.commit()

        return user