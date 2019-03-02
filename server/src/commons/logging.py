"""Logging filters module."""

import logging


class RequireDebugFalse(logging.Filter):
    """Filter for production."""

    def filter(self, record):
        """Return filtering result."""
        from config import settings
        return not settings.debug


class RequireDebugTrue(logging.Filter):
    """Filter for development."""

    def filter(self, record):
        """Return filtering result."""
        from config import settings
        return settings.debug


class LevelFilter(logging.Filter):
    """Logging level filter."""

    def __init__(self, low, high):
        """Initialize LevelFilter instance."""
        self._low = low
        self._high = high
        logging.Filter.__init__(self)

    def filter(self, record):
        """Return filtering result."""
        return self._low <= record.levelno <= self._high
