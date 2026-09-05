import pytest
from unittest.mock import Mock
from genesis_medical.domain.entities.finding import ClinicalFinding
from genesis_medical.domain.entities.recommendation import Recommendation
from genesis_medical.domain.value_objects.risk_level import RiskLevel
from genesis_medical.domain.value_objects.severity import Severity
from genesis_medical.services import ActionMapper

def test_action_mapper():
    provider = Mock()
    rec = Recommendation(doctor_specialty="Hematologist", additional_tests=["Ferritin"], urgency=Severity.MODERATE)
    provider.get_recommendation.return_value = rec
    mapper = ActionMapper(provider)
    findings = [ClinicalFinding(id="G1", title="Test", probability=0.8, risk=RiskLevel.HIGH)]
    actions = mapper.map_to_actions(findings)
    assert len(actions) == 1
    assert actions[0] == rec
