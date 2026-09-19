from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed

from wtforms import (
    StringField,
    TextAreaField,
    IntegerField,
    BooleanField,
    SubmitField
)

from wtforms.validators import (
    DataRequired,
    Optional,
    Email,
    URL,
    Length,
    NumberRange
)


class LeaderForm(FlaskForm):

    # ==========================================================
    # NAME
    # ==========================================================

    name = StringField(
        "Full Name",
        validators=[
            DataRequired(),
            Length(max=150)
        ]
    )

    # ==========================================================
    # POSITION
    # ==========================================================

    position = StringField(
        "Position",
        validators=[
            DataRequired(),
            Length(max=150)
        ]
    )

    # ==========================================================
    # PHOTO
    # ==========================================================

    photo = FileField(
        "Leader Photo",
        validators=[
            Optional(),
            FileAllowed(
                [
                    "jpg",
                    "jpeg",
                    "png",
                    "webp"
                ],
                "Only JPG, JPEG, PNG and WEBP images are allowed."
            )
        ]
    )

    # ==========================================================
    # BIOGRAPHY
    # ==========================================================

    bio = TextAreaField(
        "Biography",
        validators=[
            Optional()
        ]
    )

    # ==========================================================
    # EMAIL
    # ==========================================================

    email = StringField(
        "Email Address",
        validators=[
            Optional(),
            Email(),
            Length(max=150)
        ]
    )

    # ==========================================================
    # PHONE
    # ==========================================================

    phone = StringField(
        "Phone Number",
        validators=[
            Optional(),
            Length(max=50)
        ]
    )

    # ==========================================================
    # FACEBOOK
    # ==========================================================

    facebook = StringField(
        "Facebook URL",
        validators=[
            Optional(),
            URL(),
            Length(max=255)
        ]
    )

    # ==========================================================
    # TWITTER / X
    # ==========================================================

    twitter = StringField(
        "Twitter / X URL",
        validators=[
            Optional(),
            URL(),
            Length(max=255)
        ]
    )

    # ==========================================================
    # LINKEDIN
    # ==========================================================

    linkedin = StringField(
        "LinkedIn URL",
        validators=[
            Optional(),
            URL(),
            Length(max=255)
        ]
    )

    # ==========================================================
    # DISPLAY ORDER
    # ==========================================================

    display_order = IntegerField(
        "Display Order",
        default=1,
        validators=[
            Optional(),
            NumberRange(
                min=1,
                message="Display order must be at least 1."
            )
        ]
    )

    # ==========================================================
    # ACTIVE
    # ==========================================================

    is_active = BooleanField(
        "Active",
        default=True
    )

    # ==========================================================
    # SUBMIT
    # ==========================================================

    submit = SubmitField(
        "Save Leader"
    )