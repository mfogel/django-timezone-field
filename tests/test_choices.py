from datetime import datetime

import pytest

from timezone_field.choices import standard, with_gmt_offset


@pytest.fixture
def tzs1():
    # test timezones out of order, but they should appear in order in result.
    # avoiding an timezones that go through a Daylight Savings change here
    yield [
        "Asia/Kathmandu",  # 45 min off the hour
        "Asia/Kolkata",  # 30 min off the hour
        "America/Argentina/Buenos_Aires",  # on the hour
        "Asia/Qatar",  # on the hour
    ]


@pytest.fixture
def tzs2():
    # test timezones out of order, but they should appear in order in result.
    yield [
        "Europe/London",
        "Canada/Newfoundland",  # 30 min off the hour
        "America/Los_Angeles",  # on the hour
        "America/Santiago",  # southern hemisphere
    ]


@pytest.fixture
def tzs3_names():
    yield [
        "America/Los_Angeles",
        "Europe/London",
        "America/Argentina/Buenos_Aires",
    ]


@pytest.fixture
def tzs3_names_sorted():
    yield [
        "America/Argentina/Buenos_Aires",
        "America/Los_Angeles",
        "Europe/London",
    ]


@pytest.fixture
def tzs3_standard_displays():
    yield [
        "America/Argentina/Buenos Aires",
        "America/Los Angeles",
        "Europe/London",
    ]


def test_with_gmt_offset_using_timezone_names(tzs1, use_pytz):
    assert with_gmt_offset(tzs1, use_pytz=use_pytz) == [
        ("America/Argentina/Buenos_Aires", "GMT-03:00 America/Argentina/Buenos Aires"),
        ("Asia/Qatar", "GMT+03:00 Asia/Qatar"),
        ("Asia/Kolkata", "GMT+05:30 Asia/Kolkata"),
        ("Asia/Kathmandu", "GMT+05:45 Asia/Kathmandu"),
    ]


def test_with_gmt_offset_using_timezone_objects(tzs1, use_pytz, to_tzobj):
    tz_objects = [to_tzobj(name) for name in tzs1]
    assert with_gmt_offset(tz_objects, use_pytz=use_pytz) == [
        (
            to_tzobj("America/Argentina/Buenos_Aires"),
            "GMT-03:00 America/Argentina/Buenos Aires",
        ),
        (to_tzobj("Asia/Qatar"), "GMT+03:00 Asia/Qatar"),
        (to_tzobj("Asia/Kolkata"), "GMT+05:30 Asia/Kolkata"),
        (to_tzobj("Asia/Kathmandu"), "GMT+05:45 Asia/Kathmandu"),
    ]


def test_with_gmt_offset_in_northern_summer(tzs2, use_pytz, utc_tzobj):
    now = datetime(2020, 7, 15, tzinfo=utc_tzobj)
    assert with_gmt_offset(tzs2, now=now, use_pytz=use_pytz) == [
        ("America/Los_Angeles", "GMT-07:00 America/Los Angeles"),
        ("America/Santiago", "GMT-04:00 America/Santiago"),
        ("Canada/Newfoundland", "GMT-02:30 Canada/Newfoundland"),
        ("Europe/London", "GMT+01:00 Europe/London"),
    ]


def test_with_gmt_offset_in_northern_winter(tzs2, use_pytz, utc_tzobj):
    now = datetime(2020, 1, 15, tzinfo=utc_tzobj)
    assert with_gmt_offset(tzs2, now=now, use_pytz=use_pytz) == [
        ("America/Los_Angeles", "GMT-08:00 America/Los Angeles"),
        ("Canada/Newfoundland", "GMT-03:30 Canada/Newfoundland"),
        ("America/Santiago", "GMT-03:00 America/Santiago"),
        ("Europe/London", "GMT+00:00 Europe/London"),
    ]


def test_with_gmt_offset_transition_forward(use_pytz, utc_tzobj):
    tz_names = ["Europe/London"]
    before = datetime(2021, 3, 28, 0, 59, 59, 999999, tzinfo=utc_tzobj)
    after = datetime(2021, 3, 28, 1, 0, 0, 0, tzinfo=utc_tzobj)
    assert with_gmt_offset(tz_names, now=before, use_pytz=use_pytz) == [("Europe/London", "GMT+00:00 Europe/London")]
    assert with_gmt_offset(tz_names, now=after, use_pytz=use_pytz) == [("Europe/London", "GMT+01:00 Europe/London")]


def test_with_gmt_offset_transition_backward(use_pytz, utc_tzobj):
    tz_names = ["Europe/London"]
    before = datetime(2021, 10, 31, 0, 59, 59, 999999, tzinfo=utc_tzobj)
    after = datetime(2021, 10, 31, 1, 0, 0, 0, tzinfo=utc_tzobj)
    assert with_gmt_offset(tz_names, now=before, use_pytz=use_pytz) == [("Europe/London", "GMT+01:00 Europe/London")]
    assert with_gmt_offset(tz_names, now=after, use_pytz=use_pytz) == [("Europe/London", "GMT+00:00 Europe/London")]


def test_standard_using_timezone_names(tzs3_names, tzs3_names_sorted, tzs3_standard_displays):
    assert standard(tzs3_names) == list(zip(tzs3_names_sorted, tzs3_standard_displays))


def test_standard_using_timezone_objects(tzs3_names, tzs3_names_sorted, tzs3_standard_displays, to_tzobj):
    tzs3_objects = [to_tzobj(tz) for tz in tzs3_names]
    tzs3_objects_sorted = [to_tzobj(tz) for tz in tzs3_names_sorted]
    assert standard(tzs3_objects) == list(zip(tzs3_objects_sorted, tzs3_standard_displays))
