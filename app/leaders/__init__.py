from flask import Blueprint


leaders_bp = Blueprint(
    "leaders",
    __name__
)


from . import routes