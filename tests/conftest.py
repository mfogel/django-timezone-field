import zoneinfo

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

class _TZModel(models.Model):
    tz = TimeZoneField(use_pytz=True)
    tz_opt = TimeZoneField(blank=True, use_pytz=True)
    tz_opt_default = TimeZoneField(blank=True, default="America/Los_Angeles", use_pytz=True)
    tz_gmt_offset = TimeZoneField(blank=True, display_GMT_offset=True, use_pytz=True)


class _ZIModel(models.Model):
    tz = TimeZoneField(use_pytz=False)
    tz_opt = TimeZoneField(blank=True, use_pytz=False)
    tz_opt_default = TimeZoneField(blank=True, default="America/Los_Angeles", use_pytz=False)
    tz_gmt_offset = TimeZoneField(blank=True, use_pytz=False)


class _TZModelChoice(models.Model):
    tz_superset = TimeZoneField(
        choices=[(tz, tz) for tz in pytz.all_timezones],
        blank=True,
        use_pytz=True,
    )
    tz_subset = TimeZoneField(
        choices=[(tz, tz) for tz in USA_TZS],
        blank=True,
        use_pytz=True,
    )


class _ZIModelChoice(models.Model):
    tz_superset = TimeZoneField(
        choices=[(tz, tz) for tz in pytz.all_timezones],
        blank=True,
        use_pytz=False,
    )
    tz_subset = TimeZoneField(
        choices=[(tz, tz) for tz in USA_TZS],
        blank=True,
        use_pytz=False,
    )


class _TZModelOldChoiceFormat(models.Model):
    tz_superset = TimeZoneField(
        choices=[(pytz.timezone(tz), tz) for tz in pytz.all_timezones],
        blank=True,
        use_pytz=True,
    )
    tz_subset = TimeZoneField(
        choices=[(pytz.timezone(tz), tz) for tz in USA_TZS],
        blank=True,
        use_pytz=True,
    )


class _ZIModelOldChoiceFormat(models.Model):
    tz_superset = TimeZoneField(
        choices=[(zoneinfo.ZoneInfo(tz), tz) for tz in pytz.all_timezones],
        blank=True,
        use_pytz=False,
    )
    tz_subset = TimeZoneField(
        choices=[(zoneinfo.ZoneInfo(tz), tz) for tz in USA_TZS],
        blank=True,
        use_pytz=False,
    )


class _TZModelForm(forms.ModelForm):
    class Meta:
        model = _TZModel
        fields = "__all__"


class _ZIModelForm(forms.ModelForm):
    class Meta:
        model = _ZIModel
        fields = "__all__"


@pytest.fixture(params=[True, False])
def use_pytz(request):
    yield request.param


@pytest.fixture
def tz_func(use_pytz):
    yield pytz.timezone if use_pytz else zoneinfo.ZoneInfo


@pytest.fixture
def Model(use_pytz):
    yield _TZModel if use_pytz else _ZIModel


@pytest.fixture
def ModelChoice(use_pytz):
    yield _TZModelChoice if use_pytz else _ZIModelChoice


@pytest.fixture
def ModelOldChoiceFormat(use_pytz):
    yield _TZModelOldChoiceFormat if use_pytz else _ZIModelOldChoiceFormat


@pytest.fixture
def ModelForm(use_pytz):
    yield _TZModelForm if use_pytz else _ZIModelForm


@pytest.fixture
def pst():
    yield "America/Los_Angeles"


@pytest.fixture
def pst_tz(use_pytz, pst):
    yield (
        pytz.timezone(pst)  # pytz.tzinfo.DstTzInfo
        if use_pytz
        else zoneinfo.ZoneInfo(pst)
    )


@pytest.fixture
def gmt():
    yield "GMT"


@pytest.fixture
def gmt_tz(use_pytz, gmt):
    yield (
        pytz.timezone(gmt)  # pytz.tzinfo.StaticTzInfo
        if use_pytz
        else zoneinfo.ZoneInfo(gmt)
    )


@pytest.fixture
def utc():
    yield "UTC"


@pytest.fixture
def utc_tz(use_pytz, utc):
    yield (
        pytz.timezone(utc)  # pytz.utc singleton
        if use_pytz
        else zoneinfo.ZoneInfo(utc)
    )


@pytest.fixture
def uncommon_tz():
    yield "Singapore"


@pytest.fixture
def invalid_tz():
    yield "foobar"
