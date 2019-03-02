import asyncio
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from api.helpers import json_response
from api.constants import Status
from commons.helpers import get_password
from db.models import User


async def register(request):
    data = await request.json()
    required_parameters = ['first_name', 'last_name', 'login', 'password']

    for field in required_parameters:
        if field not in data:
            raise KeyError()

    data['password'] = get_password(data['password'])

    async with request.app.db.acquire() as connection:
        query = select(['*']).select_from(User).where(
            User.login == data['login']
        )
        user = await asyncio.wait_for(connection.fetchrow(query), timeout=None)

        if not user:
            insert_q = insert(
                User,
                data
            ).on_conflict_do_nothing().returning(User.id)

            user_id = await asyncio.shield(connection.fetchval(insert_q))
        else:
            user_id = user['id']


    return json_response(data={'status': Status.OK, 'user_id': user_id})
