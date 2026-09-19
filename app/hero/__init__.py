from flask import Blueprint

hero_bp = Blueprint(
    "hero",
    __name__,
    url_prefix="/admin/hero"
)

from . import routes