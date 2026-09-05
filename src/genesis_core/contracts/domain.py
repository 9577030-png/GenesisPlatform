from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .rule_loader import RuleLoader


@dataclass(frozen=True)
class DomainDescriptor(ABC):
    """Strict runtime contract exposed by an installed Genesis domain."""

    name: str
    package: str
    version: str

    @abstractmethod
    def get_rule_loader(self) -> "RuleLoader":
        """Return the domain's configured rule loader."""
        raise NotImplementedError
