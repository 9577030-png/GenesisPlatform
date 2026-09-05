from __future__ import annotations

from collections.abc import Iterable, Sequence
from typing import overload

from .contracts.rule_loader import RuleLoader as RuleLoaderContract
from .contracts.rule_resolver import RuleResolver
from .evaluation import RuleEvaluation
from .evaluator import Evaluator
from .fact import Fact
from .rule import Rule


class RuleEngine:
    """Универсальный исполнитель правил с опциональными DI-контрактами."""

    def __init__(
        self,
        loader_or_evaluator: RuleLoaderContract | Evaluator | None = None,
        resolver: RuleResolver | None = None,
        *,
        loader: RuleLoaderContract | None = None,
        evaluator: Evaluator | None = None,
    ) -> None:
        """
        Создать движок.

        Поддерживаются две формы совместимости:

        - RuleEngine(evaluator)
        - RuleEngine(loader, resolver)
        - RuleEngine(loader=..., resolver=..., evaluator=...)
        """
        if loader_or_evaluator is not None:
            if isinstance(loader_or_evaluator, Evaluator):
                if evaluator is not None:
                    raise TypeError(
                        "Evaluator provided both positionally and by keyword"
                    )
                evaluator = loader_or_evaluator
            else:
                if loader is not None:
                    raise TypeError(
                        "Loader provided both positionally and by keyword"
                    )
                loader = loader_or_evaluator

        self.evaluator = evaluator or Evaluator()
        self.loader = loader
        self.resolver = resolver

    @overload
    def evaluate(
        self,
        rules: Iterable[Rule],
        facts: Iterable[Fact],
    ) -> tuple[RuleEvaluation, ...]: ...

    @overload
    def evaluate(
        self,
        facts: Iterable[Fact],
    ) -> tuple[RuleEvaluation, ...]: ...

    def evaluate(
        self,
        rules_or_facts: Iterable[Rule] | Iterable[Fact],
        facts: Iterable[Fact] | None = None,
    ) -> tuple[RuleEvaluation, ...]:
        if facts is None:
            if self.loader is None:
                raise ValueError(
                    "RuleEngine requires loader when facts are passed alone"
                )

            rule_source = self.loader.load()
            rules = rule_source.rules
            fact_values = tuple(rules_or_facts)  # type: ignore[arg-type]
        else:
            rules = tuple(rules_or_facts)  # type: ignore[arg-type]
            fact_values = tuple(facts)

        evaluations = tuple(
            self.evaluator.evaluate(
                rule,
                fact_values,
            )
            for rule in rules
        )

        return self._resolve(evaluations)

    def evaluate_matched(
        self,
        rules: Iterable[Rule],
        facts: Iterable[Fact],
    ) -> tuple[RuleEvaluation, ...]:
        return tuple(
            evaluation
            for evaluation in self.evaluate(
                rules,
                facts,
            )
            if evaluation.matched
        )

    def evaluate_loaded(
        self,
        facts: Iterable[Fact],
    ) -> tuple[RuleEvaluation, ...]:
        """Явный вариант запуска через сконфигурированный loader."""
        return self.evaluate(facts)

    def _resolve(
        self,
        evaluations: Sequence[RuleEvaluation],
    ) -> tuple[RuleEvaluation, ...]:
        if self.resolver is None:
            return tuple(evaluations)

        resolved = self.resolver.resolve(evaluations)
        return tuple(resolved)
