from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed

from wtforms import (
    StringField,
    PasswordField,
    SelectField,
    BooleanField,
    FileField,
    SubmitField,
)

from wtforms.fields import EmailField

from wtforms.validators import (
    DataRequired,
    Email,
    EqualTo,
    Length,
    Optional,
)

from app.utils.constants import Roles


def get_role_choices():

    from flask_login import current_user

    choices = list(Roles.CHOICES)

    if not current_user.is_super_admin:

        choices = [
            choice
            for choice in choices
            if choice[0] != "Super Admin"
        ]

    return choices


class UserForm(FlaskForm):

    first_name = StringField(
        "First Name",
        validators=[
            DataRequired(),
            Length(max=100),
        ],
    )

    last_name = StringField(
        "Last Name",
        validators=[
            DataRequired(),
            Length(max=100),
        ],
    )

    username = StringField(
        "Username",
        validators=[
            DataRequired(),
            Length(max=100),
        ],
    )

    email = EmailField(
        "Email Address",
        validators=[
            DataRequired(),
            Email(),
            Length(max=120),
        ],
    )

    phone = StringField(
        "Phone Number",
        validators=[
            Optional(),
            Length(max=30),
        ],
    )

    role = SelectField(
        "Role",
        choices=[],
        validators=[
            DataRequired(),
        ],
    )

    client_id = SelectField(
        "Organization",
        coerce=int,
        choices=[],
        validators=[
            Optional(),
        ],
    )

    photo = FileField(
        "Profile Photo",
        validators=[
            Optional(),
            FileAllowed(
                [
                    "jpg",
                    "jpeg",
                    "png",
                    "webp",
                ],
                "Only JPG, JPEG, PNG and WEBP images are allowed.",
            ),
        ],
    )

    password = PasswordField(
        "Password",
        validators=[
            DataRequired(),
            Length(
                min=8,
                message="Password must be at least 8 characters.",
            ),
        ],
    )

    confirm_password = PasswordField(
        "Confirm Password",
        validators=[
            DataRequired(),
            EqualTo(
                "password",
                message="Passwords must match.",
            ),
        ],
    )

    is_active = BooleanField(
        "Active",
        default=True,
    )

    submit = SubmitField(
        "Save User",
    )

    def __init__(
        self,
        *args,
        **kwargs
    ):

        super().__init__(
            *args,
            **kwargs
        )

        self.role.choices = get_role_choices()


class EditUserForm(FlaskForm):

    first_name = StringField(
        "First Name",
        validators=[
            DataRequired(),
            Length(max=100),
        ],
    )

    last_name = StringField(
        "Last Name",
        validators=[
            DataRequired(),
            Length(max=100),
        ],
    )

    username = StringField(
        "Username",
        validators=[
            DataRequired(),
            Length(max=100),
        ],
    )

    email = EmailField(
        "Email Address",
        validators=[
            DataRequired(),
            Email(),
            Length(max=120),
        ],
    )

    phone = StringField(
        "Phone Number",
        validators=[
            Optional(),
            Length(max=30),
        ],
    )

    role = SelectField(
        "Role",
        choices=[],
        validators=[
            DataRequired(),
        ],
    )

    client_id = SelectField(
        "Organization",
        coerce=int,
        choices=[],
        validators=[
            Optional(),
        ],
    )

    photo = FileField(
        "Profile Photo",
        validators=[
            Optional(),
            FileAllowed(
                [
                    "jpg",
                    "jpeg",
                    "png",
                    "webp",
                ],
                "Only JPG, JPEG, PNG and WEBP images are allowed.",
            ),
        ],
    )

    password = PasswordField(
        "New Password",
        validators=[
            Optional(),
            Length(
                min=8,
                message="Password must be at least 8 characters.",
            ),
        ],
    )

    confirm_password = PasswordField(
        "Confirm Password",
        validators=[
            Optional(),
            EqualTo(
                "password",
                message="Passwords must match.",
            ),
        ],
    )

    is_active = BooleanField(
        "Active",
    )

    submit = SubmitField(
        "Update User",
    )

    def __init__(
        self,
        *args,
        **kwargs
    ):

        super().__init__(
            *args,
            **kwargs
        )

        self.role.choices = get_role_choices()


class ChangePasswordForm(FlaskForm):

    current_password = PasswordField(
        "Current Password",
        validators=[
            DataRequired(),
        ],
    )

    password = PasswordField(
        "New Password",
        validators=[
            DataRequired(),
            Length(
                min=8,
                message="Password must be at least 8 characters.",
            ),
        ],
    )

    confirm_password = PasswordField(
        "Confirm New Password",
        validators=[
            DataRequired(),
            EqualTo(
                "password",
                message="Passwords must match.",
            ),
        ],
    )

    submit = SubmitField(
        "Change Password",
    )