from datetime import datetime
import pytest

from mergesvp.lib.utils import \
    decimal_to_dms, \
    dms_to_decimal, \
    _get_all_dives, \
    trim_to_longest_dive, \
    sort_svp_list, \
    timedelta_to_hours, \
    lerp

from tests.lib.mock_data import svp_1, svp_2, svp_3

def test_dms_to_decimal():
    degrees = 12
    minutes = 14
    seconds = 35

    decimal = dms_to_decimal(degrees, minutes, seconds)
    assert decimal == pytest.approx(12.24305556)


def test_dms_to_decimal_neg():
    """ tests negative values in degrees for conversion as there is a
    gotcha with the sign"""

    degrees = -12  
    minutes = 14
    seconds = 35

    decimal = dms_to_decimal(degrees, minutes, seconds)
    assert decimal == pytest.approx(-12.24305556)


def test_decimal_to_dms():

    decimal = 12.24305556
    
    degrees, minutes, seconds = decimal_to_dms(decimal)

    assert degrees == 12
    assert minutes == 14
    assert seconds == pytest.approx(35)


def test_decimal_to_dms_neg():
    """ tests negative values in degrees for conversion as there is a
    gotcha with the sign"""
    decimal = -12.24305556

    degrees, minutes, seconds = decimal_to_dms(decimal)

    assert degrees == -12
    assert minutes == 14
    assert seconds == pytest.approx(35)


def test_get_all_dives():
    # note the actual sound speed has no impact on this function, so we
    # just use the same speed value because it's easier to copy/paste
    svp_data = [
        (0.0, 0.1),
        (0.3, 0.1),  # dive 1
        (0.1, 0.1),  # dive 2
        (0.0, 0.1),
        (0.1, 0.1),
        (0.2, 0.1),
        (1.0, 0.1),
        (1.3, 0.1),  # dive 3
        (1.2, 0.1),  # dive 4
        (0.9, 0.1),  # dive 5
        (0.8, 0.1),  # dive 6
        (0.2, 0.1),  # dive 7
        (0.1, 0.1),  # dive 8
    ]

    all_dives = _get_all_dives(svp_data)
    assert len(all_dives) == 8

    dive_1 = all_dives[0]
    assert dive_1[0][0] == 0.0
    assert dive_1[1][0] == 0.3

    dive_3 = all_dives[2]
    assert dive_3[0][0] == 0.0
    assert dive_3[1][0] == 0.1
    assert dive_3[len(dive_3) - 1][0] == 1.3


def test_trim_to_longest_dive():
    # note the actual sound speed has no impact on this function, so we
    # just use the same speed value because it's easier to copy/paste
    svp_data = [
        (0.0, 0.1),
        (0.3, 0.1),  # dive 1
        (0.1, 0.1),  # dive 2
        (0.0, 0.1),
        (0.1, 0.1),
        (0.2, 0.1),
        (1.0, 0.1),
        (1.3, 0.1),  # dive 3
        (1.2, 0.1),  # dive 4
        (0.9, 0.1),  # dive 5
        (0.8, 0.1),  # dive 6
        (0.2, 0.1),  # dive 7
        (0.1, 0.1),  # dive 8
    ]

    longest_dive = trim_to_longest_dive(svp_data)
    assert len(longest_dive) == 5


def test_svps_sorting():
    svps = [svp_2, svp_3, svp_1]

    sorted_svps = sort_svp_list(svps)

    assert sorted_svps[0] == svp_1
    assert sorted_svps[1] == svp_2
    assert sorted_svps[2] == svp_3


def test_timedelta_to_hours():
    d1 = datetime(2022, 6, 17, 1, 30, 0)
    d2 = datetime(2022, 6, 17, 2, 00, 0)
    d3 = datetime(2022, 6, 18, 2, 00, 0)

    dt21 = d2 - d1
    dt31 = d3 - d1

    assert timedelta_to_hours(dt21) == 0.5
    assert timedelta_to_hours(dt31) == 24.5


def test_lerp():
    assert lerp(5, 10, 0.5) == 7.5
    assert lerp(5, 15, 0.25) == 7.5
    assert lerp(5, 15, 0.75) == 12.5
