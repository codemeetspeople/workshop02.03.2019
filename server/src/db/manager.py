from contextlib import contextmanager

import structlog
import ujson
import asyncpg
import asyncpgsa
from asyncpgsa.connection import SAConnection
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.postgresql import psycopg2

from config import settings
from db.engines import ENGINES, DEFAULT_POOL_SIZE, DEFAULT_MAX_OVERFLOW
from db.sessions import MasterSlaveSession

logger = structlog.getLogger('daemon.' + __name__)

db_factory = sessionmaker(class_=MasterSlaveSession, engines=ENGINES, autoflush=True)
SET_APPLICATION_NAME = settings.db.get('set_application_name', True)

# asyncpgsa has default dialect that do not contain `on_conflic_*` statement
DEFAULT_DIALECT = psycopg2.dialect(
    json_serializer=ujson.dumps,
    json_deserializer=ujson.loads
)
DEFAULT_DIALECT.implicit_returning = True
DEFAULT_DIALECT.use_native_hstore = True


class ConnectionManager:
    """Database connection manager."""

    __slots__ = ('_connection_class', '_loop', '_dsn', '_connection', '_statement_cache_size')

    def __init__(self, loop=None, statement_cache_size=0):
        """Initialize ConnectionManager instance."""
        class SynctoolConnection(SAConnection):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, dialect=DEFAULT_DIALECT, **kwargs)

        self._connection_class = SynctoolConnection
        self._loop = loop

        self._dsn = settings.db.master['dsn']
        self._connection = None
        self._statement_cache_size = statement_cache_size

    def acquire(self):
        """Acquire connection within context."""
        return self

    async def __aenter__(self):
        """Return connection within async context."""
        self._connection = await asyncpg.connect(
            self._dsn,
            connection_class=self._connection_class,
            loop=self._loop,
            statement_cache_size=self._statement_cache_size
        )
        return self._connection

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit from context."""
        await self._connection.close()

    def __await__(self):
        """Initialize context."""
        return self.__aenter__().__await__()

    async def close(self):
        """Close connection."""
        if self._connection:
            await self._connection.close()


class SessionManager:
    """Synctool sessions manager class."""

    __slots__ = (
        '__master_session_instance',
        '__async_master_instance',
        '__open_masters',
    )

    def __init__(self):
        """Initialize SessionManager instance."""
        self.__master_session_instance = None
        self.__async_master_instance = None
        self.__open_masters = 0

    @property
    def __master_session(self):
        """Return master session."""
        if self.__master_session_instance is None:
            self.__master_session_instance = db_factory(
                master=True, autoflush=False, autocommit=False,
                expire_on_commit=False,
            )
        return self.__master_session_instance

    @contextmanager
    def master_session(self, autoflush=True):
        """Provide a transactional master database scope around a series of operations within context."""
        self.__open_masters += 1
        try:
            yield self.__master_session
            if self.__open_masters == 1:
                self.__master_session.commit()
            else:
                if autoflush:
                    self.__master_session.flush()
        except Exception as e:
            try:
                if self.__open_masters == 1:
                    self.__master_session.rollback()
            except Exception as inner_e:
                raise inner_e
            finally:
                raise e
        finally:
            self.__open_masters -= 1
            if not self.has_open_master:
                self.__master_session.close()

    def current_session(self):
        """Return opened master session or create one."""
        if self.has_open_master:
            return self.master_session()

        return self.master_session()

    @property
    def has_open_master(self):
        """Check for opened master sessions."""
        return self.__open_masters > 0

    def close_all(self):
        """Close master session."""
        if self.__master_session_instance is not None:
            self.__master_session_instance.close()

    async def async_master(self, loop=None):
        """Return async master session."""
        if self.__async_master_instance is None:
            master = settings.db.master
            self.__async_master_instance = await asyncpgsa.create_pool(
                master['dsn'],
                min_size=master.get('pool_size', DEFAULT_POOL_SIZE) - master.get('max_overflow', DEFAULT_MAX_OVERFLOW),
                max_size=master.get('pool_size', DEFAULT_POOL_SIZE) + master.get('max_overflow', DEFAULT_MAX_OVERFLOW),
                loop=loop,
                dialect=DEFAULT_DIALECT
            )

        return self.__async_master_instance

    async def async_close_master(self):
        """Close async master session."""
        if self.__async_master_instance is not None:
            await self.__async_master_instance.close()
            self.__async_master_instance = None

    async def async_close_all(self):
        """Close async master session."""
        await self.async_close_master()
