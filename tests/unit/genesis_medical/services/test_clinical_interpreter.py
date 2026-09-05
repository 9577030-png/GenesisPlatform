from genesis_medical.domain.entities.parameter import Parameter
from genesis_medical.domain.entities.patient import PatientProfile
from genesis_medical.domain.value_objects.gender import Gender
from genesis_medical.domain.value_objects.unit import Unit
from genesis_medical.services import ClinicalInterpreter


def test_clinical_interpreter_loads_bundled_knowledge() -> None:
    interpreter = ClinicalInterpreter(
        ""
    )
    interpreter.interpretations = {
        "demo": {
            "label": "Demo",
            "category": "test",
            "criteria": [
                {
                    "parameter": "glucose",
                    "unit": "mmol/L",
                    "comment_template": "value={value}",
                }
            ],
        }
    }

    patient = PatientProfile("P1", Gender.MALE, 30)
    result = interpreter.interpret(
        [{"id": "demo"}],
        [Parameter("glucose", 5.0, Unit("mmol/L"))],
        patient,
    )

    assert result["demo"].label == "Demo"
    assert result["demo"].criteria[0].value == 5.0
