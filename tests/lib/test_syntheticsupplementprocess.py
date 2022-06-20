from datetime import timedelta
from tests.lib.mock_data import svp_1, svp_2, svp_3, svp_4
from mergesvp.lib.syntheticsupplementprocess import \
    find_gaps, \
    get_supplement_coords


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
    supplement_coords = get_supplement_coords(svp_1, svp_2, 0.5)

    assert len(supplement_coords) == 2

    coords_1 = supplement_coords[0]
    coords_2 = supplement_coords[1]

    assert coords_1[0] == svp_1.timestamp + timedelta(hours=0.5)

    assert coords_2[0] == svp_1.timestamp + 2 * timedelta(hours=0.5)


