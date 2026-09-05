from dataclasses import dataclass, field
from datetime import datetime, UTC
from typing import Optional, List, Dict, Any
from enum import IntEnum, Enum

class RulePriority(IntEnum):
    LOW = 10
    MEDIUM = 50
    HIGH = 100
    CRITICAL = 200

class RuleTier(str, Enum):
    BASIC = "basic"
    ENRICHED = "enriched"

@dataclass
class RuleVersion:
    rule_id: str
    name: str
    conditions: List[Dict[str, Any]]
    actions: List[Dict[str, Any]]
    created_at: datetime
    created_by: str
    version_id: int = 0
    priority: RulePriority = RulePriority.MEDIUM
    conflicts_with: List[str] = field(default_factory=list)
    supports: List[str] = field(default_factory=list)
    is_active: bool = False
    comment: Optional[str] = None
    tier: RuleTier = RuleTier.BASIC  # <-- новое поле

    @classmethod
    def from_yaml(cls, rule_id: str, yaml_data: Dict[str, Any], created_by: str = "system", tier: RuleTier = RuleTier.BASIC) -> "RuleVersion":
        """
        Создать версию из YAML-словаря.
        Если в YAML есть секция 'conditions', используем её.
        Иначе конвертируем старый формат (thresholds/scoring) в conditions.
        """
        # Если уже есть conditions, используем как есть
        if "conditions" in yaml_data:
            conditions = yaml_data["conditions"]
        else:
            # Конвертируем старый формат
            conditions = cls._convert_old_format(yaml_data, rule_id)

        # Извлекаем actions (рекомендации) из секции recommendations
        actions = []
        if "recommendations" in yaml_data:
            for rec in yaml_data["recommendations"]:
                actions.append({"type": "recommendation", "text": rec})

        return cls(
            version_id=0,
            rule_id=rule_id,
            name=yaml_data.get("name", rule_id),
            conditions=conditions,
            actions=actions,
            priority=RulePriority[yaml_data.get("priority", "MEDIUM").upper()],
            conflicts_with=yaml_data.get("conflicts_with", []),
            supports=yaml_data.get("supports", []),
            created_at=datetime.now(UTC),
            created_by=created_by,
            is_active=False,
            comment=yaml_data.get("comment"),
            tier=tier
        )

    @staticmethod
    def _convert_old_format(yaml_data: Dict[str, Any], rule_id: str) -> List[Dict[str, Any]]:
        """
        Преобразует старый формат (thresholds/scoring) в список conditions.
        Поддерживает:
          - thresholds: { param: {min: X, max: Y} }
          - scoring: { param: weight }

        ВАЖНО про id: каждому condition нужен СВОЙ уникальный id, иначе
        InferenceEngine.infer() (cond.get('id', rule.rule_id)) присвоит всем
        условиям одного файла один и тот же id -> findings схлопнутся в
        неразличимые дубли в отчёте (см. разбор бага с acute_coronary_syndrome).

        - top_id берём из yaml_data['id'] (чистое имя, например "acute_kidney_injury"),
          а не из rule_id (это относительный путь вида "nephrology/acute_kidney_injury") -
          иначе рвётся связь с diagnosis_labels/clinical_interpretations.yaml.
        - если параметр в файле один - id условия = top_id (совпадает с диагнозом целиком).
        - если параметров несколько - id условия = "{top_id}_{param}" (уникально для каждого).
        """
        top_id = yaml_data.get("id", rule_id)
        conditions = []
        # Если есть thresholds
        if "thresholds" in yaml_data:
            is_single = len(yaml_data["thresholds"]) == 1
            for param, spec in yaml_data["thresholds"].items():
                cond_id = top_id if is_single else f"{top_id}_{param}"
                cond = {"id": cond_id, "parameter": param}
                if "min" in spec:
                    cond["min"] = spec["min"]
                if "max" in spec:
                    cond["max"] = spec["max"]
                # Если есть gender
                if "gender" in spec:
                    cond["gender"] = spec["gender"]
                # scoring может быть задан отдельно или брать вес из scoring_rules
                # по умолчанию ставим scoring = 5
                cond["scoring"] = spec.get("scoring", 5)
                cond["risk"] = spec.get("risk", "MEDIUM")
                cond["label"] = f"{param} out of range"
                conditions.append(cond)
        # Если есть scoring_rules (старый формат)
        elif "scoring" in yaml_data:
            is_single = len(yaml_data["scoring"]) == 1
            for param, weight in yaml_data["scoring"].items():
                cond_id = top_id if is_single else f"{top_id}_{param}"
                cond = {
                    "id": cond_id,
                    "parameter": param,
                    "scoring": weight,
                    "risk": "MEDIUM",
                    "label": f"{param} abnormal"
                }
                # Если есть override_thresholds, можно добавить min/max
                if "override_thresholds" in yaml_data and param in yaml_data["override_thresholds"]:
                    overrides = yaml_data["override_thresholds"][param]
                    if "low" in overrides:
                        cond["max"] = overrides["low"]  # т.к. low означает нижнюю границу нормы?
                    if "high" in overrides:
                        cond["min"] = overrides["high"]
                conditions.append(cond)
        else:
            # Если ничего нет, создаём заглушку
            conditions.append({
                "parameter": "unknown",
                "scoring": 5,
                "risk": "LOW",
                "label": "Unknown condition"
            })
        return conditions