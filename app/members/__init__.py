from flask import Blueprint

members_bp = Blueprint(
    "members",
    __name__,
    url_prefix="/admin/members"
)

from . import routes