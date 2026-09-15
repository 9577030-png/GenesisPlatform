from __future__ import annotations

from collections.abc import Iterable

from genesis_core import Fact, RuleEngine, RuleEvaluation, load_domain

from .domain_resolver_registry import DomainResolverRegistry


class DomainRuntime:
    """Execute an installed Genesis domain through the Core rule engine."""

    def __init__(
        self,
        domain_name: str,
        resolver_registry: DomainResolverRegistry,
    ) -> None:
        self.domain_name = domain_name
        self.resolver_registry = resolver_registry
        self.descriptor = load_domain(domain_name)

    def evaluate(self, facts: Iterable[Fact]) -> tuple[RuleEvaluation, ...]:
        rule_set = self.descriptor.get_rule_loader().load()
        engine = RuleEngine()
        evaluations = engine.evaluate_matched(rule_set.rules, facts)
        resolver = self.resolver_registry.get(self.domain_name)
        return tuple(resolver.resolve(evaluations))
