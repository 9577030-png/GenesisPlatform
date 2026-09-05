from __future__ import annotations

from pathlib import Path

from genesis_core import DefaultRuleLoader
from genesis_core.contracts import DomainDescriptor, RuleLoader

from genesis_medical.parsers import MedicalRuleParser
from genesis_medical.sources import YamlMedicalRuleSource


class MedicalDomainDescriptor(DomainDescriptor):
    """Genesis Medical runtime domain descriptor."""

    def __init__(self, package: str, version: str, knowledge_path: Path) -> None:
        super().__init__(name="medical", package=package, version=version)
        self._knowledge_path = knowledge_path

    def get_rule_loader(self) -> RuleLoader:
        return DefaultRuleLoader(
            source=YamlMedicalRuleSource(self._knowledge_path / "guidelines"),
            parser=MedicalRuleParser(),
        )
