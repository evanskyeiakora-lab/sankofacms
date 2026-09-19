import os
import uuid

from flask import current_app
from werkzeug.utils import secure_filename


# ==========================================================
# Allowed File
# ==========================================================

def allowed_file(filename):
    """
    Check whether the uploaded file has an allowed extension.
    """

    if not filename or "." not in filename:
        return False

    extension = (
        filename.rsplit(".", 1)[1].lower()
    )

    return extension in current_app.config[
        "ALLOWED_EXTENSIONS"
    ]


# ==========================================================
# Generate Unique Filename
# ==========================================================

def generate_unique_filename(filename):
    """
    Generate a unique filename while preserving
    the original extension.
    """

    extension = (
        filename.rsplit(".", 1)[1].lower()
    )

    return (
        f"{uuid.uuid4().hex}.{extension}"
    )


# ==========================================================
# Save Image
# ==========================================================

def save_image(file, folder):
    """
    Save an uploaded image and return the
    stored filename.
    """

    # --------------------------------------
    # No file
    # --------------------------------------

    if not file:
        return None

    # --------------------------------------
    # Make sure this is an uploaded file
    # --------------------------------------

    if not hasattr(file, "filename"):
        return None

    # --------------------------------------
    # Empty filename
    # --------------------------------------

    if not file.filename:
        return None

    # --------------------------------------
    # Validate extension
    # --------------------------------------

    if not allowed_file(
        file.filename
    ):

        raise ValueError(
            "Unsupported image format."
        )

    # --------------------------------------
    # Secure original filename
    # --------------------------------------

    secure_name = secure_filename(
        file.filename
    )

    # --------------------------------------
    # Generate unique filename
    # --------------------------------------

    filename = generate_unique_filename(
        secure_name
    )

    # --------------------------------------
    # Upload directory
    # --------------------------------------

    upload_folder = os.path.join(
        current_app.config["UPLOAD_FOLDER"],
        folder
    )

    os.makedirs(
        upload_folder,
        exist_ok=True
    )

    # --------------------------------------
    # Full file path
    # --------------------------------------

    filepath = os.path.join(
        upload_folder,
        filename
    )

    # --------------------------------------
    # Save file
    # --------------------------------------

    file.save(filepath)

    return filename


# ==========================================================
# Delete Image
# ==========================================================

def delete_image(filename, folder):
    """
    Delete an image from disk.
    """

    if not filename:
        return

    filepath = os.path.join(
        current_app.config["UPLOAD_FOLDER"],
        folder,
        filename
    )

    if os.path.exists(filepath):

        os.remove(filepath)


# ==========================================================
# Replace Image
# ==========================================================

def replace_image(
    old_image,
    new_file,
    folder
):
    """
    Replace an existing image with a newly
    uploaded one.

    If no new image is uploaded, the existing
    image is preserved.
    """

    # --------------------------------------
    # No new file
    # --------------------------------------

    if not new_file:

        return old_image

    # --------------------------------------
    # Make sure this is an uploaded file
    # --------------------------------------

    if not hasattr(
        new_file,
        "filename"
    ):

        return old_image

    # --------------------------------------
    # Empty filename
    # --------------------------------------

    if not new_file.filename:

        return old_image

    # --------------------------------------
    # Save new image FIRST
    # --------------------------------------

    new_filename = save_image(
        new_file,
        folder
    )

    # --------------------------------------
    # If saving failed, preserve old image
    # --------------------------------------

    if not new_filename:

        return old_image

    # --------------------------------------
    # Delete old image
    # --------------------------------------

    if old_image:

        delete_image(
            old_image,
            folder
        )

    # --------------------------------------
    # Return new filename
    # --------------------------------------

    return new_filename