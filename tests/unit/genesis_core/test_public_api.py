import inspect

import genesis_core
from genesis_core.api import API_VERSION


def test_public_api_exports_all_core_types():
    expected = {
        "API_VERSION",
        "__version__",
        "Condition",
        "DefaultRuleLoader",
        "DomainDescriptor",
        "Evidence",
        "Evaluator",
        "Fact",
        "OutputAdapter",
        "Rule",
        "RuleEngine",
        "RuleEvaluation",
        "RuleLoader",
        "RuleParser",
        "RuleResolver",
        "RuleSet",
        "RuleSource",
        "discover_domains",
        "list_domains",
        "load_domain",
    }

    assert set(genesis_core.__all__) == expected
    assert genesis_core.API_VERSION == API_VERSION == "1"

    for name in expected:
        assert hasattr(genesis_core, name)


def test_public_api_signatures_are_stable():
    assert list(inspect.signature(genesis_core.RuleEngine).parameters) == [
        "loader_or_evaluator",
        "resolver",
        "loader",
        "evaluator",
    ]

    assert list(inspect.signature(genesis_core.Evaluator.evaluate).parameters) == [
        "self",
        "rule",
        "facts",
    ]

    assert list(inspect.signature(genesis_core.RuleEngine.evaluate).parameters) == [
        "self",
        "rules_or_facts",
        "facts",
    ]

    assert list(inspect.signature(genesis_core.load_domain).parameters) == [
        "name",
    ]


def test_contract_types_are_public_for_domain_authors():
    from genesis_core import (
        DomainDescriptor,
        OutputAdapter,
        RuleLoader,
        RuleParser,
        RuleResolver,
        RuleSource,
    )

    assert DomainDescriptor is not None
    assert OutputAdapter is not None
    assert RuleLoader is not None
    assert RuleParser is not None
    assert RuleResolver is not None
    assert RuleSource is not None
