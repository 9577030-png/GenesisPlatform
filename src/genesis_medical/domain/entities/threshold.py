from dataclasses import dataclass
from typing import Optional
from genesis_medical.domain.value_objects.unit import Unit
from genesis_medical.domain.value_objects.risk_level import RiskLevel
from genesis_medical.domain.exceptions import ConfigurationError


@dataclass(frozen=True)
class Threshold:
    parameter_name: str
    low: Optional[float]
    high: Optional[float]
    unit: Unit
    risk_level: RiskLevel

    def __post_init__(self):
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
