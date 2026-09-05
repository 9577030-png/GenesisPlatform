from __future__ import annotations

from pathlib import Path

from genesis_core import DefaultRuleLoader
from genesis_core.contracts import DomainDescriptor, RuleLoader

from genesis_construction.parsers import ConstructionRuleParser
from genesis_construction.sources import YamlConstructionRuleSource


class ConstructionDomainDescriptor(DomainDescriptor):
    """Genesis Construction runtime domain descriptor."""

    def __init__(self, package: str, version: str, knowledge_path: Path) -> None:
        super().__init__(name="construction", package=package, version=version)
        self._knowledge_path = knowledge_path

    def get_rule_loader(self) -> RuleLoader:
        return DefaultRuleLoader(
            source=YamlConstructionRuleSource(self._knowledge_path / "rules"),
            parser=ConstructionRuleParser(),
        )
