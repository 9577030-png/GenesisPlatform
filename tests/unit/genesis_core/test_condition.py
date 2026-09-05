import pytest

from genesis_core import Condition


def test_unsupported_operator_is_rejected():
    with pytest.raises(
        ValueError,
        match="Unsupported operator",
    ):
        Condition(
            fact="temperature",
            operator="contains_temperature",
            value=90,
        )


def test_condition_requires_fact():
    with pytest.raises(
        ValueError,
        match="Condition fact cannot be empty",
    ):
        Condition(
            fact="",
            operator="==",
            value=10,
        )


@pytest.mark.parametrize(
    "operator",
    [
        "==",
        "!=",
        "<",
        "<=",
        ">",
        ">=",
        "in",
        "not_in",
        "between",
    ],
)
def test_all_supported_operators_are_accepted(
    operator: str,
):
    Condition(
        fact="value",
        operator=operator,
        value=10,
    )