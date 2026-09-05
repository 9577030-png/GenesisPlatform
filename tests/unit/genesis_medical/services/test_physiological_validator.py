from genesis_medical.services import PhysiologicalValidator


def test_physiological_validator_uses_bundled_knowledge() -> None:
    validator = PhysiologicalValidator()

    assert validator.validate(
        [{"name": "glucose", "value": 5.0}]
    ) == []
