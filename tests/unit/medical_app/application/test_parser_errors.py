import pytest
from genesis_medical.parsers.regex_parser import RegexParser
from genesis_medical.domain.exceptions import ParsingError

def test_parser_handles_empty_text():
    parser = RegexParser()
    with pytest.raises(ParsingError, match="empty"):
        parser.parse("")

def test_parser_handles_invalid_lines_gracefully():
    parser = RegexParser()
    text = """Hb 120 g/L
    Invalid line without value
    Ferritin 30 ug/L
    """
    params = parser.parse(text)
    assert len(params) == 2
    names = [p.name for p in params]
    # РўРµРїРµСЂСЊ РєР°РЅРѕРЅРёС‡РµСЃРєРѕРµ РёРјСЏ 'hemoglobin' (Р° РЅРµ 'hb')
    assert "hemoglobin" in names
    assert "ferritin" in names

def test_parser_handles_negative_values():
    parser = RegexParser()
    text = "Hb -10 g/L"
    with pytest.raises(ParsingError, match="No valid parameters"):
        parser.parse(text)
