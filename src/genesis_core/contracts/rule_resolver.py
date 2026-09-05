from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Sequence

from ..evaluation import RuleEvaluation


class RuleResolver(ABC):
    """Абстракция разрешения отношений между сработавшими правилами."""

    @abstractmethod
    def resolve(
        self,
        evaluations: Sequence[RuleEvaluation],
    ) -> Sequence[RuleEvaluation]:
        raise NotImplementedError
