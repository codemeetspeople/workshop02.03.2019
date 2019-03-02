import random

from sqlalchemy import event
from sqlalchemy.orm import Session

from db.engines import ENGINES


class ServerError(Exception):
    """Exception to represent database server error."""


class MasterSession(Session):
    """Master session to database."""

    def __init__(self, *args, **kwargs):
        """Initialize MasterSession instance."""
        self._after_commit_handlers = []

        super(MasterSession, self).__init__(*args, **kwargs)

        event.listen(MasterSession, 'after_commit', self._after_commit_hook)

    def on_commit(self, hook, *args, **kwargs):
        """Append post-commit hooks."""
        if not callable(hook):
            raise ServerError('hook should be callable')

        self._after_commit_handlers.append((hook, args, kwargs, ))

    def _after_commit_hook(self, session):
        """Append after-commit hooks."""
        for handler, args, kwargs in self._after_commit_handlers:
            handler(*args, **kwargs)

        self._after_commit_handlers.clear()


class SlaveSession(Session):
    """Slave session to database."""

    def flush(self, objects=None):
        """Clean session."""
        if not self._is_clean():
            raise ServerError('Use master_session instead of slave_session.')


class MasterSlaveSession:
    """Master-Slave session class."""

    def __new__(cls, engines=None, master=True, **kwargs):
        """Create MasterSlaveSession instance."""
        engines = engines or ENGINES

        if master:
            kwargs['bind'] = engines['master']
            return MasterSession(**kwargs)
        else:
            kwargs['bind'] = random.choice(engines['slaves'])
            return SlaveSession(**kwargs)
