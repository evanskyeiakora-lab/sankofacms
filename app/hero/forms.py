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
    URL,
    Length,
    NumberRange
)


class HeroForm(FlaskForm):

    # ======================================================
    # TITLE
    # ======================================================

    title = StringField(
        "Title",
        validators=[
            DataRequired(
                message="Please enter a title."
            ),
            Length(
                max=255,
                message="Title cannot exceed 255 characters."
            )
        ]
    )


    # ======================================================
    # SUBTITLE
    # ======================================================

    subtitle = TextAreaField(
        "Subtitle",
        validators=[
            Optional()
        ]
    )


    # ======================================================
    # HERO IMAGE
    # ======================================================

    image = FileField(
        "Hero Image",
        validators=[
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


    # ======================================================
    # BUTTON TEXT
    # ======================================================

    button_text = StringField(
        "Button Text",
        validators=[
            Optional(),
            Length(
                max=100,
                message="Button text cannot exceed 100 characters."
            )
        ]
    )


    # ======================================================
    # BUTTON URL
    # ======================================================

    button_url = StringField(
        "Button URL",
        validators=[
            Optional(),
            Length(
                max=255,
                message="Button URL cannot exceed 255 characters."
            ),
            URL(
                message="Please enter a valid URL."
            )
        ]
    )


    # ======================================================
    # DISPLAY ORDER
    # ======================================================

    display_order = IntegerField(
        "Display Order",
        default=1,
        validators=[
            NumberRange(
                min=1,
                message="Display order must be 1 or greater."
            )
        ]
    )


    # ======================================================
    # ACTIVE
    # ======================================================

    is_active = BooleanField(
        "Active",
        default=True
    )


    # ======================================================
    # SUBMIT
    # ======================================================

    submit = SubmitField(
        "Save Slide"
    )