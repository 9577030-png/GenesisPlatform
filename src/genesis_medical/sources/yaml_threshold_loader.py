from __future__ import annotations

from importlib.resources import files
from typing import Dict, Optional

import yaml

from ..domain.entities.threshold import Threshold
from ..domain.value_objects.gender import Gender
from ..domain.value_objects.risk_level import RiskLevel
from ..domain.value_objects.unit import Unit


class YamlThresholdLoader:
    """Load medical thresholds from bundled YAML knowledge or an explicit file."""

    def __init__(self, config_path: str | None = None) -> None:
        self.config_path = config_path
        self._loaded = False
        self._male_thresholds: Dict[str, Threshold] = {}
        self._female_thresholds: Dict[str, Threshold] = {}

    def _default_path(self):
        return files("genesis_medical").joinpath("knowledge", "configs", "clinical_thresholds.yaml")

    def _load(self) -> None:
        resource = open(self.config_path, "r", encoding="utf-8") if self.config_path else self._default_path().open("r", encoding="utf-8")
        try:
            data = yaml.safe_load(resource) or {}
        finally:
            resource.close()
        for name, params in data.get("thresholds", {}).items():
            unit = Unit(params.get("unit", ""))
            risk_level = getattr(RiskLevel, params.get("risk_level", "HIGH"), RiskLevel.HIGH)
            if "male" in params and "female" in params:
                male, female = params["male"], params["female"]
                self._male_thresholds[name] = Threshold(name, male.get("low"), male.get("high"), unit, risk_level)
                self._female_thresholds[name] = Threshold(name, female.get("low"), female.get("high"), unit, risk_level)
            else:
                threshold = Threshold(name, params.get("low"), params.get("high"), unit, risk_level)
                self._male_thresholds[name] = threshold
                self._female_thresholds[name] = threshold
        self._loaded = True

    def get_global_thresholds(self) -> Dict[str, Threshold]:
        if not self._loaded:
            self._load()
        return dict(self._male_thresholds)

    def get_threshold(self, parameter: str, gender: Gender) -> Optional[Threshold]:
        if not self._loaded:
            self._load()
        if gender == Gender.FEMALE:
            return self._female_thresholds.get(parameter)
        return self._male_thresholds.get(parameter)

    def reload(self) -> None:
        self._loaded = False
        self._male_thresholds.clear()
        self._female_thresholds.clear()
        self._load()
