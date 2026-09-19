from flask_wtf import FlaskForm
from flask_wtf.file import FileField

from wtforms import (
    StringField,
    TextAreaField,
    BooleanField,
    SubmitField
)

from wtforms.validators import (
    DataRequired,
    Optional,
    Email,
    URL,
    Length,
    ValidationError
)

from app.utils.file_upload import allowed_file


class SettingsForm(FlaskForm):

    # =====================================
    # General
    # =====================================

    site_name = StringField(
        "Site Name",
        validators=[
            DataRequired(),
            Length(max=255)
        ]
    )

    tagline = StringField(
        "Tagline",
        validators=[
            Optional(),
            Length(max=255)
        ]
    )

    about = TextAreaField(
        "About",
        validators=[
            Optional(),
            Length(max=5000)
        ]
    )

    # =====================================
    # Branding
    # =====================================

    logo = FileField(
        "Website Logo"
    )

    favicon = FileField(
        "Favicon"
    )

    # =====================================
    # Contact
    # =====================================

    email = StringField(
        "Email Address",
        validators=[
            Optional(),
            Email()
        ]
    )

    phone = StringField(
        "Phone Number",
        validators=[
            Optional(),
            Length(max=100)
        ]
    )

    whatsapp = StringField(
        "WhatsApp Number",
        validators=[
            Optional(),
            Length(max=100)
        ]
    )

    address = TextAreaField(
        "Office Address",
        validators=[
            Optional(),
            Length(max=1000)
        ]
    )

    # =====================================
    # Social Media
    # =====================================

    facebook = StringField(
        "Facebook URL",
        validators=[
            Optional(),
            URL(),
            Length(max=500)
        ]
    )

    instagram = StringField(
        "Instagram URL",
        validators=[
            Optional(),
            URL(),
            Length(max=500)
        ]
    )

    twitter = StringField(
        "Twitter / X URL",
        validators=[
            Optional(),
            URL(),
            Length(max=500)
        ]
    )

    youtube = StringField(
        "YouTube URL",
        validators=[
            Optional(),
            URL(),
            Length(max=500)
        ]
    )

    linkedin = StringField(
        "LinkedIn URL",
        validators=[
            Optional(),
            URL(),
            Length(max=500)
        ]
    )

    # =====================================
    # Footer
    # =====================================

    footer_text = TextAreaField(
        "Footer Text",
        validators=[
            Optional(),
            Length(max=500)
        ]
    )

    copyright_text = StringField(
        "Copyright",
        validators=[
            Optional(),
            Length(max=255)
        ]
    )

    # =====================================
    # Google Map
    # =====================================

    google_map = TextAreaField(
        "Google Maps Embed Code",
        validators=[
            Optional()
        ]
    )

    # =====================================
    # SEO
    # =====================================

    meta_title = StringField(
        "Default Meta Title",
        validators=[
            Optional(),
            Length(max=255)
        ]
    )

    meta_description = TextAreaField(
        "Meta Description",
        validators=[
            Optional(),
            Length(max=1000)
        ]
    )

    meta_keywords = TextAreaField(
        "Meta Keywords",
        validators=[
            Optional(),
            Length(max=1000)
        ]
    )

    # =====================================
    # System
    # =====================================

    maintenance_mode = BooleanField(
        "Enable Maintenance Mode"
    )

    submit = SubmitField(
        "Save Settings"
    )

    # =====================================
    # Validation
    # =====================================

    def validate_logo(self, field):

        if field.data and field.data.filename:

            if not allowed_file(field.data.filename):

                raise ValidationError(
                    "Logo must be JPG, JPEG, PNG or WEBP."
                )

    
def validate_favicon(form, field):
    """
    Validate the favicon upload.

    Allows an empty value or an existing filename string.
    Validates the file extension when a new file is uploaded.
    """

    file_data = field.data

    # No new file selected
    if not file_data:
        return

    # Existing filename stored as a string
    if isinstance(file_data, str):
        return

    # Uploaded file object
    filename = getattr(file_data, "filename", "")

    if not filename:
        return

    allowed_extensions = {
        "png",
        "jpg",
        "jpeg",
        "ico",
        "webp"
    }

    file_extension = (
        filename.rsplit(".", 1)[-1].lower()
        if "." in filename
        else ""
    )

    if file_extension not in allowed_extensions:
        raise ValidationError(
            "Invalid favicon format. "
            "Allowed formats: PNG, JPG, JPEG, ICO, and WEBP."
        )