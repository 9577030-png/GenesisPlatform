from __future__ import annotations

from importlib.resources import files
from typing import Any

import yaml


class PhysiologicalValidator:
    """Validate medical parameters against bundled physiological ranges."""

    def __init__(self, config_path: str | None = None) -> None:
        if config_path is None:
            resource = files("genesis_medical").joinpath(
                "knowledge", "configs", "physiological_ranges.yaml"
            )
            with resource.open("r", encoding="utf-8") as handle:
                data = yaml.safe_load(handle) or {}
        else:
            with open(config_path, "r", encoding="utf-8") as handle:
                data = yaml.safe_load(handle) or {}
        self.ranges = data.get("physiological_ranges", {})

    def validate(self, parameters: list[dict[str, Any]]) -> list[str]:
        errors: list[str] = []
        for parameter in parameters:
            name = parameter.get("name")
            value = parameter.get("value")
            if name not in self.ranges:
                continue
            lo, hi = self.ranges[name]
            if not (lo <= value <= hi):
                errors.append(
                    f"Parameter {name} value {value} outside physiological range [{lo}, {hi}]"
                )
        return errors
