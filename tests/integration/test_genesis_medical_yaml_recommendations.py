import pytest
from genesis_medical.sources.yaml_recommendation_loader import YamlRecommendationLoader
from genesis_medical.domain.entities.recommendation import Recommendation
from genesis_medical.domain.value_objects.severity import Severity

@pytest.mark.integration
def test_load_recommendations():
    loader = YamlRecommendationLoader()

    rec = loader.get_recommendation("iron_deficiency")
    assert rec is not None
    assert isinstance(rec, Recommendation)
    assert rec.doctor_specialty == "Hematologist"
    assert "Iron" in rec.additional_tests
    assert rec.urgency == Severity.MODERATE

    rec2 = loader.get_recommendation("b12_deficiency")
    assert rec2 is not None
    assert rec2.doctor_specialty == "Hematologist"
    assert "B12" in rec2.additional_tests
    assert rec2.urgency == Severity.MODERATE

    rec3 = loader.get_recommendation("hypothyroidism")
    assert rec3 is not None
    assert rec3.doctor_specialty == "Endocrinologist"
    assert rec3.urgency == Severity.MODERATE

    rec4 = loader.get_recommendation("hyperkalemia")
    assert rec4 is not None
    assert rec4.doctor_specialty == "Nephrologist"
    assert rec4.urgency == Severity.SEVERE

    rec5 = loader.get_recommendation("diabetes_mellitus_type2")
    assert rec5 is not None
    assert rec5.doctor_specialty == "Endocrinologist"
    assert rec5.urgency == Severity.HIGH

    rec6 = loader.get_recommendation("acute_hepatitis")
    assert rec6 is not None
    assert rec6.doctor_specialty == "Hepatologist"
    assert rec6.urgency == Severity.HIGH

    rec7 = loader.get_recommendation("acute_pancreatitis")
    assert rec7 is not None
    assert rec7.doctor_specialty == "Gastroenterologist"
    assert rec7.urgency == Severity.HIGH

    rec8 = loader.get_recommendation("celiac_disease")
    assert rec8 is not None
    assert rec8.doctor_specialty == "Gastroenterologist"
    assert rec8.urgency == Severity.MODERATE

    rec_unknown = loader.get_recommendation("unknown")
    assert rec_unknown is None

@pytest.mark.integration
def test_recommendation_loader_parses_all():
    loader = YamlRecommendationLoader()
    expected_ids = [
        "iron_deficiency",
        "b12_deficiency",
        "macrocytic_anemia",
        "hypothyroidism",
        "hyperthyroidism",
        "thyroid",
        "hyperkalemia",
        "hypokalemia",
        "hypernatremia",
        "hyponatremia",
        "diabetes_mellitus_type2",
        "prediabetes",
        "metabolic_syndrome",
        "hypercholesterolemia",
        "acute_hepatitis",
        "cholestasis",
        "nonalcoholic_fatty_liver",
        "acute_kidney_injury",
        "chronic_kidney_disease",
        "acute_pancreatitis",
        "inflammatory_bowel_disease",
        "celiac_disease",
        "gout",
        "osteoporosis",
        "folate_deficiency"
    ]
    for expected_id in expected_ids:
        assert loader.get_recommendation(expected_id) is not None
