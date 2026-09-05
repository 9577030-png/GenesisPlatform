import pytest
from unittest.mock import Mock
from datetime import datetime, UTC

from genesis_medical.domain.entities.patient import PatientProfile
from genesis_medical.domain.entities.parameter import Parameter
from genesis_medical.domain.value_objects.unit import Unit
from genesis_medical.domain.value_objects.risk_level import RiskLevel
from genesis_medical.domain.value_objects.gender import Gender
from medical_app.application.ports.rule_repository import RuleRepository
from genesis_medical.domain.rule_version import RuleVersion, RulePriority
from medical_app.application.services.inference_engine import InferenceEngine


@pytest.fixture
def rule_repo_mock():
    repo = Mock(spec=RuleRepository)

    rule = RuleVersion(
        version_id=1,
        rule_id="G1",
        name="Test rule",
        conditions=[
            {
                "id": "G1_condition",
                "parameter": "hb",
                "min": 90,
                "max": 110,
                "label": "Test finding",
                "scoring": 5,
                "risk": "HIGH",
            }
        ],
        actions=[],
        priority=RulePriority.MEDIUM,
        conflicts_with=[],
        supports=[],
        created_at=datetime.now(UTC),
        created_by="test",
        is_active=True,
        comment=None,
    )

    repo.get_active_versions.return_value = [rule]

    return repo


def test_inference_engine(rule_repo_mock):
    guideline_provider = Mock()
    threshold_provider = Mock()

    patient = PatientProfile(
        id="P1",
        gender=Gender.MALE,
        age=30,
    )

    parameters = [
        Parameter("Hb", 100, Unit("g/L"))
    ]

    engine = InferenceEngine(
        rule_repo_mock,
        threshold_provider,
        guideline_provider,
    )

    findings = engine.infer(
        patient,
        parameters,
    )

    assert len(findings) == 1

    finding = findings[0]

    assert finding.id == "G1_condition"
    assert finding.risk == RiskLevel.HIGH
    assert finding.probability > 0


def make_engine():
    return InferenceEngine(
        Mock(spec=RuleRepository),
        Mock(),
        Mock(),
    )



