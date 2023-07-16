import os

import pytest
from django import forms
from django.db import models

from timezone_field import TimeZoneField, compat

USA_TZS = [
    "US/Alaska",
    "US/Arizona",
    "US/Central",
    "US/Eastern",
    "US/Hawaii",
    "US/Mountain",
    "US/Pacific",
]


# we have to define these Models at import time, so django will create the DB table
# we then redefine-the model at runtime to customize the fields further
class _Model(models.Model):
    tz = TimeZoneField()
    tz_opt = TimeZoneField()
    tz_opt_default = TimeZoneField()


class _ModelChoice(models.Model):
    tz_superset = TimeZoneField()
    tz_subset = TimeZoneField()


class _ModelOldChoiceFormat(models.Model):
    tz_superset = TimeZoneField()
    tz_subset = TimeZoneField()


@pytest.fixture
def Model(use_pytz):
    class _Model(models.Model):
        tz = TimeZoneField(use_pytz=use_pytz)
        tz_opt = TimeZoneField(blank=True, use_pytz=use_pytz)
        tz_opt_default = TimeZoneField(blank=True, default="America/Los_Angeles", use_pytz=use_pytz)

    yield _Model


@pytest.fixture
def ModelChoice(use_pytz, all_tzstrs):
    class _ModelChoice(models.Model):
        tz_superset = TimeZoneField(
            choices=[(tz, tz) for tz in all_tzstrs],
            blank=True,
            use_pytz=use_pytz,
        )
        tz_subset = TimeZoneField(
            choices=[(tz, tz) for tz in USA_TZS],
            blank=True,
            use_pytz=use_pytz,
        )

    yield _ModelChoice


@pytest.fixture
def ModelOldChoiceFormat(use_pytz, all_tzstrs, to_tzobj):
    class _ModelOldChoiceFormat(models.Model):
        tz_superset = TimeZoneField(
            choices=[(to_tzobj(tz), tz) for tz in all_tzstrs],
            blank=True,
            use_pytz=use_pytz,
        )
        tz_subset = TimeZoneField(
            choices=[(to_tzobj(tz), tz) for tz in USA_TZS],
            blank=True,
            use_pytz=use_pytz,
        )

    yield _ModelOldChoiceFormat


@pytest.fixture
def ModelForm(use_pytz, Model):
    class _ModelForm(forms.ModelForm):
        class Meta:
            model = Model
            fields = "__all__"

    yield _ModelForm


@pytest.fixture(params=[(os.environ["TZ_ENGINE"])] if "TZ_ENGINE" in os.environ else ["pytz", "zoneinfo"])
def use_pytz(request):
    yield request.param == "pytz"


@pytest.fixture
def to_tzobj(use_pytz):
    yield lambda value: compat.to_tzobj(value, use_pytz=use_pytz)


@pytest.fixture
def utc_tzobj(use_pytz):
    yield compat.get_utc_tzobj(use_pytz=use_pytz)


@pytest.fixture
def all_tzstrs(use_pytz):
    yield compat.get_all_tzstrs(use_pytz=use_pytz)


@pytest.fixture
def base_tzstrs(use_pytz):
    yield compat.get_base_tzstrs(use_pytz=use_pytz)


@pytest.fixture
def pst():
    yield "America/Los_Angeles"


@pytest.fixture
def pst_tz(to_tzobj, pst):
    yield to_tzobj(pst)  # for pytz: pytz.tzinfo.DstTzInfo


@pytest.fixture
def gmt():
    yield "GMT"


@pytest.fixture
def gmt_tz(to_tzobj, gmt):
    yield to_tzobj(gmt)  # for pytz: pytz.tzinfo.StaticTzInfo


@pytest.fixture
def utc():
    yield "UTC"


@pytest.fixture
def utc_tz(utc_tzobj):
    yield utc_tzobj  # for pytz: pytz.utc singleton


@pytest.fixture
def uncommon_tz(use_pytz):
    # there are no Zoneinfo "uncommon" tzs
    yield "Singapore" if use_pytz else "foobar"


@pytest.fixture
def invalid_tz():
    yield "foobar"
