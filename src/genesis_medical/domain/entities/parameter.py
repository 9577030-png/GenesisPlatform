from dataclasses import dataclass
from genesis_medical.domain.value_objects.unit import Unit
from genesis_medical.domain.exceptions import InvalidParameterError


@dataclass(frozen=True)
class Parameter:
    """Р›Р°Р±РѕСЂР°С‚РѕСЂРЅС‹Р№ РїР°СЂР°РјРµС‚СЂ (РЅР°Р·РІР°РЅРёРµ, Р·РЅР°С‡РµРЅРёРµ, РµРґРёРЅРёС†Р°)."""
    name: str
    value: float
    unit: Unit

    def __post_init__(self):
        if not self.name or not self.name.strip():
            raise InvalidParameterError("Parameter name cannot be empty")
        if self.value < 0:
            raise InvalidParameterError(f"Invalid parameter value: {self.value}. Value must be >= 0")
        if self.value > 10000:
            raise InvalidParameterError(f"Parameter value too high: {self.value}")
        if not isinstance(self.unit, Unit):
            raise InvalidParameterError("Unit must be an instance of Unit")
