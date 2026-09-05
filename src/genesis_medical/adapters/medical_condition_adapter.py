from __future__ import annotations

from typing import Any

from genesis_core import Condition


class MedicalConditionAdapter:
    """
    Преобразует legacy medical condition
    в generic Condition.

    Generic engine получает только математические условия.
    Medical metadata (gender, scoring, risk, label, id)
    остаётся в medical layer.
    """

    @staticmethod
    def to_conditions(
        condition: dict[str, Any],
    ) -> tuple[Condition, ...]:
        parameter = condition.get("parameter")

        if not parameter:
            raise ValueError(
                "Medical condition requires 'parameter'"
            )

        parameter = str(parameter).lower()

        result: list[Condition] = []

        if "min" in condition:
            result.append(
                Condition(
                    fact=parameter,
                    operator=">=",
                    value=condition["min"],
                )
            )

        if "max" in condition:
            result.append(
                Condition(
                    fact=parameter,
                    operator="<=",
                    value=condition["max"],
                )
            )

        if not result:
            raise ValueError(
                f"Medical condition for {parameter!r} "
                "must contain 'min' or 'max'"
            )

        return tuple(result)

    @staticmethod
    def matches_gender(
        condition: dict[str, Any],
        patient_gender: Any,
    ) -> bool:
        required_gender = condition.get("gender")

        if required_gender is None:
            return True

        required = str(required_gender).lower()

        if hasattr(patient_gender, "value"):
            current = str(patient_gender.value).lower()
        else:
            current = str(patient_gender).lower()

        return required == current

    @staticmethod
    def is_applicable(
        condition: dict[str, Any],
        patient_gender: Any,
    ) -> bool:
        return MedicalConditionAdapter.matches_gender(
            condition,
            patient_gender,
        )