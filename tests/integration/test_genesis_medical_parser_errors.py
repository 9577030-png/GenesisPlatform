import pytest
from genesis_medical.parsers.regex_parser import RegexParser
from genesis_medical.domain.exceptions import ParsingError

@pytest.mark.integration
def test_parser_empty_text():
    parser = RegexParser()
    with pytest.raises(ParsingError, match="empty"):
        parser.parse("   ")

@pytest.mark.integration
def test_parser_negative_value():
    parser = RegexParser()
    text = "Hb -10 g/L"
    with pytest.raises(ParsingError, match="No valid parameters"):
        parser.parse(text)
