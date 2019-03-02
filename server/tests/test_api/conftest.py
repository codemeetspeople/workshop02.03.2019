import pytest

from api.app import init_server


@pytest.fixture
def web_server():
    app = init_server()
    return app
