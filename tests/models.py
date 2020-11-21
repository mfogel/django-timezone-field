from django.db import models

from timezone_field import TimeZoneField


class TestModel(models.Model):
    tz = TimeZoneField()
    tz_opt = TimeZoneField(blank=True)
    tz_opt_default = TimeZoneField(blank=True, default='America/Los_Angeles')
    tz_gmt_offset = TimeZoneField(blank=True, display_GMT_offset=True)


class TestChoicesDisplayModel(models.Model):
    limited_tzs = [
        'Asia/Tokyo',
        'Asia/Dubai',
        'America/Argentina/Buenos_Aires',
        'Africa/Nairobi',
    ]
    limited_choices = [(tz, tz) for tz in limited_tzs]

    tz_none = TimeZoneField()
    tz_standard = TimeZoneField(choices_display='STANDARD')
    tz_with_gmt_offset = TimeZoneField(choices_display='WITH_GMT_OFFSET')
    tz_limited_none = TimeZoneField(choices=limited_choices)
    tz_limited_standard = TimeZoneField(choices=limited_choices, choices_display='STANDARD')
    tz_limited_with_gmt_offset = TimeZoneField(
        choices=limited_choices,
        choices_display='WITH_GMT_OFFSET',
    )
