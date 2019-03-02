"""Synctool Admin decorators module."""


def register_view(group):
    """Register ModelView to group."""
    def wrapper(cls):
        """Check if ModelView in group and append it if not."""
        if cls.__name__ not in group:
            group[cls.__name__] = cls

        return cls

    return wrapper
