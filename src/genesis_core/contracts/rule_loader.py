from __future__ import annotations

from abc import ABC, abstractmethod

from ..rule_set import RuleSet


class RuleLoader(ABC):
    """Абстракция загрузки готового RuleSet."""

    @abstractmethod
    def load(self) -> RuleSet:
        raise NotImplementedError
