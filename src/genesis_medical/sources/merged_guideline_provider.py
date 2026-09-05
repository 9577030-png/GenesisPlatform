from __future__ import annotations

from pathlib import Path
from typing import List
from importlib.resources import files

import yaml

from ..domain.entities.guideline import SpecialtyGuideline


class MergedGuidelineProvider:
    """Load and normalize medical guideline YAML files."""

    def __init__(self, threshold_provider: object | None = None, guidelines_dir: str | None = None):
        self.threshold_provider = threshold_provider
        self.guidelines_dir = guidelines_dir
        self._guidelines: list[SpecialtyGuideline] | None = None

    def _default_directory(self) -> Path:
        return Path(str(files("genesis_medical").joinpath("knowledge", "guidelines")))

    def _load_guidelines(self) -> List[SpecialtyGuideline]:
        guidelines_dir = Path(self.guidelines_dir) if self.guidelines_dir else self._default_directory()
        result: list[SpecialtyGuideline] = []
        for path in sorted(guidelines_dir.rglob("*.yaml")):
            with path.open("r", encoding="utf-8") as handle:
                data = yaml.safe_load(handle) or {}
            if not data:
                continue

            if "conditions" in data:
                result.append(
                    SpecialtyGuideline(
                        id=data.get("id", path.stem),
                        description=data.get("description"),
                        recommendations=data.get("recommendations", []),
                        conditions=data["conditions"],
                    )
                )
                continue

            scoring_rules: dict[str, float] = {}
            override_thresholds: dict[str, dict] = {}
            if "thresholds" in data:
                for param, condition in data["thresholds"].items():
                    scoring_rules[param] = 5
                    overrides = {}
                    if "min" in condition:
                        overrides["high"] = condition["min"]
                    if "max" in condition:
                        overrides["low"] = condition["max"]
                    if overrides:
                        override_thresholds[param] = overrides
            else:
                scoring_rules = data.get("scoring", {})
                override_thresholds = data.get("override_thresholds", {})

            result.append(
                SpecialtyGuideline(
                    id=data.get("id", path.stem),
                    scoring_rules=scoring_rules,
                    override_thresholds=override_thresholds,
                    description=data.get("description"),
                    condition=data.get("condition", "any"),
                    recommendations=data.get("recommendations", []),
                )
            )
        return result

    def get_all(self) -> List[SpecialtyGuideline]:
        if self._guidelines is None:
            self._guidelines = self._load_guidelines()
        return list(self._guidelines)

    def reload(self) -> None:
        self._guidelines = self._load_guidelines()
