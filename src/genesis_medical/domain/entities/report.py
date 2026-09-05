from dataclasses import dataclass, field
from typing import List
from genesis_medical.domain.entities.finding import ClinicalFinding
from genesis_medical.domain.entities.recommendation import Recommendation

@dataclass(frozen=True)
class AnalysisReport:
    findings: List[ClinicalFinding] = field(default_factory=list)
    actions: List[Recommendation] = field(default_factory=list)
    explanation: str = ""
