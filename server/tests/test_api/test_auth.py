import pytest

from api.constants import Status
from commons.helpers import get_password
from db.models import User


_USER_PASSWORD = 'qwerty123'
_TOKEN = '1klj3dfghjvcvbn86y'


@pytest.fixture
def user(db, user_factory):
    try:
        yield user_factory(**{
            'first_name': 'Test',
            'last_name': 'User',
            'login': 'test_user',
            'password': get_password(_USER_PASSWORD)
        })
    finally:
        db.query(User).delete()


@pytest.mark.parametrize('api_method', [
    '/api/v1/login',
    '/api/v1/login/'
])
async def test_auth_ok(test_client, web_server, user, mocker, api_method):
    client = await test_client(web_server)

    mocker.patch('api.v1.handlers.auth.generate_token', side_effect=lambda *args, **kwargs: _TOKEN)

    resp = await client.post(api_method, json={
        'login': user.login,
        'password': _USER_PASSWORD
    })

    data = await resp.json()
    assert resp.status == 200

    assert data == {
        'status': Status.OK
    }

    assert resp.cookies['token'].value == _TOKEN
