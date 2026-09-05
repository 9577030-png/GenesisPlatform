from __future__ import annotations

from collections.abc import Sequence

from genesis_core import RuleEvaluation
from genesis_core.contracts import RuleResolver


class ConstructionRuleResolver(RuleResolver):
    """Keeps the highest-priority evaluation among directly conflicting rules."""

    def resolve(
        self,
        evaluations: Sequence[RuleEvaluation],
    ) -> Sequence[RuleEvaluation]:
        matched = sorted(
            (item for item in evaluations if item.matched),
            key=lambda item: item.priority,
            reverse=True,
        )
        kept: list[RuleEvaluation] = []
        for item in matched:
            if any(
                item.rule_id in existing.conflicts_with
                or existing.rule_id in item.conflicts_with
                for existing in kept
            ):
                continue
            kept.append(item)
        return tuple(kept)
