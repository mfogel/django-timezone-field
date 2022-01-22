import pytz

from timezone_field.utils import add_gmt_offset_to_choices


def test_add_gmt_offset_to_choices():
    # test timezones out of order, but they should appear in order in result.
    timezones = [
        (pytz.timezone("US/Eastern"), "US/Eastern"),
        (pytz.timezone("US/Pacific"), "US/Pacific"),
        (pytz.timezone("Asia/Qatar"), "Asia/Qatar"),
        (pytz.timezone("Pacific/Fiji"), "Pacific/Fiji"),
        (pytz.timezone("Europe/London"), "Europe/London"),
        (pytz.timezone("Pacific/Apia"), "Pacific/Apia"),
    ]
    result = add_gmt_offset_to_choices(timezones)
    expected = [
        "GMT-11:00 Pacific/Apia",
        "GMT-08:00 US/Pacific",
        "GMT-05:00 US/Eastern",
        "GMT+00:00 Europe/London",
        "GMT+03:00 Asia/Qatar",
        "GMT+13:00 Pacific/Fiji",
    ]
    for i in range(len(expected)):
        assert expected[i] == result[i][1]
