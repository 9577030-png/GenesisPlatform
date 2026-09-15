from __future__ import annotations

from genesis_core import RuleResolver


class DomainResolverRegistry:
    """Resolve domain names to application-level rule resolvers."""

    def __init__(self, resolvers: dict[str, RuleResolver]) -> None:
        self._resolvers = dict(resolvers)

    def get(self, domain_name: str) -> RuleResolver:
        try:
            return self._resolvers[domain_name]
        except KeyError as exc:
            raise ValueError(f"No resolver registered for domain: {domain_name}") from exc
