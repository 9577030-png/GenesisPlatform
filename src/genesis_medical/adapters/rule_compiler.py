from __future__ import annotations

from typing import Any

from genesis_core import Condition, Rule
from genesis_medical.domain.rule_version import RuleVersion

from .compiled_rule import CompiledRule
from .medical_condition_adapter import MedicalConditionAdapter


class RuleCompiler:
    """
    РљРѕРјРїРёР»РёСЂСѓРµС‚ RuleVersion РІ РЅР°Р±РѕСЂ РёСЃРїРѕР»РЅСЏРµРјС‹С… generic Rule
    СЃ СЃРѕС…СЂР°РЅРµРЅРёРµРј РёСЃС…РѕРґРЅРѕРіРѕ medical context.

    РџСЂРё РїРµСЂРµРґР°РЅРЅРѕРј patient_gender medical conditions,
    РЅРµСЃРѕРІРјРµСЃС‚РёРјС‹Рµ СЃ РїРѕР»РѕРј РїР°С†РёРµРЅС‚Р°, РЅРµ РєРѕРјРїРёР»РёСЂСѓСЋС‚СЃСЏ.
    """

    @staticmethod
    def compile(
        rule_version: RuleVersion,
        patient_gender: Any | None = None,
    ) -> tuple[CompiledRule, ...]:
        result: list[CompiledRule] = []

        for condition in rule_version.conditions:
            if (
                patient_gender is not None
                and not MedicalConditionAdapter.is_applicable(
                    condition,
                    patient_gender,
                )
            ):
                continue

            conditions = RuleCompiler._convert_condition(
                condition
            )

            rule_id = condition.get(
                "id",
                rule_version.rule_id,
            )

            rule = Rule(
                id=rule_id,
                conditions=conditions,
                result=rule_version.actions,
                version=str(rule_version.version_id),
                priority=int(rule_version.priority),
                conflicts_with=tuple(
                    rule_version.conflicts_with
                ),
                supports=tuple(
                    rule_version.supports
                ),
            )

            result.append(
                CompiledRule(
                    rule=rule,
                    condition=condition,
                    rule_version=rule_version,
                )
            )

        return tuple(result)

    @staticmethod
    def _convert_condition(
        condition: dict[str, Any],
    ) -> tuple[Condition, ...]:
        if "fact" in condition:
            return (
                Condition(
                    fact=condition["fact"],
                    operator=condition["operator"],
                    value=condition.get("value"),
                ),
            )

        if "parameter" in condition:
            return MedicalConditionAdapter.to_conditions(
                condition
            )

        raise ValueError(
            "Unsupported condition format: "
            "expected either 'fact' or 'parameter'"
        )
