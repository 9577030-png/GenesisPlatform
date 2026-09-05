from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Fact:
    """
    Универсальный факт.

    Fact не зависит от предметной области.
    Значение может быть любым Python-объектом.
    """

    name: str
    value: Any
    unit: str | None = None

    def __post_init__(self) -> None:
        if not self.name:
            raise ValueError("Fact name cannot be empty")