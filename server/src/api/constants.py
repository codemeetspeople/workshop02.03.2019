"""Synctool public API constants module."""

from aiohttp.web_exceptions import (
    HTTPUnsupportedMediaType,
    HTTPBadRequest,
    HTTPInternalServerError,
    HTTPUnprocessableEntity,
)

from commons.helpers import Constants
from .helpers import Error


class Headers(Constants):
    """Acceptable requests headers."""

    CONTENT_TYPE = 'Content-Type'


class ContentType(Constants):
    """Supported requests content types."""

    JSON = 'application/json'
    FORM_MULTIPART = 'multipart/form-data'


class Errors(Constants):
    """Synctool public API errors."""

    WRONG_CONTENT_TYPE = Error(
        4152, HTTPUnsupportedMediaType, 'Wrong {}. Should be one of: {{content_types}}'.format(Headers.CONTENT_TYPE)
    )
    NO_REQUIRED_PARAMETERS = Error(4002, HTTPBadRequest, 'Required parameters missed: {params}')
    UNKNOWN_SERVER_ERROR = Error(5002, HTTPInternalServerError, 'Unknown server error!')
    UNPROCESSABLE_ENTITY = Error(4222, HTTPUnprocessableEntity, 'Request content not in JSON')
    WRONG_PARAMETER_TYPE = Error(4004, HTTPBadRequest, 'Wrong type for parameter {param}. Should be {p_type}')
    WRONG_JSON_STRUCTURE = Error(4007, HTTPBadRequest, 'Wrong JSON structure. Errors: {errors}')


class Status(Constants):
    """Synctool pubslic API response statuses."""

    OK = 'ok'
    ERROR = 'error'


class UnauthorizedEndpoints(Constants):
    """Unauthorized endpoints."""

    ROUTES = [
        'ping/', 'ping',
        'login/', 'login',
        'register/', 'register'
    ]
