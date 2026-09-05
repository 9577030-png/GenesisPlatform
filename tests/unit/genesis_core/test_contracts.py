from collections.abc import Iterator

import pytest

from genesis_core import (
    Condition,
    Fact,
    Rule,
    RuleEngine,
    DefaultRuleLoader,
    RuleSet,
)
from genesis_core.contracts import (
    OutputAdapter,
    RuleLoader as RuleLoaderContract,
    RuleParser,
    RuleResolver,
    RuleSource,
)


class InMemorySource(RuleSource):
    def load_rules(self) -> Iterator[dict]:
        yield {
            "id": "high_value",
            "value": 10,
        }


class SimpleParser(RuleParser):
    def parse(self, raw: dict) -> Rule:
        return Rule(
            id=raw["id"],
            conditions=(
                Condition(
                    fact="value",
                    operator=">",
                    value=raw["value"],
                ),
            ),
            result="MATCH",
        )


class IdentityResolver(RuleResolver):
    def resolve(self, evaluations):
        return evaluations


class ListOutput(OutputAdapter):
    def format(self, evaluations):
        return list(evaluations)


def test_contracts_are_abstract():
    with pytest.raises(TypeError):
        RuleSource()

    with pytest.raises(TypeError):
        RuleParser()

    with pytest.raises(TypeError):
        RuleLoaderContract()

    with pytest.raises(TypeError):
        RuleResolver()

    with pytest.raises(TypeError):
        OutputAdapter()


def test_rule_loader_builds_ruleset_from_source_and_parser():
    loader = DefaultRuleLoader(InMemorySource(), SimpleParser())

    result = loader.load()

    assert isinstance(result, RuleSet)
    assert len(result) == 1
    assert result.require("high_value").conditions[0].value == 10


def test_rule_engine_can_use_loader_and_resolver():
    loader = DefaultRuleLoader(InMemorySource(), SimpleParser())
    engine = RuleEngine(
        loader,
        IdentityResolver(),
    )

    result = engine.evaluate_loaded(
        (Fact("value", 20),),
    )

    assert len(result) == 1
    assert result[0].matched is True
    assert result[0].result == "MATCH"


def test_domain_descriptor_requires_rule_loader():
    from genesis_core import DomainDescriptor

    with pytest.raises(TypeError):
        DomainDescriptor("example", "example", "0.1.0")
