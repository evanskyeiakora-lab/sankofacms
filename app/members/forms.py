from flask_wtf import FlaskForm
from flask_wtf.file import (
    FileField,
    FileAllowed
)

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
    Length,
    Email,
    NumberRange,
    URL
)


# ==========================================
# Member Form
# ==========================================

class MemberForm(FlaskForm):

    # --------------------------------------
    # Full Name
    # --------------------------------------

    full_name = StringField(
        "Full Name",
        validators=[
            DataRequired(),
            Length(max=150)
        ]
    )


    # --------------------------------------
    # Position
    # --------------------------------------

    position = StringField(
        "Position",
        validators=[
            DataRequired(),
            Length(max=100)
        ]
    )


    # --------------------------------------
    # Biography
    # --------------------------------------

    biography = TextAreaField(
        "Biography",
        validators=[
            Optional()
        ]
    )


    # --------------------------------------
    # Photo
    # --------------------------------------

    photo = FileField(
        "Photo",
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


    # --------------------------------------
    # Email
    # --------------------------------------

    email = StringField(
        "Email",
        validators=[
            Optional(),
            Length(max=120),
            Email(
                message="Please enter a valid email address."
            )
        ]
    )


    # --------------------------------------
    # Phone
    # --------------------------------------

    phone = StringField(
        "Phone",
        validators=[
            Optional(),
            Length(max=30)
        ]
    )


    # --------------------------------------
    # Facebook
    # --------------------------------------

    facebook = StringField(
        "Facebook",
        validators=[
            Optional(),
            Length(max=255)
        ]
    )


    # --------------------------------------
    # LinkedIn
    # --------------------------------------

    linkedin = StringField(
        "LinkedIn",
        validators=[
            Optional(),
            Length(max=255)
        ]
    )


    # --------------------------------------
    # Twitter / X
    # --------------------------------------

    twitter = StringField(
        "Twitter / X",
        validators=[
            Optional(),
            Length(max=255)
        ]
    )


    # --------------------------------------
    # Display Order
    # --------------------------------------

    display_order = IntegerField(
        "Display Order",
        default=1,
        validators=[
            Optional(),
            NumberRange(
                min=0,
                message="Display order cannot be negative."
            )
        ]
    )


    # --------------------------------------
    # Active Status
    # --------------------------------------

    is_active = BooleanField(
        "Active",
        default=True
    )


    # --------------------------------------
    # Submit
    # --------------------------------------

    submit = SubmitField(
        "Save Member"
    )


# ==========================================
# Delete Member Form
# ==========================================

class DeleteMemberForm(FlaskForm):

    submit = SubmitField(
        "Delete Member"
    )