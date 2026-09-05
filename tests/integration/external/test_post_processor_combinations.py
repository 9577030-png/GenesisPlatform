import pytest
pytest.importorskip('passlib', reason="optional external dependency not installed")
pytestmark = pytest.mark.external
pytest.importorskip('passlib', reason="optional external dependency not installed")
from medical_app.infrastructure.bootstrap.di_container import DIContainer
from genesis_medical.domain.entities.finding import ClinicalFinding
from genesis_medical.domain.value_objects.risk_level import RiskLevel
from genesis_medical.domain.entities.report import AnalysisReport

@pytest.mark.integration
def test_combination_primary_hyperparathyroidism():
    container = DIContainer()
    findings = [
        ClinicalFinding(id="hypercalcemia", title="Hypercalcemia", probability=0.8, risk=RiskLevel.HIGH),
        ClinicalFinding(id="vitamin_d_deficiency", title="Vitamin D deficiency", probability=0.7, risk=RiskLevel.HIGH)
    ]
    report = AnalysisReport(findings=findings, actions=[], explanation="")
    result = container.post_processor.process(report)
    combined = [d for d in result["diagnoses"] if d.get("combined") and d["id"] == "primary_hyperparathyroidism"]
    assert len(combined) == 1

@pytest.mark.integration
def test_combination_hepatorenal_syndrome():
    container = DIContainer()
    findings = [
        ClinicalFinding(id="acute_kidney_injury", title="AKI", probability=0.6, risk=RiskLevel.HIGH),
        ClinicalFinding(id="acute_hepatitis", title="Acute hepatitis", probability=0.6, risk=RiskLevel.HIGH)
    ]
    report = AnalysisReport(findings=findings, actions=[], explanation="")
    result = container.post_processor.process(report)
    combined = [d for d in result["diagnoses"] if d.get("combined") and d["id"] == "hepatorenal_syndrome"]
    assert len(combined) == 1

@pytest.mark.integration
def test_combination_septic_syndrome():
    """
    РџСЂРѕРІРµСЂСЏРµС‚, С‡С‚Рѕ РєРѕРјР±РёРЅР°С†РёСЏ septic_syndrome РќР• СЃРѕР·РґР°С‘С‚СЃСЏ,
    РїРѕС‚РѕРјСѓ С‡С‚Рѕ systemic_inflammation РёСЃРєР»СЋС‡Р°РµС‚СЃСЏ РїСЂРё РЅР°Р»РёС‡РёРё sepsis (СЃРј. exclusions РІ clinical_logic.yaml).
    Р­С‚Рѕ РєРѕСЂСЂРµРєС‚РЅРѕРµ РїРѕРІРµРґРµРЅРёРµ СЃРёСЃС‚РµРјС‹.
    """
    container = DIContainer()
    findings = [
        ClinicalFinding(id="sepsis", title="Sepsis", probability=0.9, risk=RiskLevel.CRITICAL),
        ClinicalFinding(id="systemic_inflammation", title="Systemic inflammation", probability=0.7, risk=RiskLevel.HIGH)
    ]
    report = AnalysisReport(findings=findings, actions=[], explanation="")
    result = container.post_processor.process(report)
    combined = [d for d in result["diagnoses"] if d.get("combined") and d["id"] == "septic_syndrome"]
    assert len(combined) == 0, "Septic syndrome combination should not appear because systemic_inflammation is excluded"

@pytest.mark.integration
def test_combination_metabolic_bone_disease():
    container = DIContainer()
    findings = [
        ClinicalFinding(id="vitamin_d_deficiency", title="Vitamin D deficiency", probability=0.7, risk=RiskLevel.HIGH),
        ClinicalFinding(id="hypercalcemia", title="Hypercalcemia", probability=0.8, risk=RiskLevel.HIGH)
    ]
    report = AnalysisReport(findings=findings, actions=[], explanation="")
    result = container.post_processor.process(report)
    combined = [d for d in result["diagnoses"] if d.get("combined") and d["id"] == "metabolic_bone_disease"]
    assert len(combined) == 1
