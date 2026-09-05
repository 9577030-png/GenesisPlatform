from genesis_medical.sources import MedicalReferenceLoader


def test_bundled_reference_loader_discovers_medical_parameters() -> None:
    loader = MedicalReferenceLoader()

    parameters = loader.get_all_parameters()

    assert "glucose" in parameters
    assert "hemoglobin" in parameters


def test_bundled_reference_loader_applies_gender_specific_range() -> None:
    loader = MedicalReferenceLoader()

    result = loader.get_interpretation(
        "hemoglobin",
        125,
        gender="female",
    )

    assert result["min"] == 120
    assert result["max"] == 150
    assert result["unit"] == "г/Л"
