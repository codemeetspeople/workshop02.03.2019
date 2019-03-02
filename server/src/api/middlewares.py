"""Public API middlewares."""

from aiohttp import web

from db import db_manager
from db.models import User
from .constants import Errors, UnauthorizedEndpoints
from .helpers import Error
from .exceptions import ApiException


__all__ = (
    'error_middleware',
    'auth_middleware'
)


@web.middleware
async def error_middleware(request, handler):
    """Handle errors."""
    try:
        response = await handler(request)
        return response
    except ApiException:
        raise
    except web.HTTPException as e:
        error = Error(
            int(f"{e.status_code}2"),
            e.__class__,
            e.reason
        )
        raise error.get_exception(exception_params={k: v for k, v in e.__dict__.items() if not k.startswith('_')})
    except Exception:
        raise Errors.UNKNOWN_SERVER_ERROR.get_exception()


async def auth_middleware(app, handler):
    """Authenticate users."""
    @web.middleware
    async def middleware_handler(request):
        """Check requests cookies and validate token."""
        cookies = request.cookies

        authorization_required = True
        for endpoint in UnauthorizedEndpoints.ROUTES:
            if request.path.endswith(endpoint):
                authorization_required = False
                break

        if authorization_required and not cookies:
            return web.HTTPUnauthorized()

        if authorization_required:
            try:
                with db_manager.master_session() as db:
                    user = db.query(User).filter(User.token == cookies['token']).first()
            except Exception:
                return web.HTTPUnauthorized()

            if not user:
                return web.HTTPUnauthorized()

            request.app.user = user
        return await handler(request)

    return middleware_handler
