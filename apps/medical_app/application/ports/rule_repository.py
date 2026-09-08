from __future__ import annotations

from abc import ABC, abstractmethod

from genesis_medical.domain.rule_version import RuleVersion


class RuleRepository(ABC):
    @abstractmethod
    def save(
        self,
        rule_version: RuleVersion,
    ) -> RuleVersion:
        pass

    @abstractmethod
    def get_active_versions(
        self,
    ) -> list[RuleVersion]:
        pass

    @abstractmethod
    def get_by_id(
        self,
        rule_id: str,
        version_id: int | None = None,
    ) -> RuleVersion | None:
        pass

    @abstractmethod
    def activate_version(
        self,
        rule_id: str,
        version_id: int,
    ) -> None:
        pass

    @abstractmethod
    def get_version_history(
        self,
        rule_id: str,
    ) -> list[RuleVersion]:
        pass
