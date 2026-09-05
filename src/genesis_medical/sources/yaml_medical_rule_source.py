from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path
from typing import Any

import yaml

from genesis_core.contracts import RuleSource
from genesis_medical.domain.rule_version import RuleVersion


class YamlMedicalRuleSource(RuleSource):
    """Читает medical YAML и разворачивает их в нормализованные conditions."""

    def __init__(self, base_path: str | Path) -> None:
        self.base_path = Path(base_path)

    def load_rules(self) -> Iterator[dict[str, Any]]:
        if not self.base_path.exists():
            return

        for yaml_file in sorted(self.base_path.rglob("*.yaml")):
            with yaml_file.open("r", encoding="utf-8") as handle:
                data = yaml.safe_load(handle)

            if not isinstance(data, dict):
                continue

            rule_id = str(data.get("id", yaml_file.stem))
            rule_version = RuleVersion.from_yaml(
                rule_id=rule_id,
                yaml_data=data,
            )

            for condition in rule_version.conditions:
                yield {
                    "source": str(yaml_file),
                    "rule_version": rule_version,
                    "condition": condition,
                    "core_rule_id": f"{rule_version.rule_id}:{condition.get('id', rule_version.rule_id)}",
                }
