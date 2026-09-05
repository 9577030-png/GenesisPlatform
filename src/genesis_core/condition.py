from __future__ import annotations

from dataclasses import dataclass
from typing import Any


SUPPORTED_OPERATORS = frozenset(
    {
        "==",
        "!=",
        "<",
        "<=",
        ">",
        ">=",
        "in",
        "not_in",
        "between",
    }
)


@dataclass(frozen=True)
class Condition:
    """
    Универсальное условие rule engine.

    Пример:

        Condition(
            fact="temperature",
            operator=">",
            value=90,
        )
    """

    fact: str
    operator: str
    value: Any

    def __post_init__(self) -> None:
        if not self.fact:
            raise ValueError("Condition fact cannot be empty")

        if self.operator not in SUPPORTED_OPERATORS:
            raise ValueError(
                f"Unsupported operator: {self.operator!r}"
            )