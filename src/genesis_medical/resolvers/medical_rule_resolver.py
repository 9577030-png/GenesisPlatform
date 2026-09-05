from __future__ import annotations

from collections.abc import Sequence

from genesis_core import RuleEvaluation
from genesis_core.contracts import RuleResolver


class MedicalRuleResolver(RuleResolver):
    """Разрешает прямые конфликты с учётом priority в Core evaluations."""

    def resolve(
        self,
        evaluations: Sequence[RuleEvaluation],
    ) -> Sequence[RuleEvaluation]:
        matched = [evaluation for evaluation in evaluations if evaluation.matched]
        ordered = sorted(matched, key=lambda item: item.priority, reverse=True)

        kept: list[RuleEvaluation] = []
        for evaluation in ordered:
            if any(
                evaluation.rule_id in existing.conflicts_with
                or existing.rule_id in evaluation.conflicts_with
                for existing in kept
            ):
                continue
            kept.append(evaluation)

        return tuple(kept)
