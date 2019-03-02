import pytest

from db import db_manager, connection_manager


@pytest.mark.asyncio
async def test_async_db_manager_contextmanager(event_loop):
    pool = await db_manager.async_master()
    async with pool.acquire() as conn:
        async with conn.transaction():
            await conn.fetchrow('SELECT * FROM pg_stat_activity LIMIT 1')
    await db_manager.async_close_master()


def test_sync_master_session(event_loop):
    with db_manager.master_session() as db:
        db.execute('SELECT * FROM pg_stat_activity LIMIT 1').first()


@pytest.mark.asyncio
async def test_async_connection_manager_context(event_loop):
    manager = connection_manager(loop=event_loop)

    async with manager.acquire() as conn:
        async with conn.transaction():
            await conn.fetchrow('SELECT * FROM pg_stat_activity LIMIT 1')


@pytest.mark.asyncio
async def test_async_connection_manager(event_loop):
    manager = connection_manager(loop=event_loop)
    conn = await manager

    async with conn.transaction():
        await conn.fetchrow('SELECT * FROM pg_stat_activity LIMIT 1')

    await manager.close()
