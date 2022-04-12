import pytest
from datetime import datetime

from mergesvp.lib.process import SvpSource, parse_svp_line
from mergesvp.lib.errors import SvpParsingException

def test_svpsource_class():
    """ Simple test case, checks if values passed to the constructor
    are assigned correctly to the instance """
    fn = 'a.txt'
    ts = datetime.now()
    lat = 123.0
    lng = 321.0

    test_svp = SvpSource(fn, ts, lat, lng)
    assert test_svp.filename == fn
    assert test_svp.timestamp == ts
    assert test_svp.longitude == lng
    assert test_svp.latitude == lat


def test_parse_svp_line():
    """Check parsing of a valid svp line"""
    raw_data = [
        'V000013.TXT',
        '31/05/2015 06:37:34',
        '-12.24555556',
        '130.90583330'
    ]

    test_svp = parse_svp_line(raw_data)
    assert test_svp.filename == 'V000013.TXT'
    assert test_svp.timestamp == datetime(2015,5,31,6,37,34)
    assert test_svp.latitude == -12.24555556
    assert test_svp.longitude == 130.90583330
    

def test_parse_svp_bad_date():
    """Check that a bad date format raises the correct exception"""
    raw_data = [
        'V000013.TXT',
        '3ahgdjhasjh1/05/2015 06:37:34',
        '-12.24555556',
        '130.90583330'
    ]

    with pytest.raises(SvpParsingException):
        test_svp = parse_svp_line(raw_data)


def test_parse_svp_bad_latitude():
    """Check that a bad latitude format raises the correct exception"""
    raw_data = [
        'V000013.TXT',
        '31/05/2015 06:37:34',
        'a',
        '130.90583330'
    ]

    with pytest.raises(SvpParsingException):
        test_svp = parse_svp_line(raw_data)
