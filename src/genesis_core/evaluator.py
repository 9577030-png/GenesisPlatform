from __future__ import annotations

from typing import Any, Iterable

from .condition import Condition
from .evaluation import Evidence, RuleEvaluation
from .fact import Fact
from .rule import Rule


class Evaluator:
    """
    Выполняет одно универсальное Rule
    относительно набора Fact.
    """

    def evaluate(
        self,
        rule: Rule,
        facts: Iterable[Fact],
    ) -> RuleEvaluation:
        fact_map = self._build_fact_map(facts)

        evidence = tuple(
            self._evaluate_condition(
                condition,
                fact_map,
            )
            for condition in rule.conditions
        )

        matched = all(
            item.matched
            for item in evidence
        )

        return RuleEvaluation(
            rule_id=rule.id,
            matched=matched,
            evidence=evidence,
            result=rule.result,
            priority=rule.priority,
            version=rule.version,
            conflicts_with=rule.conflicts_with,
            supports=rule.supports,
        )

    @staticmethod
    def _build_fact_map(
        facts: Iterable[Fact],
    ) -> dict[str, Any]:
        fact_map: dict[str, Any] = {}

        for fact in facts:
            if fact.name in fact_map:
                raise ValueError(
                    f"Duplicate fact name: {fact.name!r}"
                )

            fact_map[fact.name] = fact.value

        return fact_map

    def _evaluate_condition(
        self,
        condition: Condition,
        facts: dict[str, Any],
    ) -> Evidence:
        if condition.fact not in facts:
            return Evidence(
                fact=condition.fact,
                actual=None,
                operator=condition.operator,
                expected=condition.value,
                matched=False,
            )

        actual = facts[condition.fact]

        matched = self._compare(
            actual,
            condition.operator,
            condition.value,
        )

        return Evidence(
            fact=condition.fact,
            actual=actual,
            operator=condition.operator,
            expected=condition.value,
            matched=matched,
        )

    @staticmethod
    def _compare(
        actual: Any,
        operator: str,
        expected: Any,
    ) -> bool:
        if operator == "==":
            return actual == expected

        if operator == "!=":
            return actual != expected

        if operator == ">":
            return actual > expected

        if operator == ">=":
            return actual >= expected

        if operator == "<":
            return actual < expected

        if operator == "<=":
            return actual <= expected

        if operator == "in":
            try:
                return actual in expected
            except TypeError:
                raise TypeError(
                    "'in' expects a membership-compatible value"
                ) from None

        if operator == "not_in":
            try:
                return actual not in expected
            except TypeError:
                raise TypeError(
                    "'not_in' expects a membership-compatible value"
                ) from None

        if operator == "between":
            if not isinstance(expected, (tuple, list)):
                raise TypeError(
                    "'between' expects exactly two values"
                )

            if len(expected) != 2:
                raise ValueError(
                    "'between' expects exactly two values"
                )

            minimum, maximum = expected
            return minimum <= actual <= maximum

        raise ValueError(
            f"Unsupported operator: {operator!r}"
        )