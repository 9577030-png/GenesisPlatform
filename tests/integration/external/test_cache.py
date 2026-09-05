import pytest
pytest.importorskip('redis', reason="optional external dependency not installed")
pytestmark = pytest.mark.external
pytest.importorskip('redis', reason="optional external dependency not installed")
from unittest.mock import MagicMock
from genesis_medical.domain.entities.patient import PatientProfile
from genesis_medical.domain.entities.parameter import Parameter
from genesis_medical.domain.entities.finding import ClinicalFinding
from genesis_medical.domain.entities.report import AnalysisReport
from genesis_medical.domain.value_objects.gender import Gender
from genesis_medical.domain.value_objects.unit import Unit
from genesis_medical.domain.value_objects.risk_level import RiskLevel
from medical_app.infrastructure.cache.redis_cache import RedisCache
from medical_app.infrastructure.repositories.audit_repository import AuditRepository
from medical_app.application.ports.rule_repository import RuleRepository
from genesis_medical.services import PhysiologicalValidator
from medical_app.application.services.inference_engine import InferenceEngine
from genesis_medical.services import ActionMapper
from genesis_medical.services import ReportBuilder
from genesis_medical.services import PostProcessor
from medical_app.application.services.analysis_pipeline import AnalysisPipeline
from medical_app.application.ports.parser_interface import ParserInterface
from medical_app.application.ports.history_repository import HistoryRepository
from medical_app.application.ports.renderer_interface import RendererInterface

@pytest.mark.integration
def test_cache_hit_does_not_raise_name_error():
    # РњРѕРєР°РµРј РІСЃРµ Р·Р°РІРёСЃРёРјРѕСЃС‚Рё
    parser = MagicMock(spec=ParserInterface)
    parser.parse.return_value = [Parameter("glucose", 10.0, Unit("mmol/L"))]

    inference_engine = MagicMock(spec=InferenceEngine)
    inference_engine.infer.return_value = []

    action_mapper = MagicMock(spec=ActionMapper)
    action_mapper.map_to_actions.return_value = []

    report_builder = MagicMock(spec=ReportBuilder)
    report_builder.build.return_value = AnalysisReport(findings=[], actions=[], explanation="Test")

    history_repo = MagicMock(spec=HistoryRepository)
    renderer = MagicMock(spec=RendererInterface)
    post_processor = MagicMock(spec=PostProcessor)
    post_processor.process.return_value = {"diagnoses": []}

    # РњРѕРєР°РµРј РєСЌС€ вЂ“ РІРѕР·РІСЂР°С‰Р°РµРј Р·Р°РєСЌС€РёСЂРѕРІР°РЅРЅС‹Р№ СЂРµР·СѓР»СЊС‚Р°С‚
    cache = MagicMock(spec=RedisCache)
    cache.get.return_value = {
        "findings": [{"id": "F1", "title": "Test", "probability": 0.9, "risk": 3, "evidence": [], "description": ""}],
        "actions": [{"doctor_specialty": "Hematologist", "urgency": "moderate", "additional_tests": []}],
        "explanation": "Cached explanation"
    }

    audit_repo = MagicMock(spec=AuditRepository)
    rule_repo = MagicMock(spec=RuleRepository)
    validator = MagicMock(spec=PhysiologicalValidator)
    validator.validate.return_value = []

    pipeline = AnalysisPipeline(
        parser=parser,
        inference_engine=inference_engine,
        action_mapper=action_mapper,
        report_builder=report_builder,
        history_repo=history_repo,
        renderer=renderer,
        post_processor=post_processor,
        cache=cache,
        audit_repo=audit_repo,
        rule_repo=rule_repo,
        validator=validator
    )

    patient = PatientProfile(id="P1", gender=Gender.MALE, age=30)
    report = pipeline.run_structured(patient, "glucose 10.0", user_id=1)

    # РџСЂРѕРІРµСЂСЏРµРј, С‡С‚Рѕ РѕС‚С‡С‘С‚ СЃРѕР±СЂР°РЅ РёР· РєСЌС€Р° Р±РµР· РѕС€РёР±РѕРє
    assert report.explanation == "Cached explanation"
    assert len(report.findings) == 1
    assert report.findings[0].id == "F1"
    # РЈР±РµР¶РґР°РµРјСЃСЏ, С‡С‚Рѕ РјРµС‚РѕРґС‹, РєРѕС‚РѕСЂС‹Рµ РЅРµ РґРѕР»Р¶РЅС‹ РІС‹Р·С‹РІР°С‚СЊСЃСЏ, РЅРµ РІС‹Р·РІР°РЅС‹
    inference_engine.infer.assert_not_called()
