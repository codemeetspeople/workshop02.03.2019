import pytest

from api.app import init_server


@pytest.fixture(scope='module')
def web_server():
    app = init_server()
    return app
