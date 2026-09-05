import pytest
pytest.importorskip('passlib', reason="optional external dependency not installed")
pytestmark = pytest.mark.external
pytest.importorskip('passlib', reason="optional external dependency not installed")
from medical_app.infrastructure.bootstrap.di_container import DIContainer
from genesis_medical.domain.entities.patient import PatientProfile
from genesis_medical.domain.entities.parameter import Parameter
from genesis_medical.domain.value_objects.unit import Unit
from genesis_medical.domain.value_objects.gender import Gender

@pytest.mark.integration
def test_gender_thresholds_creatinine_affects_probability():
    container = DIContainer()
    male = PatientProfile(id="M", gender=Gender.MALE, age=40)
    female = PatientProfile(id="F", gender=Gender.FEMALE, age=40)

    params = [
        Parameter("creatinine", 110, Unit("umol/L")),
        Parameter("egfr", 45, Unit("mL/min/1.73m2")),
        Parameter("urea", 6, Unit("mmol/L"))
    ]

    findings_male = container.inference_engine.infer(male, params)
    findings_female = container.inference_engine.infer(female, params)

    kidney_ids_male = {"creatinine_high_male", "chronic_kidney_disease"}
    kidney_ids_female = {"creatinine_high_female", "chronic_kidney_disease"}

    male_kidney = [f for f in findings_male if f.id in kidney_ids_male and f.probability > 0]
    female_kidney = [f for f in findings_female if f.id in kidney_ids_female and f.probability > 0]

    male_prob_sum = sum(f.probability for f in male_kidney)
    female_prob_sum = sum(f.probability for f in female_kidney)

    assert female_prob_sum > male_prob_sum, "Female should have higher kidney disease probability due to elevated creatinine"

@pytest.mark.integration
def test_gender_thresholds_hemoglobin_no_finding_for_female():
    container = DIContainer()
    male = PatientProfile(id="M", gender=Gender.MALE, age=40)
    female = PatientProfile(id="F", gender=Gender.FEMALE, age=40)

    params = [Parameter("hemoglobin", 125, Unit("g/L"))]

    findings_male = container.inference_engine.infer(male, params)
    findings_female = container.inference_engine.infer(female, params)

    male_has = any(f.id == "anemia_male" and f.probability > 0 for f in findings_male)
    female_has = any(f.id == "anemia_female" and f.probability > 0 for f in findings_female)

    assert male_has, "Male should have anemia finding due to low hemoglobin"
    assert not female_has, "Female should have no anemia finding from hemoglobin 125 (within normal range)"
