from dataclasses import dataclass, field

from genesis_medical.domain.value_objects.severity import Severity


@dataclass(frozen=True)
class Recommendation:
    doctor_specialty: str
    urgency: Severity
    additional_tests: list[str] = field(default_factory=list)
