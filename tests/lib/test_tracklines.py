import pytest
from datetime import datetime

from mergesvp.lib.tracklines import \
    TracklinesParser, \
    TracklinePoint, \
    Trackline


def test_parse_line():
    line = "8/1/20,10:24:52.562,0000_20200801_102451_FK200804_EM710,146.1588473,-16.7456360,58.726"

    parser = TracklinesParser()
    tl_id, tl_pt = parser._process_line(line)

    assert tl_id == '0000_20200801_102451_FK200804_EM710'
    
    assert tl_pt.timestamp == datetime(2020,8,1,10,24,52,562000)
    assert tl_pt.latitude == -16.7456360
    assert tl_pt.longitude == 146.1588473
    assert tl_pt.depth == 58.726


def test_parse_lines():
    lines = [
        "8/1/20,10:24:52.562,0000_20200801_102451_FK200804_EM710,146.1588473,-16.7456360,58.726",
        "8/1/20,10:24:52.562,0000_20200801_102451_FK200804_EM710,146.1588526,-16.7456300,58.626",
        "8/1/20,10:24:52.874,0000_20200801_102451_FK200804_EM710,146.1588615,-16.7456253,58.644",
        "8/1/20,10:24:52.875,0000_20200801_102451_FK200804_EM710,146.1588668,-16.7456194,58.693",
        "8/4/20,21:59:10.710,0079_20200804_214711_FK200804_EM710,146.1261428,-16.7575014,55.086",
        "8/4/20,21:59:11.007,0079_20200804_214711_FK200804_EM710,146.1261365,-16.7575085,55.163",
        "8/4/20,21:59:11.009,0079_20200804_214711_FK200804_EM710,146.1261314,-16.7575147,55.098",
        "8/4/20,21:59:11.305,0079_20200804_214711_FK200804_EM710,146.1261253,-16.7575218,55.036",
        "8/27/20,23:04:32.134,0493_20200827_223127_FK200804_EM710,153.5227069,-22.1081210,372.932",
        "8/27/20,23:04:33.665,0493_20200827_223127_FK200804_EM710,153.5227762,-22.1081632,373.379",
        "8/27/20,23:04:33.709,0493_20200827_223127_FK200804_EM710,153.5227695,-22.1081918,373.136",
        "8/27/20,23:04:35.240,0493_20200827_223127_FK200804_EM710,153.5228547,-22.1082284,372.311",
        "8/27/20,23:04:35.283,0493_20200827_223127_FK200804_EM710,153.5228488,-22.1082570,372.008",
        "8/27/20,23:04:36.819,0493_20200827_223127_FK200804_EM710,153.5228475,-22.1083012,372.499",
    ]

    parser = TracklinesParser()
    parser._process_lines(lines)

    tracklines = parser.tracklines

    # they are three unique tracklines in the above array, denoted by the differing
    # line ids (third column)
    assert len(tracklines) == 3

    assert tracklines[0].line_id == '0000_20200801_102451_FK200804_EM710'
    assert len(tracklines[0].points) == 4

    assert tracklines[1].line_id == '0079_20200804_214711_FK200804_EM710'
    assert len(tracklines[1].points) == 4

    assert tracklines[2].line_id == '0493_20200827_223127_FK200804_EM710'
    assert len(tracklines[2].points) == 6


def test_trackline_is_in():
    lines = [
        "8/27/20,20:04:35.240,0493_20200827_223127_FK200804_EM710,153.5228547,-22.1082284,372.311",
        "8/27/20,21:04:35.283,0493_20200827_223127_FK200804_EM710,153.5228488,-22.1082570,372.008",
        "8/27/20,22:04:36.819,0493_20200827_223127_FK200804_EM710,153.5228475,-22.1083012,372.499",
    ]
    parser = TracklinesParser()
    parser._process_lines(lines)
    trackline = parser.tracklines[0]

    # this one is in the trackline start and end
    to_check_timestamp = datetime(2020,8,27,21,0,0)
    assert trackline.is_in(to_check_timestamp) == True

    # is before the trackline
    to_check_timestamp = datetime(2020, 8, 27, 19, 59, 59)
    assert trackline.is_in(to_check_timestamp) == False

    # is after the trackline
    to_check_timestamp = datetime(2020, 8, 27, 22, 4, 37)
    assert trackline.is_in(to_check_timestamp) == False
    

def test_trackline_point_lerp():
    pt1 = TracklinePoint(
        datetime(2000, 1, 1, 12, 0, 0),
        20,
        30,
        200
    )
    pt2 = TracklinePoint(
        datetime(2000, 1, 2, 12, 0, 0),
        60,
        10,
        210
    )

    # based on time this is exactly in the middle of the two points
    pt_lerp = pt1.lerp(
        pt2,
        datetime(2000, 1, 2, 0, 0, 0)
    )
    assert pt_lerp.latitude == 40
    assert pt_lerp.longitude == 20
    assert pt_lerp.depth == 205

    # based on time this is exactly 3/4 of the way between the two points
    pt_lerp = pt1.lerp(
        pt2,
        datetime(2000, 1, 2, 6, 0, 0)
    )
    assert pt_lerp.latitude == 50
    assert pt_lerp.longitude == 15
    assert pt_lerp.depth == 207.5


def test_trackline_lerp():
    pt1 = TracklinePoint(
        datetime(2000, 1, 1, 12, 0, 0),
        20,
        30,
        200
    )
    pt2 = TracklinePoint(
        datetime(2000, 1, 2, 12, 0, 0),
        60,
        10,
        210
    )
    pt3 = TracklinePoint(
        datetime(2000, 1, 3, 12, 0, 0),
        60,
        10,
        210
    )

    trackline = Trackline(None, None)
    trackline.points = [pt1, pt2, pt3]

    # based on time this is exactly 3/4 of the way between the first 
    # two points
    pt_lerp = trackline.get_lerp_point(
        datetime(2000, 1, 2, 6, 0, 0)
    )
    assert pt_lerp.latitude == 50
    assert pt_lerp.longitude == 15
    assert pt_lerp.depth == 207.5
