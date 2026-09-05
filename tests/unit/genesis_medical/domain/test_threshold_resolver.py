import pytest
from genesis_medical.domain.value_objects.unit import Unit
from genesis_medical.domain.value_objects.risk_level import RiskLevel
from genesis_medical.domain.entities.threshold import Threshold
from genesis_medical.domain.services.threshold_resolver import resolve

def test_resolve_without_overrides():
    """Р•СЃР»Рё overrides РїСѓСЃС‚, РІРѕР·РІСЂР°С‰Р°СЋС‚СЃСЏ С‚Рµ Р¶Рµ РїРѕСЂРѕРіРё."""
    global_thresholds = {
        "potassium": Threshold(
            parameter_name="potassium",
            low=3.5,
            high=5.0,
            unit=Unit("mmol/L"),
            risk_level=RiskLevel.HIGH
        ),
        "hemoglobin": Threshold(
            parameter_name="hemoglobin",
            low=120,
            high=160,
            unit=Unit("g/L"),
            risk_level=RiskLevel.HIGH
        )
    }
    result = resolve(global_thresholds, {})
    assert result == global_thresholds

def test_partial_override():
    """РџРµСЂРµРѕРїСЂРµРґРµР»СЏРµРј С‚РѕР»СЊРєРѕ high РґР»СЏ potassium, low РѕСЃС‚Р°С‘С‚СЃСЏ РёР· РіР»РѕР±Р°Р»СЊРЅРѕРіРѕ."""
    global_thresholds = {
        "potassium": Threshold(
            parameter_name="potassium",
            low=3.5,
            high=5.0,
            unit=Unit("mmol/L"),
            risk_level=RiskLevel.HIGH
        ),
        "hemoglobin": Threshold(
            parameter_name="hemoglobin",
            low=120,
            high=160,
            unit=Unit("g/L"),
            risk_level=RiskLevel.HIGH
        )
    }
    overrides = {
        "potassium": {"high": 5.5}
    }
    result = resolve(global_thresholds, overrides)
    # РџСЂРѕРІРµСЂСЏРµРј, С‡С‚Рѕ potassium.high СЃС‚Р°Р» 5.5, Р° low РѕСЃС‚Р°Р»СЃСЏ 3.5
    assert result["potassium"].high == 5.5
    assert result["potassium"].low == 3.5
    # hemoglobin РЅРµ РёР·РјРµРЅРёР»СЃСЏ
    assert result["hemoglobin"] == global_thresholds["hemoglobin"]

def test_full_override():
    """РџРµСЂРµРѕРїСЂРµРґРµР»СЏРµРј РІСЃРµ РїРѕР»СЏ РґР»СЏ РїР°СЂР°РјРµС‚СЂР°."""
    global_thresholds = {
        "potassium": Threshold(
            parameter_name="potassium",
            low=3.5,
            high=5.0,
            unit=Unit("mmol/L"),
            risk_level=RiskLevel.HIGH
        )
    }
    overrides = {
        "potassium": {
            "low": 3.0,
            "high": 6.0,
            "unit": Unit("mEq/L"),
            "risk_level": RiskLevel.CRITICAL
        }
    }
    result = resolve(global_thresholds, overrides)
    assert result["potassium"].low == 3.0
    assert result["potassium"].high == 6.0
    assert result["potassium"].unit == Unit("mEq/L")
    assert result["potassium"].risk_level == RiskLevel.CRITICAL
