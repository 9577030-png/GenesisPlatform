from genesis_medical.parsers.unit_converter import convert

def test_convert():
    assert convert(10, 2.5) == 25.0
    assert convert(0, 100) == 0
