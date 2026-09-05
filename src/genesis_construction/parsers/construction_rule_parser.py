from __future__ import annotations

from typing import Any

from genesis_core import Condition, Rule
from genesis_core.contracts import RuleParser


class ConstructionRuleParser(RuleParser):
    """Converts construction-domain YAML records into generic Core Rules."""

    def parse(self, raw: dict[str, Any]) -> Rule:
        rule_id = raw.get("id")
        conditions = raw.get("conditions")
        result = raw.get("result")
        if not isinstance(rule_id, str) or not rule_id.strip():
            raise ValueError("Construction rule requires non-empty 'id'")
        if not isinstance(conditions, list) or not conditions:
            raise ValueError("Construction rule requires non-empty 'conditions'")

        parsed: list[Condition] = []
        for item in conditions:
            if not isinstance(item, dict):
                raise ValueError("Construction condition must be an object")
            fact = item.get("fact")
            operator = item.get("operator")
            value = item.get("value")
            if not isinstance(fact, str) or not fact.strip():
                raise ValueError("Construction condition requires 'fact'")
            parsed.append(Condition(fact=fact, operator=operator, value=value))

        return Rule(
            id=rule_id,
            conditions=tuple(parsed),
            result=result,
            version=str(raw.get("version", "1")),
            priority=int(raw.get("priority", 0)),
            conflicts_with=tuple(raw.get("conflicts_with", ())),
            supports=tuple(raw.get("supports", ())),
        )
