import pytest

from mergesvp.lib.carisprocess import depth_speed_compare, group_by_depth_speed
from mergesvp.lib.svpprofile import SvpProfile

# svp_1 and svp_2 are identical, svp_3 is different
svp_1 = SvpProfile(depth_speed=[
    (0.0, 0.0),
    (1.1, 1.1),
    (2.2, 1.2),
    (3.3, 1.3),
    (4.4, 1.4),
    (5.5, 1.5),
])

svp_2 = SvpProfile(depth_speed=[
    (0.0, 0.0),
    (1.1, 1.1),
    (2.2, 1.2),
    (3.3, 1.3),
    (4.4, 1.4),
    (5.5, 1.5),
])

svp_3 = SvpProfile(depth_speed=[
    (0.0, 0.0),
    (1.1, 1.1),
    (2.2, 1.2),
    (3.3, 1.3),
    (4.4, 1.45),
    (5.5, 1.5),
])


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
