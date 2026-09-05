from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Sequence
from typing import Any

from ..evaluation import RuleEvaluation


class OutputAdapter(ABC):
    """Преобразует универсальные результаты Core в внешний формат."""

    @abstractmethod
    def format(
        self,
        evaluations: Sequence[RuleEvaluation],
    ) -> Any:
        raise NotImplementedError
