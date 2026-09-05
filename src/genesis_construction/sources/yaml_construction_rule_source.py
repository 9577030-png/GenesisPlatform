from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path
from typing import Any

import yaml

from genesis_core.contracts import RuleSource


class YamlConstructionRuleSource(RuleSource):
    """Loads construction-domain rule documents from YAML files."""

    def __init__(self, base_path: str | Path) -> None:
        self.base_path = Path(base_path)

    def load_rules(self) -> Iterator[dict[str, Any]]:
        if not self.base_path.exists():
            return
        for yaml_file in sorted(self.base_path.rglob("*.yaml")):
            with yaml_file.open("r", encoding="utf-8") as handle:
                data = yaml.safe_load(handle)
            if isinstance(data, dict):
                yield data
