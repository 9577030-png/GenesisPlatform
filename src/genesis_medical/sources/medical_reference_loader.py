from __future__ import annotations

import json
from importlib.resources import files
from typing import Any

import yaml


class MedicalReferenceLoader:
    """Load and query laboratory reference intervals from bundled knowledge."""

    def __init__(
        self,
        config_path: str | None = None,
        data: dict[str, Any] | None = None,
    ) -> None:
        self._references: dict[str, Any] = {}
        if config_path:
            self._load_from_file(config_path)
        elif data is not None:
            self._references = data
        else:
            self._load_from_resource()

        self._param_cache: dict[str, list[dict[str, Any]]] = {}
        self._build_cache()

    def _load_from_resource(self) -> None:
        clinical_resource = files("genesis_medical").joinpath(
            "knowledge", "configs", "clinical_interpretations.yaml"
        )
        with clinical_resource.open("r", encoding="utf-8") as handle:
            data = yaml.safe_load(handle) or {}

        parameters = data.get("parameters")
        if parameters:
            self._references = parameters
            return

        # The bundled medical interpretation file stores diagnosis-level
        # interpretations; laboratory reference ranges are stored separately.
        medical_data_resource = files("genesis_medical").joinpath(
            "knowledge", "configs", "medical_data.json"
        )
        with medical_data_resource.open("r", encoding="utf-8") as handle:
            medical_data = json.load(handle)
        self._references = self._build_references_from_norms(
            medical_data.get("norms", {})
        )

    def _load_from_file(self, path: str) -> None:
        with open(path, "r", encoding="utf-8") as handle:
            data = yaml.safe_load(handle) or {}
        self._references = data.get("parameters", {})

    @staticmethod
    def _build_references_from_norms(
        norms: dict[str, Any],
    ) -> dict[str, Any]:
        references: dict[str, Any] = {}
        for parameter_name, config in norms.items():
            intervals = config.get("norms")
            if not intervals:
                intervals = [
                    {
                        "min": config.get("base_min"),
                        "max": config.get("base_max"),
                    }
                ]

            normalized: list[dict[str, Any]] = []
            for interval in intervals:
                item = dict(interval)
                item.setdefault("unit", config.get("unit", ""))
                item.setdefault("status", "normal")
                item.setdefault("risk", "LOW")
                normalized.append(item)

            references[parameter_name] = {
                "name": config.get("name", parameter_name),
                "unit": config.get("unit", ""),
                "intervals": normalized,
            }

        return references

    def _build_cache(self) -> None:
        for param_name, config in self._references.items():
            intervals = config.get("intervals", [])
            if intervals:
                self._param_cache[param_name] = intervals

    def get_interpretation(
        self,
        param_name: str,
        value: Any,
        gender: str | None = None,
        age: float | None = None,
    ) -> dict[str, Any]:
        if value is None:
            return {}

        intervals = self._param_cache.get(param_name)
        if not intervals:
            return {}

        try:
            numeric_value = float(value)
        except (TypeError, ValueError):
            return {}

        for interval in intervals:
            interval_gender = interval.get("gender")
            if interval_gender and gender:
                if interval_gender.lower() != gender.lower():
                    continue
            if "age_min" in interval and age is not None and age < interval["age_min"]:
                continue
            if "age_max" in interval and age is not None and age > interval["age_max"]:
                continue

            min_val = interval.get("min")
            max_val = interval.get("max")
            if min_val is not None and numeric_value < min_val:
                continue
            if max_val is not None and numeric_value > max_val:
                continue

            return {
                "status": interval.get("status", "normal"),
                "comment": interval.get("comment", ""),
                "range": (
                    f"{min_val if min_val is not None else '…'} – "
                    f"{max_val if max_val is not None else '…'}"
                ),
                "risk_level": interval.get("risk", "LOW"),
                "recommendations": interval.get("recommendations", []),
                "min": min_val,
                "max": max_val,
                "unit": interval.get("unit", ""),
                "text": interval.get("text", interval.get("comment", "")),
            }

        return {
            "status": "unknown",
            "comment": (
                f"Значение {numeric_value} вне заданных референсных "
                f"интервалов для {param_name}"
            ),
            "range": "не определено",
            "risk_level": "MEDIUM",
            "recommendations": ["Требуется уточнение референсных значений"],
        }

    def get_all_parameters(self) -> list[str]:
        return list(self._references.keys())

    def get_parameter_config(self, param_name: str) -> dict[str, Any] | None:
        return self._references.get(param_name)
