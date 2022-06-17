import pytest

from mergesvp.lib.carisprocess import \
    depth_speed_compare, group_by_depth_speed

from tests.lib.mock_data import svp_1, svp_2, svp_3


def test_depth_speed_compare():
    assert depth_speed_compare(svp_1.depth_speed, svp_2.depth_speed) == True
    assert depth_speed_compare(svp_1.depth_speed, svp_3.depth_speed) == False


def test_group_svps():
    
    svps = [svp_1, svp_2, svp_3]

    groups = group_by_depth_speed(svps)

    assert len(groups) == 2
    assert svp_1 in groups[0]
    assert svp_2 in groups[0]
    assert svp_3 in groups[1]
