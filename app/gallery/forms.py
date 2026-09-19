from flask_wtf import FlaskForm
from flask_wtf.file import FileField

from wtforms import (
    StringField,
    TextAreaField,
    SelectField,
    IntegerField,
    BooleanField,
    SubmitField
)

from wtforms.validators import (
    DataRequired,
    Optional,
    Length,
    NumberRange,
    ValidationError
)

from app.utils.file_upload import allowed_file


class GalleryForm(FlaskForm):

    # ==========================================================
    # TITLE
    # ==========================================================

    title = StringField(
        "Title",
        validators=[
            DataRequired(),
            Length(max=255)
        ]
    )

    # ==========================================================
    # DESCRIPTION
    # ==========================================================

    description = TextAreaField(
        "Description",
        validators=[
            Optional(),
            Length(max=5000)
        ]
    )

    # ==========================================================
    # IMAGE
    # ==========================================================

    image = FileField(
        "Gallery Image",
        validators=[
            Optional()
        ]
    )

    # ==========================================================
    # CATEGORY
    # ==========================================================

    category = SelectField(
        "Category",
        choices=[
            ("General", "General"),
            ("Church Service", "Church Service"),
            ("Conference", "Conference"),
            ("Youth Ministry", "Youth Ministry"),
            ("Women's Ministry", "Women's Ministry"),
            ("Men's Ministry", "Men's Ministry"),
            ("Children", "Children"),
            ("Outreach", "Outreach"),
            ("Community", "Community")
        ],
        validators=[
            DataRequired()
        ]
    )

    # ==========================================================
    # DISPLAY ORDER
    # ==========================================================

    display_order = IntegerField(
        "Display Order",
        default=0,
        validators=[
            NumberRange(
                min=0,
                message="Display order cannot be negative."
            )
        ]
    )

    # ==========================================================
    # FEATURED
    # ==========================================================

    is_featured = BooleanField(
        "Featured Image",
        default=False
    )

    # ==========================================================
    # PUBLISHED
    # ==========================================================

    is_published = BooleanField(
        "Published",
        default=True
    )

    # ==========================================================
    # SUBMIT
    # ==========================================================

    submit = SubmitField(
        "Save Gallery"
    )

    # ==========================================================
    # IMAGE VALIDATION
    # ==========================================================

    def validate_image(self, field):

        # ------------------------------------------------------
        # NO NEW IMAGE
        # ------------------------------------------------------
        #
        # This is completely valid when editing.
        #
        # The existing image will remain unchanged.
        # ------------------------------------------------------

        if not field.data:

            return

        # ------------------------------------------------------
        # MAKE SURE WE HAVE A FILE OBJECT
        # ------------------------------------------------------

        if not hasattr(
            field.data,
            "filename"
        ):

            return

        # ------------------------------------------------------
        # GET FILENAME
        # ------------------------------------------------------

        filename = (
            field.data.filename or ""
        ).strip()

        # ------------------------------------------------------
        # EMPTY FILE INPUT
        # ------------------------------------------------------

        if not filename:

            return

        # ------------------------------------------------------
        # VALIDATE EXTENSION
        # ------------------------------------------------------

        if not allowed_file(
            filename
        ):

            raise ValidationError(
                "Invalid image upload. "
                "Only JPG, JPEG, PNG and WEBP images are allowed."
            )