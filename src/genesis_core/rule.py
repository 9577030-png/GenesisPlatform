from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .condition import Condition


@dataclass(frozen=True)
class Rule:
    """
    Универсальное правило.

    Все conditions правила объединяются через AND.
    """

    id: str
    conditions: tuple[Condition, ...]
    result: Any = None

    version: str = "1"
    priority: int = 0

    conflicts_with: tuple[str, ...] = field(
        default_factory=tuple
    )
    supports: tuple[str, ...] = field(
        default_factory=tuple
    )

    def __post_init__(self) -> None:
        if not isinstance(self.id, str):
            raise TypeError("Rule id must be a string")

        if not self.id.strip():
            raise ValueError("Rule id cannot be empty")

        if not isinstance(self.conditions, tuple):
            raise TypeError(
                "Rule conditions must be a tuple"
            )

        if any(
            not isinstance(condition, Condition)
            for condition in self.conditions
        ):
            raise TypeError(
                "Rule conditions must contain only Condition objects"
            )

    @property
    def condition_count(self) -> int:
        return len(self.conditions)