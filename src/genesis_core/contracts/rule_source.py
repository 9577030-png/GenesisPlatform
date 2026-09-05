from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterator
from typing import Any


class RuleSource(ABC):
    """Абстрактный источник сырых правил."""

    @abstractmethod
    def load_rules(self) -> Iterator[dict[str, Any]]:
        """Вернуть итератор сырых описаний правил."""
        raise NotImplementedError
