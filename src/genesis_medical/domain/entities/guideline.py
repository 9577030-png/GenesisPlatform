from dataclasses import dataclass, field
from typing import Any


@dataclass
class SpecialtyGuideline:
    id: str
    scoring_rules: dict[str, float] = field(default_factory=dict)
    override_thresholds: dict[str, Any] = field(default_factory=dict)
    description: str | None = None
    condition: str = "any"
    recommendations: list[str] = field(default_factory=list)
    # Новое поле для условий диапазонов
    conditions: list[dict[str, Any]] = field(default_factory=list)
