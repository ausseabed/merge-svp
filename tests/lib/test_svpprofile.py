import pytest
from datetime import datetime

from mergesvp.lib.svpprofile import \
    SvpProfile, \
    _parse_l0_header_line, \
    _parse_l0_body_line, \
    _parse_l3_header_line, \
    _parse_l3_body_line


def test_parse_l0_header_line():

    lines = [
        "Now: 28/05/2015 23:49:31",
        "Battery Level: 1.4V",
        "MiniSVP: S/N 34826",
        "Site info: DARWIN HARBOUR",
        "Calibrated: 10/01/2011",
        "Latitude: -12 14 35 S",
        "Longtitude: 130 55 40 E",
        "Mode: P2.000000e-1",
        "Tare: 10.0854",
        "Pressure units: dBar",
    ]

    svp = SvpProfile()
    for line in lines:
        _parse_l0_header_line(line, svp)
        
    assert svp.timestamp == datetime(2015, 5, 28, 23, 49, 31)
    assert svp.latitude == pytest.approx(-12.24306)
    assert svp.longitude == pytest.approx(130.9278)


def test_parse_l0_header_line():

    lines = [
        "00.040	24.047	0000.000",
        "00.202	26.599	1539.508",
        "00.400	26.911	1539.485",
    ]

    svp = SvpProfile()
    for line in lines:
        _parse_l0_body_line(line, svp)

    # a few spot checks of the data
    assert svp.depth_speed[0][0] == 0.04
    assert svp.depth_speed[1][1] == 1539.508
    assert svp.depth_speed[2][0] == 0.4
    assert len(svp.depth_speed) == 3


def test_parse_l3_header_line():
    line = "( SoundVelocity  1.0 0 201505282349 -12.24305556 130.92777780 -1 0 0 SSM_2021.1.7 P 0088 )"

    svp = SvpProfile()
    _parse_l3_body_line(line, svp)

    assert svp.timestamp == datetime(2015, 5, 28, 23, 49, 00)
    assert svp.latitude == pytest.approx(-12.24305556)
    assert svp.longitude == pytest.approx(130.92777780)


def test_parse_l3_header_line():

    lines = [
        "0.00 1539.51",
        "0.20 1539.51",
        "0.40 1539.48",
    ]

    svp = SvpProfile()
    for line in lines:
        _parse_l3_body_line(line, svp)

    # a few spot checks of the data
    assert svp.depth_speed[0][0] == 0.00
    assert svp.depth_speed[1][1] == 1539.51
    assert svp.depth_speed[2][0] == 0.4
    assert len(svp.depth_speed) == 3
