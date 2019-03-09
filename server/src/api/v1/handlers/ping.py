"""Public API PING module."""

from api.helpers import json_response
from api.constants import Status


async def ping(request):
    """Check the API is alive."""
    return json_response(data={'status': Status.OK})
