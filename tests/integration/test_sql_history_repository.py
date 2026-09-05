import pytest
import os
from medical_app.infrastructure.adapters.storage.sql_history_repository import SqlHistoryRepository
from genesis_medical.domain.entities.report import AnalysisReport
from genesis_medical.domain.entities.finding import ClinicalFinding
from genesis_medical.domain.entities.recommendation import Recommendation
from genesis_medical.domain.value_objects.risk_level import RiskLevel
from genesis_medical.domain.value_objects.severity import Severity

@pytest.fixture
def db_path(tmp_path):
    return str(tmp_path / "test_history.db")

@pytest.fixture
def repo(db_path):
    return SqlHistoryRepository(db_path)

def test_save_and_load(repo):
    # РЎРѕР·РґР°С‘Рј С‚РµСЃС‚РѕРІС‹Р№ РѕС‚С‡С‘С‚
    finding = ClinicalFinding(
        id="F1",
        title="Anemia",
        probability=0.9,
        risk=RiskLevel.HIGH,
        doctor_specialty="Hematologist",
        tests=["Iron"],
        evidence=["Low ferritin"],
        excluded_by=[]
    )
    action = Recommendation(
        doctor_specialty="Hematologist",
        urgency=Severity.MODERATE,
        additional_tests=["B12", "Folate"]
    )
    report = AnalysisReport(
        findings=[finding],
        actions=[action],
        explanation="Test explanation"
    )

    # РЎРѕС…СЂР°РЅСЏРµРј
    repo.save("P123", report)

    # Р—Р°РіСЂСѓР¶Р°РµРј
    loaded = repo.load("P123")
    assert loaded is not None
    assert len(loaded.findings) == 1
    assert loaded.findings[0].id == "F1"
    assert loaded.findings[0].risk == RiskLevel.HIGH
    assert loaded.actions[0].urgency == Severity.MODERATE
    assert loaded.explanation == "Test explanation"

    # РџСЂРѕРІРµСЂСЏРµРј РЅРµСЃСѓС‰РµСЃС‚РІСѓСЋС‰РµРіРѕ РїР°С†РёРµРЅС‚Р°
    none_report = repo.load("UNKNOWN")
    assert none_report is None

def test_multiple_saves(repo):
    # РЎРѕС…СЂР°РЅСЏРµРј РґРІР° РѕС‚С‡С‘С‚Р° РґР»СЏ РѕРґРЅРѕРіРѕ РїР°С†РёРµРЅС‚Р°
    report1 = AnalysisReport(findings=[], actions=[], explanation="First")
    report2 = AnalysisReport(findings=[], actions=[], explanation="Second")
    repo.save("P1", report1)
    repo.save("P1", report2)
    loaded = repo.load("P1")
    assert loaded.explanation == "Second"  # РґРѕР»Р¶РµРЅ Р·Р°РіСЂСѓР·РёС‚СЊСЃСЏ РїРѕСЃР»РµРґРЅРёР№
