"""Public API PING module."""
import ujson
from api.helpers import json_response
from api.constants import Status
from aiohttp import ClientSession, TCPConnector



async def check(request):
    """Check the API is alive."""

    status = 'fail'
    response_status = 200

    try:
        async with ClientSession(
                connector=TCPConnector(verify_ssl=False), raise_for_status=True
        ) as session:
            async with session.get('https://subchat.site/api/v1/ping/') as response:
                data = await response.read()
                data = ujson.loads(data.decode('utf-8'))

                if data['status'] == Status.OK:
                    status = 'alive'

                response_status = response.status
    except Exception as e:
        status = 'error'

    return json_response(status=response_status, data={'status': status})
