from . import paths # noqa
import time

import pytest
from invoke import Context
from pytest_factoryboy import register

from db.migrations.tasks import downgrade, upgrade
from .factories import test_session, factories_list


# Register factories
list(map(register, factories_list))


@pytest.fixture(scope='session')
def invoke_context():
    return Context()


@pytest.yield_fixture(scope='session', autouse=True)
def db(invoke_context):
    upgrade(invoke_context, revision='head')
    # Migrations contain version creation that is current timestamp. If we want to create new one - we should sleep
    time.sleep(1)

    yield test_session

    test_session.close()
    downgrade(invoke_context, revision='base')
