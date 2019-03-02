"""Authentication API handler module."""

import asyncio

from aiohttp import web
from sqlalchemy import select, update

from db.models import User
from api.helpers import json_response
from api.constants import Status
from commons.helpers import generate_token, get_password


async def auth(request):
    """Authenticate user on server."""
    data = await request.json()

    login = data.get('login')
    password = data.get('password')

    if not login or not password:
        return web.HTTPBadRequest()

    async with request.app.db.acquire() as connection:
        user_query = select(['*']).select_from(User).where(
            User.login == login
        ).where(User.password == get_password(password))

        user = await asyncio.wait_for(connection.fetchrow(user_query), timeout=None)

        if not user:
            return json_response(data={'status': Status.ERROR, 'message': 'User not found!'})

        token = generate_token(user['id'])

        await connection.execute(
            update(User).where(User.id == user['id']).values(
                token=token
            )
        )

    response = web.json_response({
        'status': Status.OK
    })
    response.set_cookie(name='token', value=token)

    return response
