from django.db import models

from timezone_field import TimeZoneField


class TestModel(models.Model):
    tz = TimeZoneField()
    tz_opt = TimeZoneField(blank=True, null=True)
    tz_opt_default = TimeZoneField(blank=True, default='America/Los_Angeles')
