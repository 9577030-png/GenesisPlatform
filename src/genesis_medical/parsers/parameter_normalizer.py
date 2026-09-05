from __future__ import annotations

from typing import Dict, Tuple
from importlib.resources import files

import yaml

from ..domain.exceptions import InvalidParameterError
from ..domain.value_objects.unit import Unit
from .unit_converter import convert


class ParameterNormalizer:
    """Normalize medical parameter names and units using bundled knowledge."""

    def __init__(self) -> None:
        self._aliases = self._load_aliases()
        self._units = self._load_units()

    @staticmethod
    def _load_yaml(relative_path: str) -> dict:
        resource = files("genesis_medical").joinpath("knowledge", relative_path)
        with resource.open("r", encoding="utf-8") as handle:
            return yaml.safe_load(handle) or {}

    def _load_aliases(self) -> Dict[str, str]:
        data = self._load_yaml("laboratory/aliases.yaml")
        return {
            synonym.lower(): canonical
            for canonical, synonyms in data.get("aliases", {}).items()
            for synonym in synonyms
        }

    def _load_units(self) -> Dict[str, Dict]:
        return self._load_yaml("laboratory/units.yaml").get("units", {})

    def normalize(
        self,
        raw_name: str,
        raw_value: float,
        raw_unit: str,
    ) -> Tuple[str, float, Unit]:
        if raw_value < 0:
            raise InvalidParameterError(
                f"Parameter value cannot be negative: {raw_value} for {raw_name}"
            )

        name_lower = raw_name.strip().lower()
        if not name_lower:
            raise InvalidParameterError("Parameter name cannot be empty")

        canonical = self._aliases.get(name_lower, raw_name.strip())
        unit_str = raw_unit.strip()
        if not unit_str:
            return canonical, raw_value, Unit("")

        unit_info = self._units.get(unit_str)
        if unit_info is None:
            return canonical, raw_value, Unit(unit_str)

        base_unit = unit_info["base"]
        converted_value = convert(raw_value, unit_info["factor"])
        return canonical, converted_value, Unit(base_unit)
