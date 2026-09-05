from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from ..rule import Rule


class RuleParser(ABC):
    """Преобразует одно сырое описание в универсальный Rule."""

    @abstractmethod
    def parse(self, raw: dict[str, Any]) -> Rule:
        raise NotImplementedError
