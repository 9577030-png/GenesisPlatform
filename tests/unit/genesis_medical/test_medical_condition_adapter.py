import pytest

from genesis_medical.adapters.medical_condition_adapter import (
    MedicalConditionAdapter,
)
from genesis_core import Condition


def test_min_and_max_are_converted_to_two_conditions():
    condition = {
        "parameter": "glucose",
        "min": 7.0,
        "max": 10.0,
    }

    result = MedicalConditionAdapter.to_conditions(condition)

    assert result == (
        Condition(
            fact="glucose",
            operator=">=",
            value=7.0,
        ),
        Condition(
            fact="glucose",
            operator="<=",
            value=10.0,
        ),
    )


def test_min_is_converted_to_greater_or_equal():
    condition = {
        "parameter": "glucose",
        "min": 7.0,
    }

    result = MedicalConditionAdapter.to_conditions(condition)

    assert result == (
        Condition(
            fact="glucose",
            operator=">=",
            value=7.0,
        ),
    )


def test_max_is_converted_to_less_or_equal():
    condition = {
        "parameter": "glucose",
        "max": 10.0,
    }

    result = MedicalConditionAdapter.to_conditions(condition)

    assert result == (
        Condition(
            fact="glucose",
            operator="<=",
            value=10.0,
        ),
    )


def test_parameter_name_is_normalized_to_lowercase():
    condition = {
        "parameter": "GLUCOSE",
        "min": 7.0,
    }

    result = MedicalConditionAdapter.to_conditions(condition)

    assert result == (
        Condition(
            fact="glucose",
            operator=">=",
            value=7.0,
        ),
    )


def test_medical_metadata_is_not_put_into_generic_condition():
    condition = {
        "id": "high_glucose",
        "parameter": "glucose",
        "min": 7.0,
        "max": 10.0,
        "gender": "female",
        "scoring": 5,
        "risk": "HIGH",
        "label": "High glucose",
    }

    result = MedicalConditionAdapter.to_conditions(condition)

    assert len(result) == 2

    for item in result:
        assert item.fact == "glucose"
        assert item.operator in {">=", "<="}
        assert item.value in {7.0, 10.0}

        assert not hasattr(item, "gender")
        assert not hasattr(item, "scoring")
        assert not hasattr(item, "risk")
        assert not hasattr(item, "label")


def test_parameter_is_required():
    with pytest.raises(ValueError, match="parameter"):
        MedicalConditionAdapter.to_conditions(
            {
                "min": 7.0,
            }
        )


def test_min_or_max_is_required():
    with pytest.raises(
        ValueError,
        match="must contain 'min', 'max'",
    ):
        MedicalConditionAdapter.to_conditions(
            {
                "parameter": "glucose",
            }
        )


def test_gender_without_value_is_accepted_by_default():
    assert MedicalConditionAdapter.matches_gender(
        {
            "parameter": "glucose",
            "min": 7.0,
        },
        "male",
    )


def test_gender_matches_string():
    assert MedicalConditionAdapter.matches_gender(
        {
            "parameter": "hemoglobin",
            "max": 130,
            "gender": "male",
        },
        "male",
    )


def test_gender_matches_enum():
    class Gender:
        value = "male"

    assert MedicalConditionAdapter.matches_gender(
        {
            "parameter": "hemoglobin",
            "max": 130,
            "gender": "MALE",
        },
        Gender(),
    )


def test_gender_is_case_insensitive():
    assert MedicalConditionAdapter.matches_gender(
        {
            "parameter": "hemoglobin",
            "max": 130,
            "gender": "MALE",
        },
        "male",
    )


def test_wrong_gender_does_not_match():
    assert not MedicalConditionAdapter.matches_gender(
        {
            "parameter": "hemoglobin",
            "max": 130,
            "gender": "male",
        },
        "female",
    )
def test_min_is_converted_to_greater_or_equal():
    condition = {
        "parameter": "glucose",
        "min": 7.0,
    }

    result = MedicalConditionAdapter.to_conditions(condition)

    assert result == (
        Condition(
            fact="glucose",
            operator=">=",
            value=7.0,
        ),
    )


def test_max_is_converted_to_less_or_equal():
    condition = {
        "parameter": "glucose",
        "max": 10.0,
    }

    result = MedicalConditionAdapter.to_conditions(condition)

    assert result == (
        Condition(
            fact="glucose",
            operator="<=",
            value=10.0,
        ),
    )


def test_medical_metadata_is_not_put_into_generic_condition():
    condition = {
        "id": "high_glucose",
        "parameter": "glucose",
        "min": 7.0,
        "max": 10.0,
        "gender": "female",
        "scoring": 5,
        "risk": "HIGH",
        "label": "High glucose",
    }

    result = MedicalConditionAdapter.to_conditions(condition)

    assert len(result) == 2

    for item in result:
        assert item.fact == "glucose"
        assert item.operator in {">=", "<="}
        assert item.value in {7.0, 10.0}

        assert not hasattr(item, "gender")
        assert not hasattr(item, "scoring")
        assert not hasattr(item, "risk")
        assert not hasattr(item, "label")


def test_parameter_is_required():
    with pytest.raises(ValueError, match="parameter"):
        MedicalConditionAdapter.to_conditions(
            {
                "min": 7.0,
            }
        )


def test_min_or_max_is_required():
    with pytest.raises(
        ValueError,
        match="must contain 'min' or 'max'",
    ):
        MedicalConditionAdapter.to_conditions(
            {
                "parameter": "glucose",
            }
        )

def test_is_applicable_without_gender():
    assert MedicalConditionAdapter.is_applicable(
        {
            "parameter": "glucose",
            "min": 7.0,
        },
        "male",
    )


def test_is_applicable_for_matching_gender():
    assert MedicalConditionAdapter.is_applicable(
        {
            "parameter": "hemoglobin",
            "max": 130,
            "gender": "male",
        },
        "male",
    )


def test_is_not_applicable_for_wrong_gender():
    assert not MedicalConditionAdapter.is_applicable(
        {
            "parameter": "hemoglobin",
            "max": 130,
            "gender": "male",
        },
        "female",
    )        
