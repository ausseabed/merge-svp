# collection of some mock data used across multiple unit tests

from datetime import datetime
from mergesvp.lib.svpprofile import SvpProfile

# svp_1 and svp_2 are identical, svp_3 is different
svp_1 = SvpProfile(
    timestamp=datetime(2015, 6, 1, 1, 11, 11),
    depth_speed=[
        (0.0, 0.0),
        (1.1, 1.1),
        (2.2, 1.2),
        (3.3, 1.3),
        (4.4, 1.4),
        (5.5, 1.5),
    ]
)

svp_2 = SvpProfile(
    timestamp=datetime(2015, 6, 1, 2, 11, 12),
    depth_speed=[
        (0.0, 0.0),
        (1.1, 1.1),
        (2.2, 1.2),
        (3.3, 1.3),
        (4.4, 1.4),
        (5.5, 1.5),
    ]
)

svp_3 = SvpProfile(
    timestamp=datetime(2015, 6, 1, 2, 45, 13),
    depth_speed=[
        (0.0, 0.0),
        (1.1, 1.1),
        (2.2, 1.2),
        (3.3, 1.3),
        (4.4, 1.45),
        (5.5, 1.5),
    ]
)

svp_4 = SvpProfile(
    timestamp=datetime(2015, 6, 2, 2, 46, 13),
    depth_speed=[
        (0.0, 0.0),
        (1.1, 1.9),
        (2.2, 2.2),
        (3.3, 2.3),
        (4.4, 2.45),
        (5.5, 2.5),
    ]
)
