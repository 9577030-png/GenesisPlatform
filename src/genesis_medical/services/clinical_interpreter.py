import ast
import operator
from collections.abc import Callable
from importlib.resources import files
from pathlib import Path
from typing import Any, cast

import yaml

from genesis_medical.domain.entities.parameter import Parameter
from genesis_medical.domain.entities.patient import PatientProfile
from genesis_medical.models.clinical_insights import (
    ClinicalInsights,
    CriterionEvaluation,
    DifferentialSuggestion,
    RedFlag,
    TreatmentHint,
)
from genesis_medical.sources.medical_reference_loader import MedicalReferenceLoader


class ClinicalInterpreter:
    def __init__(self, config_path: str | None = None) -> None:
        self.config_path = Path(config_path) if config_path else None
        self._load_config()
        self.reference_loader = MedicalReferenceLoader()

    def _load_config(self) -> None:
        if self.config_path is None:
            resource = files("genesis_medical").joinpath(
                "knowledge", "configs", "clinical_interpretations.yaml"
            )
            with resource.open("r", encoding="utf-8") as f:
                self.config = cast(dict[str, Any], yaml.safe_load(f) or {})
        else:
            with open(self.config_path, encoding="utf-8") as f:
                self.config = cast(dict[str, Any], yaml.safe_load(f) or {})
        self.interpretations = self.config.get("interpretations", {})

    def interpret(
        self, diagnoses: list[dict[str, Any]], parameters: list[Parameter], patient: PatientProfile
    ) -> dict[str, ClinicalInsights]:
        print("\n" + "=" * 60)
        print("🟢 ВЫЗВАН НОВЫЙ ИНТЕРПРЕТАТОР (ClinicalInterpreter)")
        print(f"Получено диагнозов: {len(diagnoses)}")
        print(f"Получено параметров: {len(parameters)}")
        print("=" * 60 + "\n")

        param_dict = {p.name: p.value for p in parameters}
        patient_info = {
            "gender": patient.gender.value
            if hasattr(patient.gender, "value")
            else str(patient.gender),
            "age": patient.age,
        }

        result: dict[str, ClinicalInsights] = {}
        for diag in diagnoses:
            diag_id = diag.get("id")
            if not diag_id:
                print(f"⚠️ Диагноз без ID: {diag}")
                continue
            # Извлекаем базовое имя (после последнего "/")
            base_name = diag_id.split("/")[-1]
            if base_name not in self.interpretations:
                print(f"⚠️ Диагноз {diag_id} (базовое имя {base_name}) не найден в интерпретациях")
                continue
            diag_config = self.interpretations[base_name]
            insights = self._build_insights(diag_config, diag, param_dict, patient_info)
            result[diag_id] = insights
            print(f"✅ Сгенерированы инсайты для {diag_id} (базовое имя {base_name})")

        print(f"📦 Итого инсайтов: {len(result)}")
        return result

    def _build_insights(
        self,
        diag_config: dict[str, Any],
        diag: dict[str, Any],
        param_dict: dict[str, float],
        patient_info: dict[str, Any],
    ) -> ClinicalInsights:
        insights = ClinicalInsights(
            diagnosis_id=diag.get("id", ""),
            label=diag_config.get("label", diag.get("label", "")),
            category=diag_config.get("category", ""),
            description=diag_config.get("description", diag.get("description")),
            references=diag_config.get("references"),
        )

        for crit in diag_config.get("criteria", []):
            param_name = crit.get("parameter")
            if not param_name:
                continue
            value = param_dict.get(param_name)
            is_optional = crit.get("optional", False)
            if value is None and is_optional:
                continue
            comment = self._generate_comment(crit, value, patient_info)
            evaluation = CriterionEvaluation(
                parameter=param_name,
                value=value,
                unit=crit.get("unit", ""),
                threshold=crit.get("threshold") or crit.get("threshold_low"),
                condition=crit.get("condition"),
                comment=comment,
            )
            insights.criteria.append(evaluation)

        for diff in diag_config.get("differentials", []):
            condition = diff.get("condition", "")
            if self._check_condition(condition, param_dict, patient_info):
                insights.differentials.append(
                    DifferentialSuggestion(condition=condition, text=diff.get("text", ""))
                )

        for rf in diag_config.get("red_flags", []):
            condition = rf.get("condition", "")
            if self._check_condition(condition, param_dict, patient_info):
                insights.red_flags.append(RedFlag(condition=condition, text=rf.get("text", "")))

        for hint in diag_config.get("treatment_hints", []):
            insights.treatment_hints.append(
                TreatmentHint(step=hint.get("step", ""), note=hint.get("note", ""))
            )

        return insights

    def _generate_comment(
        self, crit_config: dict[str, Any], value: float | None, patient_info: dict[str, Any]
    ) -> str:
        template = str(crit_config.get("comment_template", ""))
        if not template:
            return ""

        param_name = str(crit_config.get("parameter", ""))
        gender = patient_info.get("gender", "male")
        age = patient_info.get("age", 30)
        ref_info = (
            self.reference_loader.get_interpretation(param_name, value, gender, age)
            if param_name
            else {}
        )

        context: dict[str, Any] = {
            "value": value if value is not None else "не указан",
            "gender": gender,
            "age": age,
            "unit": crit_config.get("unit", ref_info.get("unit", "")),
            "threshold": crit_config.get("threshold") or crit_config.get("threshold_low"),
            "severity": self._determine_severity(value, crit_config.get("severity_mapping", [])),
            "additional": "",
            "interpretation": ref_info.get("text", ""),
            "ref_min": ref_info.get("min"),
            "ref_max": ref_info.get("max"),
        }
        if context["ref_min"] is not None and context["ref_max"] is not None:
            context["additional"] += (
                f" Референсный интервал: {context['ref_min']}–{context['ref_max']} {context['unit']}. "
            )

        comment = template.format(**context)

        for rule in crit_config.get("additional_rules", []):
            condition = rule.get("condition", "")
            if self._check_condition(
                condition, {str(crit_config.get("parameter", "")): value}, patient_info
            ):
                comment += " " + str(rule.get("text", ""))

        return comment

    def _determine_severity(self, value: float | None, mapping: list[dict[str, Any]]) -> str:
        if value is None:
            return "не определено"
        for item in mapping:
            range_str = item.get("range", "")
            try:
                if ">=" in range_str:
                    threshold = float(range_str.split(">=")[1].strip())
                    if value >= threshold:
                        return str(item.get("label", ""))
                elif "-" in range_str:
                    parts = range_str.split("-")
                    low = float(parts[0].strip())
                    high = float(parts[1].strip())
                    if low <= value <= high:
                        return str(item.get("label", ""))
                elif "<" in range_str:
                    threshold = float(range_str.split("<")[1].strip())
                    if value < threshold:
                        return str(item.get("label", ""))
            except Exception:
                continue
        return "не классифицировано"

    def _check_condition(
        self, condition: str, param_dict: dict[str, Any], patient_info: dict[str, Any]
    ) -> bool:
        if not condition:
            return True

        allowed_vars: dict[str, Any] = {}
        for k, v in {**param_dict, **patient_info}.items():
            if isinstance(v, (int, float, str, bool)):
                allowed_vars[k] = v

        binary_operators: dict[type[ast.AST], Callable[[Any, Any], Any]] = {
            ast.Add: operator.add,
            ast.Sub: operator.sub,
            ast.Mult: operator.mul,
            ast.Div: operator.truediv,
            ast.Mod: operator.mod,
        }

        comparison_operators: dict[type[ast.AST], Callable[[Any, Any], Any]] = {
            ast.Eq: operator.eq,
            ast.NotEq: operator.ne,
            ast.Lt: operator.lt,
            ast.LtE: operator.le,
            ast.Gt: operator.gt,
            ast.GtE: operator.ge,
        }

        unary_operators: dict[type[ast.AST], Callable[[Any], Any]] = {
            ast.Not: operator.not_,
            ast.USub: operator.neg,
            ast.UAdd: operator.pos,
        }

        def _eval_node(node: ast.AST) -> Any:
            if isinstance(node, ast.Constant):
                return node.value
            elif isinstance(node, ast.Name):
                if node.id in allowed_vars:
                    return allowed_vars[node.id]
                raise ValueError(f"Unknown variable: {node.id}")
            elif isinstance(node, ast.BinOp):
                left = _eval_node(node.left)
                right = _eval_node(node.right)
                binary_op_type = type(node.op)
                if binary_op_type not in binary_operators:
                    raise ValueError(f"Unsupported operator: {binary_op_type}")
                return binary_operators[binary_op_type](left, right)
            elif isinstance(node, ast.Compare):
                left = _eval_node(node.left)
                for op, comp in zip(
                    node.ops,
                    node.comparators,
                    strict=True,
                ):
                    right = _eval_node(comp)
                    comparison_op_type = type(op)
                    if comparison_op_type not in comparison_operators:
                        raise ValueError(f"Unsupported comparison: {comparison_op_type}")
                    if not comparison_operators[comparison_op_type](left, right):
                        return False
                    left = right
                return True
            elif isinstance(node, ast.BoolOp):
                values = [_eval_node(v) for v in node.values]
                if isinstance(node.op, ast.And):
                    return all(values)
                elif isinstance(node.op, ast.Or):
                    return any(values)
                else:
                    raise ValueError("Unsupported boolean operator")
            elif isinstance(node, ast.UnaryOp):
                operand = _eval_node(node.operand)
                unary_op_type = type(node.op)
                if unary_op_type not in unary_operators:
                    raise ValueError(f"Unsupported unary operator: {unary_op_type}")
                return unary_operators[unary_op_type](operand)
            elif isinstance(node, ast.Attribute):
                raise ValueError("Attribute access not allowed")
            else:
                raise ValueError(f"Unsupported AST node: {type(node).__name__}")

        try:
            parsed = ast.parse(condition, mode="eval")
            return bool(_eval_node(parsed.body))
        except Exception:
            return False
