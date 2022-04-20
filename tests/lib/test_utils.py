import pytest

from mergesvp.lib.utils import decimal_to_dms, dms_to_decimal


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
