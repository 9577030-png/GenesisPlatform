from genesis_app.application.services.domain_resolver_registry import (
    DomainResolverRegistry,
)

from genesis_construction.resolvers import ConstructionRuleResolver


def test_registry_returns_registered_resolver() -> None:
    resolver = ConstructionRuleResolver()
    registry = DomainResolverRegistry({"construction": resolver})

    assert registry.get("construction") is resolver


def test_registry_rejects_unknown_domain() -> None:
    registry = DomainResolverRegistry({})

    try:
        registry.get("construction")
    except ValueError as exc:
        assert str(exc) == "No resolver registered for domain: construction"
    else:
        raise AssertionError("Expected ValueError")
