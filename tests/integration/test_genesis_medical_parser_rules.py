import pytest
from genesis_medical.parsers.regex_parser import RegexParser

@pytest.mark.integration
def test_parser_handles_tsh():
    parser = RegexParser()
    text = "TSH 5.2 mU/L"
    params = parser.parse(text)
    assert len(params) == 1
    assert params[0].name == "tsh"
    assert params[0].value == 5.2

@pytest.mark.integration
def test_parser_handles_potassium():
    parser = RegexParser()
    text = "potassium 6.0 mmol/L"
    params = parser.parse(text)
    assert len(params) == 1
    assert params[0].name == "potassium"
    assert params[0].value == 6.0

@pytest.mark.integration
def test_parser_handles_t4():
    parser = RegexParser()
    text = "T4 10 pmol/L"
    params = parser.parse(text)
    assert len(params) == 1
    # Р”РѕР»Р¶РЅРѕ СЂР°СЃРїР°СЂСЃРёС‚СЊСЃСЏ РєР°Рє free_t4 СЃРѕ Р·РЅР°С‡РµРЅРёРµРј 10.0
    assert params[0].name == "free_t4"
    assert params[0].value == 10.0
