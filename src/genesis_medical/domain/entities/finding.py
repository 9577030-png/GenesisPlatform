from dataclasses import dataclass, field
from typing import List, Optional
from genesis_medical.domain.value_objects.risk_level import RiskLevel

@dataclass(frozen=True)
class ClinicalFinding:
    id: str
    title: str
    probability: float
    risk: RiskLevel
    doctor_specialty: Optional[str] = None
    tests: List[str] = field(default_factory=list)
    evidence: List[str] = field(default_factory=list)
    excluded_by: List[str] = field(default_factory=list)
    description: Optional[str] = None
