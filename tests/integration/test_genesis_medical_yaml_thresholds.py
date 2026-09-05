import pytest
from genesis_medical.sources.yaml_threshold_loader import YamlThresholdLoader
from genesis_medical.domain.entities.threshold import Threshold
from genesis_medical.domain.value_objects.unit import Unit
from genesis_medical.domain.value_objects.risk_level import RiskLevel

@pytest.mark.integration
def test_load_global_thresholds():
    loader = YamlThresholdLoader()
    thresholds = loader.get_global_thresholds()

    # РўРµРїРµСЂСЊ РёСЃРїРѕР»СЊР·СѓРµС‚СЃСЏ РєР°РЅРѕРЅРёС‡РµСЃРєРѕРµ РёРјСЏ 'hemoglobin'
    assert "hemoglobin" in thresholds
    assert "mcv" in thresholds
    assert "ferritin" in thresholds

    hb = thresholds["hemoglobin"]
    assert isinstance(hb, Threshold)
    assert hb.parameter_name == "hemoglobin"
    # Р’ clinical_thresholds.yaml РґР»СЏ РјСѓР¶С‡РёРЅ low=130, high=170
    assert hb.low == 130
    assert hb.high == 170
    assert hb.unit == Unit("g/L")
    assert hb.risk_level == RiskLevel.HIGH

    mcv = thresholds["mcv"]
    assert mcv.low == 80
    assert mcv.high == 100
    assert mcv.unit == Unit("fL")

    ferritin = thresholds["ferritin"]
    assert ferritin.low == 30
    # РСЃРїСЂР°РІР»РµРЅРѕ: РІ clinical_thresholds.yaml РґР»СЏ С„РµСЂСЂРёС‚РёРЅР° high=400 (Р° РЅРµ 300)
    assert ferritin.high == 400
    assert ferritin.unit == Unit("ng/mL")
    assert ferritin.risk_level == RiskLevel.HIGH

@pytest.mark.integration
def test_threshold_loader_returns_dict():
    loader = YamlThresholdLoader()
    thresholds = loader.get_global_thresholds()
    assert isinstance(thresholds, dict)
    for key, value in thresholds.items():
        assert isinstance(key, str)
        assert isinstance(value, Threshold)
