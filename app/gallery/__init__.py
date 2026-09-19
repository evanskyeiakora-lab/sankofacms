from flask import Blueprint

gallery_bp = Blueprint(
    "gallery",
    __name__,
    url_prefix="/admin/gallery"
)

from . import routes