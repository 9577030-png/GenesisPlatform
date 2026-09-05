from __future__ import annotations

from genesis_core.contracts.rule_loader import RuleLoader as RuleLoaderContract
from genesis_core.contracts.rule_parser import RuleParser
from genesis_core.contracts.rule_source import RuleSource
from genesis_core.rule_set import RuleSet


class DefaultRuleLoader(RuleLoaderContract):
    """Универсальный loader: Source -> Parser -> RuleSet."""

    def __init__(
        self,
        source: RuleSource,
        parser: RuleParser,
    ) -> None:
        self.source = source
        self.parser = parser

    def load(self) -> RuleSet:
        rules = tuple(
            self.parser.parse(raw)
            for raw in self.source.load_rules()
        )

        return RuleSet(rules)
