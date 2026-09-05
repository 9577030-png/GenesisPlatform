from __future__ import annotations

from importlib.metadata import EntryPoint, entry_points

from .contracts.domain import DomainDescriptor

ENTRY_POINT_GROUP = "genesis.domains"


def discover_entry_points() -> tuple[EntryPoint, ...]:
    """Return raw registered Genesis domain entry points."""
    return tuple(entry_points(group=ENTRY_POINT_GROUP))


def list_domains() -> tuple[str, ...]:
    """Return all registered Genesis domain names in deterministic order."""
    return tuple(sorted(entry_point.name for entry_point in discover_entry_points()))


def discover_domains() -> tuple[DomainDescriptor, ...]:
    """Discover and load descriptors for all installed Genesis domains."""
    return tuple(
        _load_descriptor(entry_point)
        for entry_point in discover_entry_points()
    )


def load_domain(name: str) -> DomainDescriptor:
    """Load one registered domain by name.

    Raises:
        LookupError: when the requested domain is not installed.
    """
    if not isinstance(name, str) or not name.strip():
        raise ValueError("Genesis domain name cannot be empty")

    for entry_point in discover_entry_points():
        if entry_point.name == name:
            return _load_descriptor(entry_point)

    raise LookupError(f"Genesis domain is not installed: {name!r}")


def _load_descriptor(entry_point: EntryPoint) -> DomainDescriptor:
    descriptor_factory = entry_point.load()
    descriptor = descriptor_factory()

    if not isinstance(descriptor, DomainDescriptor):
        raise TypeError(
            f"Genesis domain entry point {entry_point.name!r} "
            "must return DomainDescriptor"
        )

    return descriptor
