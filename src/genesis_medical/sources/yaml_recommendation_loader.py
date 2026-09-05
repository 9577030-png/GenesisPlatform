from __future__ import annotations

from importlib.resources import files
from typing import Optional

import yaml

from ..domain.entities.recommendation import Recommendation
from ..domain.value_objects.severity import Severity


class YamlRecommendationLoader:
    """Load doctor recommendations from bundled medical knowledge or a file."""

    def __init__(self, config_path: str | None = None) -> None:
        self.config_path = config_path
        self._recommendations: dict | None = None

    def _default_resource(self):
        return files("genesis_medical").joinpath(
            "knowledge", "configs", "doctor_recommendations.yaml"
        )

    def _load(self) -> dict:
        resource = open(self.config_path, "r", encoding="utf-8") if self.config_path else self._default_resource().open("r", encoding="utf-8")
        try:
            data = yaml.safe_load(resource) or {}
        finally:
            resource.close()
        return data.get("recommendations", {})

    def get_recommendation(self, finding_id: str) -> Optional[Recommendation]:
        if self._recommendations is None:
            self._recommendations = self._load()
        data = self._recommendations.get(finding_id)
        if not data:
            return None
        urgency = getattr(
            Severity,
            data.get("urgency", "moderate").upper(),
            Severity.MODERATE,
        )
        return Recommendation(
            doctor_specialty=data["doctor_specialty"],
            urgency=urgency,
            additional_tests=data.get("additional_tests", []),
        )

    def reload(self) -> None:
        self._recommendations = self._load()
