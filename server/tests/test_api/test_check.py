import pytest


class FakeResponse:
    def __init__(self, status, data):
        self.status = status
        self.data = data

    async def read(self):
        return self.data


class FakeSessionContext:
    def __init__(self, coro):
        self._coro = coro

    async def __aenter__(self):
        return self._coro

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass


class FakeClientSession:
    class Status:
        OK = 'ok'
        FAIL = 'fail'
        ERROR = 'error'

    status = Status.OK

    def __init__(self, *args, **kwargs):
        self.url = 'https://subchat.site/api/v1/ping/'

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

    def get(self, url, *args, **kwargs):
        if url == self.url:
            if self.status == self.Status.OK:
                return FakeSessionContext(
                    FakeResponse(200, b'{"status": "ok"}')
                )

            if self.status == self.Status.FAIL:
                return FakeSessionContext(
                    FakeResponse(401, b'{"status": "fail"}')
                )

            if self.status == self.Status.ERROR:
                raise RuntimeError()


@pytest.mark.asyncio
@pytest.mark.parametrize('api_method, session_status, response_status, status', [
    ('/api/v1/check', FakeClientSession.Status.OK, 200, 'alive'),
    ('/api/v1/check/', FakeClientSession.Status.OK, 200, 'alive'),
    ('/api/v1/check', FakeClientSession.Status.FAIL, 401, 'fail'),
    ('/api/v1/check/', FakeClientSession.Status.FAIL, 401, 'fail'),
    ('/api/v1/check', FakeClientSession.Status.ERROR, 200, 'error'),
    ('/api/v1/check/', FakeClientSession.Status.ERROR, 200, 'error')
])
async def test_check_ok(
        test_client, web_server, api_method,
        session_status, response_status, status, mocker):

    FakeClientSession.status = session_status
    mocker.patch('api.v1.handlers.check.ClientSession', FakeClientSession)

    client = await test_client(web_server)
    resp = await client.get(api_method)

    assert resp.status == response_status

    data = await resp.json()
    assert data == {'status': status}
