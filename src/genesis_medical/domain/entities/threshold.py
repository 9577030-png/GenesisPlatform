from dataclasses import dataclass

from genesis_medical.domain.exceptions import ConfigurationError
from genesis_medical.domain.value_objects.risk_level import RiskLevel
from genesis_medical.domain.value_objects.unit import Unit


@dataclass(frozen=True)
class Threshold:
    parameter_name: str
    low: float | None
    high: float | None
    unit: Unit
    risk_level: RiskLevel

    def __post_init__(self) -> None:
        if not self.parameter_name or not self.parameter_name.strip():
            raise ConfigurationError("Threshold parameter_name cannot be empty")
        if self.low is not None and self.high is not None and self.low >= self.high:
            raise ConfigurationError(
                f"Invalid threshold for {self.parameter_name}: low ({self.low}) >= high ({self.high})"
            )
        if not isinstance(self.unit, Unit):
            raise ConfigurationError("Unit must be an instance of Unit")
        if not isinstance(self.risk_level, RiskLevel):
            raise ConfigurationError("risk_level must be an instance of RiskLevel")
