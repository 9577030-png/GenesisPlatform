import pytest
from genesis_medical.domain.exceptions import (
    MedicalAIError,
    InvalidPatientDataError,
    InvalidParameterError,
    ParsingError,
    ConfigurationError
)
from genesis_medical.domain.entities.patient import PatientProfile
from genesis_medical.domain.entities.parameter import Parameter
from genesis_medical.domain.value_objects.gender import Gender
from genesis_medical.domain.value_objects.unit import Unit


def test_patient_validation_fails_on_negative_age():
    with pytest.raises(InvalidPatientDataError, match="Invalid age"):
        PatientProfile(id="P1", gender=Gender.MALE, age=-5)


def test_patient_validation_fails_on_empty_id():
    with pytest.raises(InvalidPatientDataError, match="Patient ID cannot be empty"):
        PatientProfile(id="", gender=Gender.MALE, age=30)


def test_patient_validation_fails_on_too_high_age():
    with pytest.raises(InvalidPatientDataError, match="Invalid age"):
        PatientProfile(id="P1", gender=Gender.MALE, age=200)


def test_parameter_validation_fails_on_empty_name():
    with pytest.raises(InvalidParameterError, match="Parameter name cannot be empty"):
        Parameter(name="", value=100, unit=Unit("g/L"))


def test_parameter_validation_fails_on_negative_value():
    with pytest.raises(InvalidParameterError, match="Invalid parameter value"):
        Parameter(name="Hb", value=-10, unit=Unit("g/L"))


def test_parameter_validation_fails_on_too_high_value():
    with pytest.raises(InvalidParameterError, match="Parameter value too high"):
        Parameter(name="Hb", value=20000, unit=Unit("g/L"))
