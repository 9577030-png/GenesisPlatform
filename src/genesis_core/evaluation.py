from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Evidence:
    """
    Результат проверки одного условия.
    """

    fact: str
    actual: Any
    operator: str
    expected: Any
    matched: bool


@dataclass(frozen=True)
class RuleEvaluation:
    """
    Результат выполнения одного правила.

    Evidence содержит детальное объяснение
    результата проверки каждого условия.
    """

    rule_id: str
    matched: bool
    evidence: tuple[Evidence, ...]
    result: Any = None
    priority: int = 0
    version: str = "1"
    conflicts_with: tuple[str, ...] = ()
    supports: tuple[str, ...] = ()
