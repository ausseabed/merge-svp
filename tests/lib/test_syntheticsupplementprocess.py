import pytest
from datetime import datetime, timedelta
from mergesvp.lib.svpprofile import SvpProfile
from mergesvp.lib.tracklines import Trackline, TracklinePoint
from tests.lib.mock_data import svp_1, svp_2, svp_3, svp_4
from mergesvp.lib.syntheticsupplementprocess import \
    find_gaps, \
    SyntheticSvpProcessor, \
    calc_interval


def test_find_gaps():
    svps = [svp_1, svp_2, svp_3, svp_4]

    gaps = find_gaps(svps, 1)

    assert len(gaps) == 2

    gap1 = gaps[0]
    assert gap1[0] == svp_1
    assert gap1[1] == svp_2
    assert gap1[2] == 1 + 1/60/60  # 1 hour and 1 second

    gap2 = gaps[1]
    assert gap2[0] == svp_3
    assert gap2[1] == svp_4
    assert gap2[2] == 24 + 1 / 60  # 1 day and 1 minute


def test_get_supplement_coords():
    processor = SyntheticSvpProcessor(None, None, None)

    # need to provide some rubbish trackline data so that the interpolation
    # process doesn't fail
    trackline = Trackline(None, None)
    trackline.append(TracklinePoint(datetime(1970, 1, 1), 10, 10, 10))
    trackline.append(TracklinePoint(datetime(3000, 1, 1), 10, 10, 10))
    processor.tracklines = [trackline]

    supplement_coords = processor._get_supplement_coords(svp_1, svp_2, 0.5)

    assert len(supplement_coords) == 2

    coords_1 = supplement_coords[0]
    coords_2 = supplement_coords[1]

    assert coords_1[0] == svp_1.timestamp + timedelta(hours=0.5)

    assert coords_2[0] == svp_1.timestamp + 2 * timedelta(hours=0.5)


def test_calc_interval():

    interval = calc_interval(svp_1, svp_2, 1)
    assert interval == pytest.approx(0.5, rel=1e-2)

## 
## The hyo2.abc.lib.gdal_aux.GdalAux function performs some interesting
## operations (removes env vars fr GDAL_DATA) that cause this test to
## fail when running on GitHub actions.
## 
# def test_processor_fill_gap():
#     t1 = datetime(2000, 1, 1, 0, 0, 0)
#     t2 = datetime(2000, 1, 2, 0, 0, 0)

#     trackline = Trackline(None, None)
#     trackline.append(TracklinePoint(t1, 10, 20, 30))
#     trackline.append(TracklinePoint(t2, 90, 40, 10))

#     svp1 = SvpProfile(None, t1)
#     svp2 = SvpProfile(None, t2)
#     svps = [svp1, svp2]

#     processor = SyntheticSvpProcessor(None, None, None)
#     processor.tracklines = [trackline]
#     processor.svps = svps
#     processor.time_threshold = 2

#     processor._fill_gaps()

#     # there should now be 11 new SVPs
#     assert len(processor.svps) == 13
#     # all new SVPs should be in between the initial SVPs
#     # we can check this by making sure the first and last
#     # items are still the same
#     assert processor.svps[0] == svp1
#     assert processor.svps[-1] == svp2
