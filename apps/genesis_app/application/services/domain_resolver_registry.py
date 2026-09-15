from __future__ import annotations

from importlib.metadata import EntryPoint, entry_points

from genesis_core import RuleResolver

ENTRY_POINT_GROUP = "genesis.app.resolvers"


class DomainResolverRegistry:
    """Resolve domain names to application-level rule resolvers."""

    def __init__(self, resolvers: dict[str, RuleResolver]) -> None:
        self._resolvers = dict(resolvers)

    def get(self, domain_name: str) -> RuleResolver:
        try:
            return self._resolvers[domain_name]
        except KeyError as exc:
            raise ValueError(f"No resolver registered for domain: {domain_name}") from exc


def discover_domain_resolvers() -> dict[str, RuleResolver]:
    """Discover and instantiate all installed domain rule resolvers."""
    return {
        entry_point.name: _load_resolver(entry_point) for entry_point in _discover_entry_points()
    }


def _discover_entry_points() -> tuple[EntryPoint, ...]:
    return tuple(entry_points(group=ENTRY_POINT_GROUP))


def _load_resolver(entry_point: EntryPoint) -> RuleResolver:
    resolver_factory = entry_point.load()
    resolver = resolver_factory()

    if not isinstance(resolver, RuleResolver):
        raise TypeError(
            f"Genesis domain resolver entry point {entry_point.name!r} must return RuleResolver"
        )

    return resolver
