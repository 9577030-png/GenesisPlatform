from __future__ import annotations

from importlib.resources import files
from typing import Any

import yaml


class ClinicalLogicLoader:
    """Load the medical post-processing configuration from bundled knowledge."""

    def __init__(self, config_path: str | None = None):
        self.config_path = config_path
        self._config: dict[str, Any] | None = None

    def _default_resource(self):
        return files("genesis_medical").joinpath(
            "knowledge", "configs", "clinical_logic.yaml"
        )

    def _load(self) -> dict[str, Any]:
        resource = open(self.config_path, "r", encoding="utf-8") if self.config_path else self._default_resource().open("r", encoding="utf-8")
        try:
            data = yaml.safe_load(resource) or {}
        finally:
            resource.close()
        return data

    def get_config(self) -> dict[str, Any]:
        if self._config is None:
            self._config = self._load()
        return self._config

    def reload(self) -> None:
        self._config = self._load()

    def get_diagnosis_labels(self) -> dict[str, str]:
        return self.get_config().get("diagnosis_labels", {})

    def get_system_groups(self) -> dict[str, list[str]]:
        return self.get_config().get("system_groups", {})

    def get_allowed_primary(self) -> list[str]:
        return self.get_config().get("allowed_primary", [])
