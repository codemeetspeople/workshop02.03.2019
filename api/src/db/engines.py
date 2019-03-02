import os
import ujson

from sqlalchemy import event, exc, create_engine

from config import settings

DEFAULT_POOL_SIZE = 5
DEFAULT_MAX_OVERFLOW = 4


def add_engine_pidguard(engine):
    """Add multiprocessing guards.

    Forces a connection to be reconnected if it is detected
    as having been shared to a sub-process.

    """
    @event.listens_for(engine, 'connect')
    def connect(dbapi_connection, connection_record):
        """On connect to database event."""
        connection_record.info['pid'] = os.getpid()

    @event.listens_for(engine, 'checkout')
    def checkout(dbapi_connection, connection_record, connection_proxy):
        """On checkout event."""
        pid = os.getpid()
        if connection_record.info['pid'] != pid:
            connection_record.connection = connection_proxy.connection = None
            raise exc.DisconnectionError(
                'Connection record belongs to pid %s, '
                'attempting to check out in pid %s' %
                (connection_record.info['pid'], pid)
            )

    return engine


def dispose_engines():
    """Dispose engines to prevent connection sharing between parent and child processes.

    Should be called right after os.fork() or similar called

    """
    ENGINES['master'].dispose()
    for engine in ENGINES['slaves']:
        engine.dispose()


ENGINES = {
    'master': add_engine_pidguard(create_engine(
        settings.db.master.dsn,
        pool_size=settings.db.master.get('pool_size', DEFAULT_POOL_SIZE),
        max_overflow=settings.db.master.get('max_overflow', DEFAULT_MAX_OVERFLOW),
        json_deserializer=ujson.loads,
        json_serializer=ujson.dumps
    )),
    'slaves': [
        add_engine_pidguard(create_engine(
            slave['dsn'],
            pool_size=slave.get('pool_size', DEFAULT_POOL_SIZE),
            max_overflow=slave.get('max_overflow', DEFAULT_MAX_OVERFLOW),
            isolation_level='AUTOCOMMIT',
            json_deserializer=ujson.loads,
            json_serializer=ujson.dumps
        ))
        for slave in settings.db.get('slaves', [settings.db.master])
    ]
}
