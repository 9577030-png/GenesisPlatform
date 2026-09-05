from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass

from .rule import Rule


@dataclass(frozen=True)
class RuleSet:
    """
    Неизменяемый набор универсальных правил.

    RuleSet гарантирует:
    - все элементы являются Rule;
    - идентификаторы правил уникальны;
    - порядок правил сохраняется;
    - правила доступны по идентификатору.
    """

    rules: tuple[Rule, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.rules, tuple):
            raise TypeError(
                "RuleSet rules must be a tuple"
            )

        if any(
            not isinstance(rule, Rule)
            for rule in self.rules
        ):
            raise TypeError(
                "RuleSet rules must contain only Rule objects"
            )

        rule_ids = [rule.id for rule in self.rules]

        if len(rule_ids) != len(set(rule_ids)):
            raise ValueError(
                "RuleSet rule ids must be unique"
            )

    def __iter__(self) -> Iterator[Rule]:
        return iter(self.rules)

    def __len__(self) -> int:
        return len(self.rules)

    def get(self, rule_id: str) -> Rule | None:
        for rule in self.rules:
            if rule.id == rule_id:
                return rule

        return None

    def require(self, rule_id: str) -> Rule:
        rule = self.get(rule_id)

        if rule is None:
            raise KeyError(
                f"Rule not found: {rule_id!r}"
            )

        return rule