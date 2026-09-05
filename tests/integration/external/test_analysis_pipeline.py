import pytest
pytest.importorskip('redis', reason="optional external dependency not installed")
pytestmark = pytest.mark.external
pytest.importorskip('redis', reason="optional external dependency not installed")
from unittest.mock import Mock

from genesis_medical.domain.entities.patient import PatientProfile
from genesis_medical.domain.entities.parameter import Parameter
from genesis_medical.domain.entities.finding import ClinicalFinding
from genesis_medical.domain.entities.recommendation import Recommendation
from genesis_medical.domain.entities.report import AnalysisReport
from genesis_medical.domain.value_objects.gender import Gender
from genesis_medical.domain.value_objects.unit import Unit
from genesis_medical.domain.value_objects.risk_level import RiskLevel
from genesis_medical.domain.value_objects.severity import Severity

from medical_app.application.services.analysis_pipeline import AnalysisPipeline


def test_analysis_pipeline():
    # РЎРѕР·РґР°С‘Рј РјРѕРєРё РІСЃРµС… Р·Р°РІРёСЃРёРјРѕСЃС‚РµР№
    parser = Mock()
    inference_engine = Mock()
    action_mapper = Mock()
    report_builder = Mock()
    history_repo = Mock()
    renderer = Mock()

    # РќР°СЃС‚СЂР°РёРІР°РµРј РїРѕРІРµРґРµРЅРёРµ
    parameters = [Parameter("Hb", 100, Unit("g/L"))]
    parser.parse.return_value = parameters

    findings = [ClinicalFinding(id="F1", title="Anemia", probability=0.9, risk=RiskLevel.HIGH)]
    inference_engine.infer.return_value = findings

    actions = [Recommendation(
        doctor_specialty="Hematologist",
        urgency=Severity.MODERATE,
        additional_tests=[]
    )]
    action_mapper.map_to_actions.return_value = actions

    report = AnalysisReport(findings=findings, actions=actions, explanation="Test")
    report_builder.build.return_value = report

    renderer.render.return_value = "Rendered report"

    pipeline = AnalysisPipeline(
        parser, inference_engine, action_mapper, report_builder, history_repo, renderer
    )

    patient = PatientProfile(id="P1", gender=Gender.MALE, age=30)
    result = pipeline.run(patient, "some raw text")

    # РџСЂРѕРІРµСЂСЏРµРј РІС‹Р·РѕРІС‹
    parser.parse.assert_called_once_with("some raw text")
    inference_engine.infer.assert_called_once_with(patient, parameters)
    action_mapper.map_to_actions.assert_called_once_with(findings)
    report_builder.build.assert_called_once_with(findings, actions)
    history_repo.save.assert_called_once_with("P1", report)
    renderer.render.assert_called_once_with(report)

    assert result == "Rendered report"
