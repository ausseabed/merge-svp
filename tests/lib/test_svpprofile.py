import pytest
from datetime import datetime

from mergesvp.lib.svpprofile import SvpProfile

def test_svpprofile():

    svp = SvpProfile(filename="fn", latitude=1.0, longitude=2.0)
    assert svp.filename == "fn"
    assert svp.latitude == 1.0
    assert svp.longitude == 2.0
