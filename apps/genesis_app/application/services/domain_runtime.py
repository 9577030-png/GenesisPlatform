from __future__ import annotations

from collections.abc import Iterable

from genesis_core import Fact, RuleEngine, RuleEvaluation, RuleResolver, load_domain


class DomainRuntime:
    """Execute an installed Genesis domain through the Core rule engine."""

    def __init__(self, domain_name: str, resolver: RuleResolver) -> None:
        self.domain_name = domain_name
        self.resolver = resolver
        self.descriptor = load_domain(domain_name)

    def evaluate(self, facts: Iterable[Fact]) -> tuple[RuleEvaluation, ...]:
        rule_set = self.descriptor.get_rule_loader().load()
        engine = RuleEngine()
        evaluations = engine.evaluate_matched(rule_set.rules, facts)
        return tuple(self.resolver.resolve(evaluations))
