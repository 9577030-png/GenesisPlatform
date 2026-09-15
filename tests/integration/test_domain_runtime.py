from genesis_app.application.services.domain_resolver_registry import (
    DomainResolverRegistry,
)
from genesis_app.application.services.domain_runtime import DomainRuntime

from genesis_construction.resolvers import ConstructionRuleResolver
from genesis_core import Fact


def test_domain_runtime_executes_construction() -> None:
    registry = DomainResolverRegistry({"construction": ConstructionRuleResolver()})
    runtime = DomainRuntime("construction", registry)

    result = runtime.evaluate(
        (
            Fact("steel_capacity_kn", 120),
            Fact("applied_load_kn", 140),
        )
    )

    assert [item.rule_id for item in result] == ["steel_load_reject"]
    assert result[0].result == {
        "status": "review",
        "message": "applied load exceeds the demonstration capacity",
    }
