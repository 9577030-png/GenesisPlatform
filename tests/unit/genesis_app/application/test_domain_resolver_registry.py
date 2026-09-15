import sys
import types
from collections.abc import Sequence
from importlib.metadata import EntryPoint

import pytest
from genesis_app.application.services.domain_resolver_registry import (
    DomainResolverRegistry,
    discover_domain_resolvers,
)

from genesis_core import RuleEvaluation, RuleResolver


class FakeResolver(RuleResolver):
    def resolve(
        self,
        evaluations: Sequence[RuleEvaluation],
    ) -> Sequence[RuleEvaluation]:
        return evaluations


def test_registry_returns_registered_resolver() -> None:
    resolver = FakeResolver()
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


def test_discover_domain_resolvers_loads_registered_resolver(monkeypatch) -> None:
    helper = types.ModuleType("genesis_app.domain_resolver_registry_test_helpers")
    helper.resolver = FakeResolver
    monkeypatch.setitem(sys.modules, helper.__name__, helper)

    points = (
        EntryPoint(
            "construction",
            "genesis_app.domain_resolver_registry_test_helpers:resolver",
            "genesis.app.resolvers",
        ),
    )

    monkeypatch.setattr(
        "genesis_app.application.services.domain_resolver_registry.entry_points",
        lambda group: points,
    )

    discovered = discover_domain_resolvers()

    assert tuple(discovered) == ("construction",)
    assert isinstance(discovered["construction"], FakeResolver)


def test_discover_domain_resolvers_rejects_invalid_resolver(monkeypatch) -> None:
    helper = types.ModuleType("genesis_app.domain_resolver_registry_invalid_helpers")
    helper.resolver = lambda: object()
    monkeypatch.setitem(sys.modules, helper.__name__, helper)

    points = (
        EntryPoint(
            "construction",
            "genesis_app.domain_resolver_registry_invalid_helpers:resolver",
            "genesis.app.resolvers",
        ),
    )

    monkeypatch.setattr(
        "genesis_app.application.services.domain_resolver_registry.entry_points",
        lambda group: points,
    )

    with pytest.raises(TypeError, match="must return RuleResolver"):
        discover_domain_resolvers()
