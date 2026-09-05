from __future__ import annotations

from typing import Any

from genesis_core import Condition, Rule
from genesis_core.contracts import RuleParser

from genesis_medical.adapters.medical_condition_adapter import MedicalConditionAdapter
from genesis_medical.domain.rule_version import RuleVersion


class MedicalRuleParser(RuleParser):
    """Преобразует одно нормализованное medical condition в Core Rule."""

    def parse(self, raw: dict[str, Any]) -> Rule:
        condition = raw.get("condition")
        if not isinstance(condition, dict):
            raise ValueError("Medical rule parser requires 'condition'")

        rule_version = raw.get("rule_version")
        if not isinstance(rule_version, RuleVersion):
            raise ValueError("Medical rule parser requires 'rule_version'")

        conditions = MedicalConditionAdapter.to_conditions(condition)

        rule_id = raw.get(
            "core_rule_id",
            condition.get("id", rule_version.rule_id),
        )

        return Rule(
            id=str(rule_id),
            conditions=conditions,
            result=rule_version.actions,
            version=str(rule_version.version_id),
            priority=int(rule_version.priority),
            conflicts_with=tuple(rule_version.conflicts_with),
            supports=tuple(rule_version.supports),
        )
