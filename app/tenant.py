from flask import request, g
from app.models import Client


def get_current_client():
    """
    Resolve the current client from the incoming domain.
    """

    if hasattr(g, "current_client"):
        return g.current_client

    host = request.host.lower()

    # Remove port during local development
    host = host.split(":")[0]

    client = (
        Client.query
        .filter(
            Client.domain == host,
            Client.is_active.is_(True)
        )
        .first()
    )

    g.current_client = client

    return client