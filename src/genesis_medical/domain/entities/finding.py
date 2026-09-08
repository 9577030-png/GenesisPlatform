from dataclasses import dataclass, field

from genesis_medical.domain.value_objects.risk_level import RiskLevel


@dataclass(frozen=True)
class ClinicalFinding:
    id: str
    title: str
    probability: float
    risk: RiskLevel
    doctor_specialty: str | None = None
    tests: list[str] = field(default_factory=list)
    evidence: list[str] = field(default_factory=list)
    excluded_by: list[str] = field(default_factory=list)
    description: str | None = None
