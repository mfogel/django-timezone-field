from datetime import datetime

import pytest
import pytz
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
def tzs3_standard_displays():
    yield [
        "America/Los Angeles",
        "Europe/London",
        "America/Argentina/Buenos Aires",
    ]


def test_with_gmt_offset_using_timezone_names(tzs1):
    assert with_gmt_offset(tzs1) == [
        ("America/Argentina/Buenos_Aires", "GMT-03:00 America/Argentina/Buenos Aires"),
        ("Asia/Qatar", "GMT+03:00 Asia/Qatar"),
        ("Asia/Kolkata", "GMT+05:30 Asia/Kolkata"),
        ("Asia/Kathmandu", "GMT+05:45 Asia/Kathmandu"),
    ]


def test_with_gmt_offset_using_timezone_objects(tzs1):
    tz_objects = [pytz.timezone(name) for name in tzs1]
    assert with_gmt_offset(tz_objects) == [
        (
            pytz.timezone("America/Argentina/Buenos_Aires"),
            "GMT-03:00 America/Argentina/Buenos Aires",
        ),
        (pytz.timezone("Asia/Qatar"), "GMT+03:00 Asia/Qatar"),
        (pytz.timezone("Asia/Kolkata"), "GMT+05:30 Asia/Kolkata"),
        (pytz.timezone("Asia/Kathmandu"), "GMT+05:45 Asia/Kathmandu"),
    ]


def test_with_gmt_offset_in_northern_summer(tzs2):
    now = datetime(2020, 7, 15, tzinfo=pytz.utc)
    assert with_gmt_offset(tzs2, now=now) == [
        ("America/Los_Angeles", "GMT-07:00 America/Los Angeles"),
        ("America/Santiago", "GMT-04:00 America/Santiago"),
        ("Canada/Newfoundland", "GMT-02:30 Canada/Newfoundland"),
        ("Europe/London", "GMT+01:00 Europe/London"),
    ]


def test_with_gmt_offset_in_northern_winter(tzs2):
    now = datetime(2020, 1, 15, tzinfo=pytz.utc)
    assert with_gmt_offset(tzs2, now=now) == [
        ("America/Los_Angeles", "GMT-08:00 America/Los Angeles"),
        ("Canada/Newfoundland", "GMT-03:30 Canada/Newfoundland"),
        ("America/Santiago", "GMT-03:00 America/Santiago"),
        ("Europe/London", "GMT+00:00 Europe/London"),
    ]


def test_with_gmt_offset_transition_forward():
    tz_names = ["Europe/London"]
    before = datetime(2021, 3, 28, 0, 59, 59, 999999, tzinfo=pytz.utc)
    after = datetime(2021, 3, 28, 1, 0, 0, 0, tzinfo=pytz.utc)
    assert with_gmt_offset(tz_names, now=before) == [
        ("Europe/London", "GMT+00:00 Europe/London")
    ]
    assert with_gmt_offset(tz_names, now=after) == [
        ("Europe/London", "GMT+01:00 Europe/London")
    ]


def test_with_gmt_offset_transition_backward():
    tz_names = ["Europe/London"]
    before = datetime(2021, 10, 31, 0, 59, 59, 999999, tzinfo=pytz.utc)
    after = datetime(2021, 10, 31, 1, 0, 0, 0, tzinfo=pytz.utc)
    assert with_gmt_offset(tz_names, now=before) == [
        ("Europe/London", "GMT+01:00 Europe/London")
    ]
    assert with_gmt_offset(tz_names, now=after) == [
        ("Europe/London", "GMT+00:00 Europe/London")
    ]


def test_standard_using_timezone_names(tzs3_names, tzs3_standard_displays):
    assert standard(tzs3_names) == list(zip(tzs3_names, tzs3_standard_displays))


def test_standard_using_timezone_objects(tzs3_names, tzs3_standard_displays):
    tzs3_objects = [pytz.timezone(tz) for tz in tzs3_names]
    assert standard(tzs3_objects) == list(zip(tzs3_objects, tzs3_standard_displays))
