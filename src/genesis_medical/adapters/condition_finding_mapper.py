from __future__ import annotations

from typing import Any

from genesis_medical.domain.entities.finding import ClinicalFinding
from genesis_medical.domain.rule_version import RuleVersion
from genesis_medical.domain.value_objects.risk_level import RiskLevel


class ConditionFindingMapper:
    """
    РџСЂРµРѕР±СЂР°Р·СѓРµС‚ СЃСЂР°Р±РѕС‚Р°РІС€РµРµ РјРµРґРёС†РёРЅСЃРєРѕРµ condition
    РІ ClinicalFinding.

    Р­С‚Рѕ РјРµРґРёС†РёРЅСЃРєР°СЏ РёРЅС‚РµСЂРїСЂРµС‚Р°С†РёСЏ.
    Generic rule engine СЃСЋРґР° РЅРµ РїРѕРїР°РґР°РµС‚.
    """

    _RISK_MAP = {
        "HIGH": RiskLevel.HIGH,
        "MEDIUM": RiskLevel.MEDIUM,
        "NORMAL": RiskLevel.NORMAL,
        "CRITICAL": RiskLevel.CRITICAL,
    }

    @classmethod
    def to_finding(
        cls,
        condition: dict[str, Any],
        rule: RuleVersion,
    ) -> ClinicalFinding:
        scoring = condition.get("scoring", 5)

        probability = min(scoring / 10.0, 1.0)

        risk = (
            RiskLevel.HIGH
            if probability > 0.5
            else RiskLevel.NORMAL
        )

        configured_risk = condition.get("risk")

        if configured_risk:
            risk = cls._RISK_MAP.get(
                str(configured_risk).upper(),
                risk,
            )

        return ClinicalFinding(
            id=condition.get("id", rule.rule_id),
            title=condition.get("label", rule.name),
            probability=probability,
            risk=risk,
            evidence=condition.get(
                "recommendations",
                [],
            ),
            description=condition.get(
                "description",
                rule.comment or "",
            ),
        )
