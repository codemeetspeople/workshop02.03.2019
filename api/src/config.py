"""Synctool configurations module."""

import os
import lya
import warnings
from contextlib import contextmanager
from copy import deepcopy
from logging import config as logging_config
from structlog import configure as configure_structlog
from structlog.stdlib import LoggerFactory
from pathlib import Path

from alembic.config import Config


PROJECT_DIR = Path(__file__).parent.as_posix()
LOCAL_SETTINGS_FILENAME = os.environ.get('PROJECT_CONFIG', 'settings.local.yaml')

settings_default = Path(PROJECT_DIR, 'configs', 'settings.default.yaml')
settings_local = Path(PROJECT_DIR, 'configs', LOCAL_SETTINGS_FILENAME)


class SettingsFileNotFound(Exception):
    """Exception to handle missed settings file."""


class SettingNotDefinedError(Exception):
    """Exception to handle missed setting."""


class SettingsError(Exception):
    """Settings specific exception."""


class BaseSettings:
    """Synctool Settings base class."""

    __slots__ = ('_settings', )

    @contextmanager
    def override(self, options):
        """Override setting within context.

        with settings.override(foo='test', bar=42):
            <new settings here>
        <old settings here>

        """
        self._load_settings()

        old_settings = deepcopy(self._settings)
        self._settings.update_dict(lya.AttrDict(options))

        try:
            yield
        finally:
            self._settings = old_settings

    def __getattr__(self, key):
        """Return setting value.

        :param key: setting title
        :type key: str

        """
        self._load_settings()

        try:
            return self._settings.__getattr__(key)
        except KeyError:
            raise SettingNotDefinedError('Setting {} is not defined'.format(key))

    def __contains__(self, item):
        """Check if setting exists.

        :param item: setting title
        :type type: str

        """
        self._load_settings()

        return item in self._settings

    def _load_settings(self):
        """Load settings. Can be implemented in child classes."""


class Settings(BaseSettings):
    """Settings class."""

    def __init__(self):
        """Initialize Settings instance."""
        self._settings = lya.AttrDict.from_yaml(settings_default.as_posix())
        if settings_local.exists():
            self._settings.update_yaml(settings_local.as_posix())


#: step 1 - create settings object
settings = Settings()

#: step 2 - configure alembic
alembic_cfg = Config()
alembic_cfg.set_main_option('script_location', Path(PROJECT_DIR, 'db', 'migrations').as_posix())
alembic_cfg.set_main_option('url', settings.db.master.dsn)


def configure_logging():
    """Configure logging."""
    if 'logging' not in settings:
        warnings.warn('Logging is not configured. Add logging setting to fix it.')
        return

    if 'logging_dir' in settings and settings.logging_dir:
        logging_dir = settings.logging_dir
        for _, handler in settings.logging.handlers.items():
            if 'filename' not in handler:
                continue
            handler.filename = Path(logging_dir, handler.filename).as_posix()

    logging_config.dictConfig(settings.logging)
    configure_structlog(logger_factory=LoggerFactory())


#: step 3 - configure logging
configure_logging()


def configure_db(settings):
    """Configure database."""
    if 'slaves' in settings.db:
        return

    pool_size = 50
    max_overflow = 49

    settings.db['slaves'] = [lya.AttrDict({
        'dsn': settings.db.master['dsn'],
        'pool_size': pool_size,
        'max_overflow': max_overflow
    })]


#: step 4 - configure database
configure_db(settings)
