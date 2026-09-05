from __future__ import annotations

from genesis_core.contracts import DomainDescriptor, RuleLoader


class ExampleDomainDescriptor(DomainDescriptor):
    def __init__(self, package: str, version: str) -> None:
        super().__init__(name="example", package=package, version=version)

    def get_rule_loader(self) -> RuleLoader:
        raise NotImplementedError("Implement the domain-specific RuleLoader")
