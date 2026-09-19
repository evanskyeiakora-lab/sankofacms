from app.models import Settings
from app.tenant import get_current_client


def inject_settings():
    """
    Make website settings and the current client
    available in every Jinja template.
    """

    current_client = get_current_client()

    settings = None

    if current_client:
        settings = (
            Settings.query
            .filter_by(client_id=current_client.id)
            .first()
        )

    return {
        "settings": settings,
        "current_client": current_client
    }