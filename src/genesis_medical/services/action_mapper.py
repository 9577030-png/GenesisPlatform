from __future__ import annotations

import logging
from collections.abc import Sequence
from typing import Protocol

from ..domain.entities.finding import ClinicalFinding
from ..domain.entities.recommendation import Recommendation

logger = logging.getLogger(__name__)


class RecommendationProvider(Protocol):
    def get_recommendation(self, finding_id: str) -> Recommendation | None: ...


class ActionMapper:
    """Map medical findings to domain recommendations."""

    def __init__(self, recommendation_provider: RecommendationProvider) -> None:
        self.recommendation_provider = recommendation_provider

    def map_to_actions(
        self,
        findings: Sequence[ClinicalFinding],
    ) -> list[Recommendation]:
        actions: list[Recommendation] = []
        for finding in findings:
            recommendation = self.recommendation_provider.get_recommendation(finding.id)
            if recommendation is not None:
                actions.append(recommendation)
            else:
                logger.warning("No recommendation found for finding %s", finding.id)
        return actions
