from genesis_medical.domain.entities.finding import ClinicalFinding
from genesis_medical.domain.entities.recommendation import Recommendation
from genesis_medical.domain.value_objects.risk_level import RiskLevel
from genesis_medical.domain.value_objects.severity import Severity
from genesis_medical.services import ReportBuilder

def test_report_builder():
    findings = [ClinicalFinding(id="F1", title="Anemia", probability=0.9, risk=RiskLevel.HIGH)]
    actions = [Recommendation(doctor_specialty="Hematologist", additional_tests=["Iron"], urgency=Severity.MODERATE)]
    builder = ReportBuilder()
    report = builder.build(findings, actions)
    assert report.findings == findings
    assert report.actions == actions
    assert "Findings" in report.explanation
