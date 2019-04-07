"""Public API application module."""

import structlog

from aiohttp import web
from db import db_manager
from api.middlewares import error_middleware, auth_middleware
from api.v1.handlers import (
    ping, auth, register, check
)


logger = structlog.getLogger('api.' + __name__)


def init_server(loop=None):
    """Configure server before starting.

    :param loop: Event loop
    :return: Server app

    """
    app = web.Application(middlewares=[
        error_middleware,
        web.normalize_path_middleware(
            append_slash=True,
            merge_slashes=True,
            redirect_class=web.HTTPPermanentRedirect
        ),
        auth_middleware
    ])
    add_routes(app)

    async def init(app):
        """Configure app before starting server.

        :param app: Server app
        :return: Server app

        """
        app.db = await db_manager.async_master(loop)
        app.logger = logger

    app.on_startup.append(init)

    async def cleanup(app):
        """Close all open connections before stopping server.

        :param app: Server app
        :return: Server app

        """
        await db_manager.async_close_all()

    app.on_shutdown.append(cleanup)

    return app


def add_routes(app):
    """Configure server application endpoints."""

    app.router.add_get('/api/v1/ping/', ping.ping)
    app.router.add_post('/api/v1/login/', auth.auth)
    app.router.add_post('/api/v1/register/', register.register)
    app.router.add_get('/api/v1/check/', check.check)


app = init_server()
