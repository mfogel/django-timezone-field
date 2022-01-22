import pytest
import pytz
from django import forms
from django.db import models

from timezone_field import TimeZoneField

USA_TZS = [
    "US/Alaska",
    "US/Arizona",
    "US/Central",
    "US/Eastern",
    "US/Hawaii",
    "US/Mountain",
    "US/Pacific",
]


class _Model(models.Model):
    tz = TimeZoneField()
    tz_opt = TimeZoneField(blank=True)
    tz_opt_default = TimeZoneField(blank=True, default="America/Los_Angeles")
    tz_gmt_offset = TimeZoneField(blank=True, display_GMT_offset=True)


class _ModelChoice(models.Model):
    tz_superset = TimeZoneField(
        choices=[(tz, tz) for tz in pytz.all_timezones],
        blank=True,
    )
    tz_subset = TimeZoneField(
        choices=[(tz, tz) for tz in USA_TZS],
        blank=True,
    )


class _ModelOldChoiceFormat(models.Model):
    tz_superset = TimeZoneField(
        choices=[(pytz.timezone(tz), tz) for tz in pytz.all_timezones],
        blank=True,
    )
    tz_subset = TimeZoneField(
        choices=[(pytz.timezone(tz), tz) for tz in USA_TZS],
        blank=True,
    )


class _ModelForm(forms.ModelForm):
    class Meta:
        model = _Model
        fields = "__all__"


@pytest.fixture
def Model():
    yield _Model


@pytest.fixture
def ModelChoice():
    yield _ModelChoice


@pytest.fixture
def ModelOldChoiceFormat():
    yield _ModelOldChoiceFormat


@pytest.fixture
def ModelForm():
    yield _ModelForm


@pytest.fixture
def pst():
    yield "America/Los_Angeles"


@pytest.fixture
def pst_tz(pst):
    yield pytz.timezone(pst)  # pytz.tzinfo.DstTzInfo


@pytest.fixture
def gmt():
    yield "GMT"


@pytest.fixture
def gmt_tz(gmt):
    yield pytz.timezone(gmt)  # pytz.tzinfo.StaticTzInfo


@pytest.fixture
def utc():
    yield "UTC"


@pytest.fixture
def utc_tz(utc):
    yield pytz.timezone(utc)  # pytz.utc singleton


@pytest.fixture
def uncommon_tz():
    yield "Singapore"


@pytest.fixture
def invalid_tz():
    yield "foobar"
