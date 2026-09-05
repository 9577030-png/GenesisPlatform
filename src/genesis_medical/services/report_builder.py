from __future__ import annotations

import logging
from collections.abc import Sequence

from ..domain.entities.finding import ClinicalFinding
from ..domain.entities.recommendation import Recommendation
from ..domain.entities.report import AnalysisReport
from .explanation_builder import build_explanation

logger = logging.getLogger(__name__)


class ReportBuilder:
    """Build a medical AnalysisReport from findings and recommendations."""

    def build(
        self,
        findings: Sequence[ClinicalFinding],
        actions: Sequence[Recommendation],
    ) -> AnalysisReport:
        return AnalysisReport(
            findings=list(findings),
            actions=list(actions),
            explanation=build_explanation(findings),
        )
