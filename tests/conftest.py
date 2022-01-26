import pytest
import pytz
from django import forms
from django.db import models

from timezone_field import TimeZoneField, compat

try:
    import zoneinfo  # noqa: F401

    use_pytz_params = [True, False]
except ImportError:
    use_pytz_params = [True]

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
        choices=[(compat.to_zoneinfo(tz), tz) for tz in pytz.all_timezones],
        blank=True,
        use_pytz=False,
    )
    tz_subset = TimeZoneField(
        choices=[(compat.to_zoneinfo(tz), tz) for tz in USA_TZS],
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


@pytest.fixture(params=use_pytz_params)
def use_pytz(request):
    yield request.param


@pytest.fixture
def tz_func(use_pytz):
    yield pytz.timezone if use_pytz else compat.to_zoneinfo


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
    yield (pytz.timezone(pst) if use_pytz else compat.to_zoneinfo(pst))  # pytz.tzinfo.DstTzInfo


@pytest.fixture
def gmt():
    yield "GMT"


@pytest.fixture
def gmt_tz(use_pytz, gmt):
    yield (pytz.timezone(gmt) if use_pytz else compat.to_zoneinfo(gmt))  # pytz.tzinfo.StaticTzInfo


@pytest.fixture
def utc():
    yield "UTC"


@pytest.fixture
def utc_tz(use_pytz, utc):
    yield (pytz.timezone(utc) if use_pytz else compat.to_zoneinfo(utc))  # pytz.utc singleton


@pytest.fixture
def uncommon_tz():
    yield "Singapore"


@pytest.fixture
def invalid_tz():
    yield "foobar"
