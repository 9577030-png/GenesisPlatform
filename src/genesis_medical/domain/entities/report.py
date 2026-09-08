from dataclasses import dataclass, field

from genesis_medical.domain.entities.finding import ClinicalFinding
from genesis_medical.domain.entities.recommendation import Recommendation


@dataclass(frozen=True)
class AnalysisReport:
    findings: list[ClinicalFinding] = field(default_factory=list)
    actions: list[Recommendation] = field(default_factory=list)
    explanation: str = ""
