from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed

from wtforms import (
    StringField,
    TextAreaField,
    BooleanField,
    SubmitField
)

from wtforms.validators import (
    DataRequired,
    Length
)


class NewsForm(FlaskForm):

    # ==========================================================
    # TITLE
    # ==========================================================

    title = StringField(
        "News Title",
        validators=[
            DataRequired(),
            Length(max=255)
        ]
    )

    # ==========================================================
    # CONTENT
    # ==========================================================

    content = TextAreaField(
        "Content",
        validators=[
            DataRequired()
        ]
    )

    # ==========================================================
    # FEATURED IMAGE
    # ==========================================================

    featured_image = FileField(
        "Featured Image",
        validators=[
            FileAllowed(
                ["jpg", "jpeg", "png", "webp"],
                "Only JPG, JPEG, PNG and WEBP images are allowed."
            )
        ]
    )

    # ==========================================================
    # PUBLICATION STATUS
    # ==========================================================

    is_published = BooleanField(
        "Published",
        default=False
    )

    # ==========================================================
    # SUBMIT
    # ==========================================================

    submit = SubmitField(
        "Save News"
    )