import pytest

from api.constants import Status


@pytest.mark.parametrize('api_method', [
    '/api/v1/ping',
    '/api/v1/ping/'
])
async def test_ping(test_client, web_server, api_method):
    client = await test_client(web_server)
    resp = await client.get(api_method)

    assert resp.status == 200

    data = await resp.json()
    assert data == {'status': Status.OK}
