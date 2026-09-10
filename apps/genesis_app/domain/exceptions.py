class RepositoryError(Exception):
    """Infrastructure repository failure in the application."""


class VersionNotFoundError(RepositoryError):
    """Requested rule version was not found in the application repository."""


class CacheError(Exception):
    """Application cache failure."""


class RenderError(Exception):
    """Application rendering failure."""
