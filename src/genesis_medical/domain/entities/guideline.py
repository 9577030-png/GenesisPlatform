from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List

@dataclass
class SpecialtyGuideline:
    id: str
    scoring_rules: Dict[str, float] = field(default_factory=dict)
    override_thresholds: Dict[str, Any] = field(default_factory=dict)
    description: Optional[str] = None
    condition: str = "any"
    recommendations: List[str] = field(default_factory=list)
    # Новое поле для условий диапазонов
    conditions: List[Dict[str, Any]] = field(default_factory=list)