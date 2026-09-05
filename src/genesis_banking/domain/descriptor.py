from __future__ import annotations

from pathlib import Path

from genesis_core import DefaultRuleLoader
from genesis_core.contracts import DomainDescriptor, RuleLoader

from genesis_banking.parsers import BankingRuleParser
from genesis_banking.sources import YamlBankingRuleSource


class BankingDomainDescriptor(DomainDescriptor):
    """Genesis Banking runtime domain descriptor."""

    def __init__(self, package: str, version: str, knowledge_path: Path) -> None:
        super().__init__(name="banking", package=package, version=version)
        self._knowledge_path = knowledge_path

    def get_rule_loader(self) -> RuleLoader:
        return DefaultRuleLoader(
            source=YamlBankingRuleSource(self._knowledge_path / "rules"),
            parser=BankingRuleParser(),
        )
