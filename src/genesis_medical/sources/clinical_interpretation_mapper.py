from __future__ import annotations

from importlib.resources import files
from typing import Set

import yaml


class ClinicalInterpretationMapper:
    """Identify medical rules with enriched interpretation metadata."""

    def __init__(self) -> None:
        self._enriched_ids: Set[str] = set()
        resource = files("genesis_medical").joinpath(
            "knowledge", "configs", "clinical_interpretations.yaml"
        )
        with resource.open("r", encoding="utf-8") as handle:
            data = yaml.safe_load(handle) or {}
        self._enriched_ids = set(data.get("interpretations", {}).keys())

    def is_enriched(self, rule_id: str) -> bool:
        return rule_id in self._enriched_ids

    def get_enriched_ids(self) -> Set[str]:
        return set(self._enriched_ids)
