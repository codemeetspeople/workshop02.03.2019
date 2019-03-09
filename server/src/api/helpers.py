"""API useful utils module."""

import ujson
from aiohttp import web

from .exceptions import ApiException


def json_response(*args, **kwargs):
    """Response with Content-Type: application/json header."""
    kwargs.setdefault('dumps', ujson.dumps)
    return web.json_response(*args, **kwargs)


class Error:
    """Error handling base class."""

    __slots__ = ('code', 'exception', 'reason')

    def __init__(self, code, exception, reason):
        """Initialize Error instance.

        :param code: Error code
        :param exception: Exception class
        :param reason: Error message

        """
        self.code = code
        api_exception = type(f'Api{exception.__name__}', (exception, ApiException), {'empty_body': True})

        self.exception = api_exception
        self.reason = reason

    def get_exception(self, exception_params=None, **kwargs):
        """Create Synctool specific error."""
        from .constants import ContentType, Status

        if not exception_params:
            exception_params = {}

        return self.exception(
            text=ujson.dumps(
                {
                    'status': Status.ERROR,
                    'error_code': self.code,
                    'error_text': self.reason.format(**kwargs)
                }
            ),
            content_type=ContentType.JSON,
            **exception_params
        )

    def __str__(self):
        """Represent error as a string."""
        return f'{self.code}: {self.reason}'
