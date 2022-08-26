import pytest
from datetime import datetime, timedelta
from mergesvp.lib.svpprofile import SvpProfile
from mergesvp.lib.tracklines import Trackline, TracklinePoint
from tests.lib.mock_data import svp_1, svp_2, svp_3, svp_4
from mergesvp.lib.syntheticprocess import \
    SyntheticSvpProcessor

def test_validate_tracklines():
    

    tl1_pt1 = TracklinePoint(
        datetime(2000, 1, 1, 12, 0, 0),
        20,
        30,
        200
    )
    tl1_pt2 = TracklinePoint(
        datetime(2000, 1, 2, 12, 0, 0),
        60,
        10,
        210
    )
    tl1_pt3 = TracklinePoint(
        datetime(2000, 1, 3, 12, 0, 0),
        60,
        30,
        220
    )
    trackline1 = Trackline(None, None)
    trackline1.points = [tl1_pt1, tl1_pt2, tl1_pt3]

    processor = SyntheticSvpProcessor(None, None, None, None, None)
    processor.trackline = trackline1

    # should pass without exception
    processor._validate_trackline()

    tl1_pt1.timestamp = datetime(2000, 1, 3, 12, 0, 0)

    # should fail with exception as the timestamp of the first point is after
    # the second point
    with pytest.raises(RuntimeError) as e_info:
        processor._validate_trackline()


def test_get_svp_times():

    tl1_pt1 = TracklinePoint(
        datetime(2000, 1, 1, 12, 0, 0),
        20,
        30,
        200
    )
    tl1_pt2 = TracklinePoint(
        datetime(2000, 1, 2, 12, 0, 0),
        60,
        10,
        210
    )
    trackline1 = Trackline(None, None)
    trackline1.points = [tl1_pt1, tl1_pt2]

    processor = SyntheticSvpProcessor(None, None, None, None, None)
    processor.trackline = trackline1
    processor.time_gap = 1

    svp_times = processor._get_svp_times()

    # 24hours between start and end, but there's an SVP point at the
    # start and end (hence 25, and not 24)
    assert len(svp_times) == 25

