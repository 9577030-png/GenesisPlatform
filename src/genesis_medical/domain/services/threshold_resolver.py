from dataclasses import replace
from typing import Any

from genesis_medical.domain.entities.threshold import Threshold
from genesis_medical.domain.exceptions import ConfigurationError


def resolve(
    global_thresholds: dict[str, Threshold],
    overrides: dict[str, dict[str, Any]],
) -> dict[str, Threshold]:
    if global_thresholds is None:
        raise ConfigurationError(
            "global_thresholds cannot be None"
        )

    if not isinstance(global_thresholds, dict):
        raise ConfigurationError(
            "global_thresholds must be a dict"
        )

    result: dict[str, Threshold] = {}

    for param_name, base in global_thresholds.items():
        if param_name not in overrides:
            result[param_name] = base
            continue

        override = overrides[param_name]

        if not isinstance(override, dict):
            raise ConfigurationError(
                f"Override for '{param_name}' must be a dict, "
                f"got {type(override)}"
            )

        try:
            result[param_name] = replace(
                base,
                low=override.get("low", base.low),
                high=override.get("high", base.high),
                unit=override.get("unit", base.unit),
                risk_level=override.get(
                    "risk_level",
                    base.risk_level,
                ),
            )
        except Exception as exc:
            raise ConfigurationError(
                f"Failed to apply override for "
                f"'{param_name}': {exc}"
            ) from exc

    return result
