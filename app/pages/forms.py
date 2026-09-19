from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed

from wtforms import (
    StringField,
    TextAreaField,
    BooleanField,
    SubmitField,
    SelectField
)

from wtforms.validators import (
    DataRequired,
    Length,
    Optional
)


class PageForm(FlaskForm):

    # ==========================================
    # Page Title
    # ==========================================

    title = StringField(
        "Page Title",
        validators=[
            DataRequired(),
            Length(max=200)
        ]
    )


    # ==========================================
    # Page Slug
    # ==========================================

    slug = StringField(
        "Slug",
        validators=[
            Optional(),
            Length(max=200)
        ],
        description="Leave blank to generate automatically."
    )


    # ==========================================
    # Page Role
    # ==========================================

    page_role = SelectField(
        "Page Role",
        choices=[
            ("normal", "Normal Page"),
            ("about-us", "Homepage About-us"),
            ("vision", "Homepage Vision"),
            ("mission", "Homepage Mission"),
            ("history", "Homepage History"),
            ("constitution", "Constitution"),
            ("footer", "Footer Page")
        ],
        default="normal"
    )


    # ==========================================
    # Content
    # ==========================================

    content = TextAreaField(
        "Content",
        validators=[
            DataRequired()
        ]
    )


    # ==========================================
    # Featured Image
    # ==========================================

    featured_image = FileField(
        "Featured Image",
        validators=[
            Optional(),
            FileAllowed(
                [
                    "jpg",
                    "jpeg",
                    "png",
                    "webp"
                ],
                "Images only."
            )
        ]
    )


    # ==========================================
    # SEO Meta Title
    # ==========================================

    meta_title = StringField(
        "Meta Title",
        validators=[
            Optional(),
            Length(max=255)
        ]
    )


    # ==========================================
    # SEO Meta Description
    # ==========================================

    meta_description = TextAreaField(
        "Meta Description",
        validators=[
            Optional(),
            Length(max=500)
        ]
    )


    # ==========================================
    # Published Status
    # ==========================================

    is_published = BooleanField(
        "Publish Page",
        default=True
    )


    # ==========================================
    # Submit
    # ==========================================

    submit = SubmitField(
        "Save Page"
    )


# ==========================================
# Delete Page Form
# ==========================================

class DeletePageForm(FlaskForm):

    submit = SubmitField(
        "Delete Page"
    )