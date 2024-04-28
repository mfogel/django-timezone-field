from collections import Counter

import pytest
from django import forms
from django.db import models

from timezone_field import TimeZoneField, TimeZoneFormField

pytestmark = pytest.mark.filterwarnings("ignore:Model 'tests._choicesdisplaymodel' was already registered.")


@pytest.fixture
def base_tzobjs(to_tzobj, base_tzstrs):
    yield [to_tzobj(tz) for tz in base_tzstrs]


@pytest.fixture
def ChoicesDisplayForm(use_pytz):
    class _ChoicesDisplayForm(forms.Form):
        limited_tzs = [
            "Asia/Tokyo",
            "Asia/Dubai",
            "America/Argentina/Buenos_Aires",
            "Africa/Nairobi",
        ]
        limited_choices = [(tz, tz) for tz in limited_tzs]

        tz_none = TimeZoneFormField(use_pytz=use_pytz)
        tz_standard = TimeZoneFormField(choices_display="STANDARD", use_pytz=use_pytz)
        tz_with_gmt_offset = TimeZoneFormField(choices_display="WITH_GMT_OFFSET", use_pytz=use_pytz)
        tz_limited_none = TimeZoneFormField(choices=limited_choices, use_pytz=use_pytz)
        tz_limited_standard = TimeZoneFormField(
            choices=limited_choices,
            choices_display="STANDARD",
            use_pytz=use_pytz,
        )
        tz_limited_with_gmt_offset = TimeZoneFormField(
            choices=limited_choices,
            choices_display="WITH_GMT_OFFSET",
            use_pytz=use_pytz,
        )

    yield _ChoicesDisplayForm


# we have to define these Models at import time, so django will create the DB table
# we then redefine-the model at runtime to customize the fields further
class _ChoicesDisplayModel(models.Model):
    tz_none = TimeZoneField()
    tz_standard = TimeZoneField()
    tz_with_gmt_offset = TimeZoneField()
    tz_limited_none = TimeZoneField()
    tz_limited_standard = TimeZoneField()
    tz_limited_with_gmt_offset = TimeZoneField()


@pytest.fixture
def ChoicesDisplayModel(use_pytz):
    class _ChoicesDisplayModel(models.Model):
        limited_tzs = [
            "Asia/Tokyo",
            "Asia/Dubai",
            "America/Argentina/Buenos_Aires",
            "Africa/Nairobi",
        ]
        limited_choices = [(tz, tz) for tz in limited_tzs]

        tz_none = TimeZoneField(use_pytz=use_pytz)
        tz_standard = TimeZoneField(choices_display="STANDARD", use_pytz=use_pytz)
        tz_with_gmt_offset = TimeZoneField(choices_display="WITH_GMT_OFFSET", use_pytz=use_pytz)
        tz_limited_none = TimeZoneField(choices=limited_choices, use_pytz=use_pytz)
        tz_limited_standard = TimeZoneField(
            choices=limited_choices,
            choices_display="STANDARD",
            use_pytz=use_pytz,
        )
        tz_limited_with_gmt_offset = TimeZoneField(
            choices=limited_choices,
            choices_display="WITH_GMT_OFFSET",
            use_pytz=use_pytz,
        )

    yield _ChoicesDisplayModel


@pytest.fixture
def ChoicesDisplayModelForm(ChoicesDisplayModel):
    class _ChoicesDisplayModelForm(forms.ModelForm):
        class Meta:
            model = ChoicesDisplayModel
            fields = "__all__"

    yield _ChoicesDisplayModelForm


def test_db_field_invalid_choices_display(use_pytz):
    with pytest.raises(ValueError):
        TimeZoneField(choices_display="invalid", use_pytz=use_pytz)


def test_form_field_invalid_choices_display(use_pytz):
    with pytest.raises(ValueError):
        TimeZoneFormField(choices_display="invalid", use_pytz=use_pytz)


def test_form_field_none(ChoicesDisplayForm, base_tzstrs):
    form = ChoicesDisplayForm()
    values, displays = zip(*form.fields["tz_none"].choices)
    assert sorted(values) == sorted(base_tzstrs)
    assert displays[values.index("America/Los_Angeles")] == "America/Los Angeles"
    assert displays[values.index("Asia/Kolkata")] == "Asia/Kolkata"


def test_form_field_standard(ChoicesDisplayForm):
    form = ChoicesDisplayForm()
    assert form.fields["tz_standard"].choices == form.fields["tz_none"].choices


def test_form_field_with_gmt_offset(ChoicesDisplayForm, base_tzstrs):
    form = ChoicesDisplayForm()
    values, displays = zip(*form.fields["tz_with_gmt_offset"].choices)
    assert values != tuple(base_tzstrs)
    assert sorted(values) == sorted(base_tzstrs)
    assert displays[values.index("America/Argentina/Buenos_Aires")] == "GMT-03:00 America/Argentina/Buenos Aires"
    assert displays[values.index("Europe/Moscow")] == "GMT+03:00 Europe/Moscow"


def test_form_field_limited_none(ChoicesDisplayForm):
    form = ChoicesDisplayForm()
    assert form.fields["tz_limited_none"].choices == [
        ("Asia/Tokyo", "Asia/Tokyo"),
        ("Asia/Dubai", "Asia/Dubai"),
        ("America/Argentina/Buenos_Aires", "America/Argentina/Buenos_Aires"),
        ("Africa/Nairobi", "Africa/Nairobi"),
    ]


def test_form_field_limited_standard(ChoicesDisplayForm):
    form = ChoicesDisplayForm()
    assert form.fields["tz_limited_standard"].choices == [
        ("Africa/Nairobi", "Africa/Nairobi"),
        ("America/Argentina/Buenos_Aires", "America/Argentina/Buenos Aires"),
        ("Asia/Dubai", "Asia/Dubai"),
        ("Asia/Tokyo", "Asia/Tokyo"),
    ]


def test_form_field_limited_with_gmt_offset(ChoicesDisplayForm):
    form = ChoicesDisplayForm()
    assert form.fields["tz_limited_with_gmt_offset"].choices == [
        ("America/Argentina/Buenos_Aires", "GMT-03:00 America/Argentina/Buenos Aires"),
        ("Africa/Nairobi", "GMT+03:00 Africa/Nairobi"),
        ("Asia/Dubai", "GMT+04:00 Asia/Dubai"),
        ("Asia/Tokyo", "GMT+09:00 Asia/Tokyo"),
    ]


def test_model_form_field_none(ChoicesDisplayModelForm, to_tzobj, base_tzobjs):
    form = ChoicesDisplayModelForm()
    values, displays = zip(*form.fields["tz_none"].choices)
    assert Counter(values) == Counter(("",) + tuple(base_tzobjs))
    assert displays[values.index(to_tzobj("America/Los_Angeles"))] == "America/Los Angeles"
    assert displays[values.index(to_tzobj("Asia/Kolkata"))] == "Asia/Kolkata"


def test_model_form_field_standard(ChoicesDisplayModelForm):
    form = ChoicesDisplayModelForm()
    assert form.fields["tz_standard"].choices == form.fields["tz_none"].choices


def test_model_form_field_with_gmt_offset(ChoicesDisplayModelForm, to_tzobj, base_tzobjs):
    form = ChoicesDisplayModelForm()
    values, displays = zip(*form.fields["tz_with_gmt_offset"].choices)
    assert values != tuple(base_tzobjs)
    assert sorted(str(v) for v in values) == sorted([""] + [str(tz) for tz in base_tzobjs])
    assert (
        displays[values.index(to_tzobj("America/Argentina/Buenos_Aires"))] == "GMT-03:00 America/Argentina/Buenos Aires"
    )
    assert displays[values.index(to_tzobj("Europe/Moscow"))] == "GMT+03:00 Europe/Moscow"


def test_model_form_field_limited_none(ChoicesDisplayModelForm, to_tzobj):
    form = ChoicesDisplayModelForm()
    assert form.fields["tz_limited_none"].choices == [
        ("", "---------"),
        (to_tzobj("Asia/Tokyo"), "Asia/Tokyo"),
        (to_tzobj("Asia/Dubai"), "Asia/Dubai"),
        (to_tzobj("America/Argentina/Buenos_Aires"), "America/Argentina/Buenos_Aires"),
        (to_tzobj("Africa/Nairobi"), "Africa/Nairobi"),
    ]


def test_moel_form_field_limited_standard(ChoicesDisplayModelForm, to_tzobj):
    form = ChoicesDisplayModelForm()
    assert form.fields["tz_limited_standard"].choices == [
        ("", "---------"),
        (to_tzobj("Africa/Nairobi"), "Africa/Nairobi"),
        (to_tzobj("America/Argentina/Buenos_Aires"), "America/Argentina/Buenos Aires"),
        (to_tzobj("Asia/Dubai"), "Asia/Dubai"),
        (to_tzobj("Asia/Tokyo"), "Asia/Tokyo"),
    ]


def test_model_form_field_limited_with_gmt_offset(ChoicesDisplayModelForm, to_tzobj):
    form = ChoicesDisplayModelForm()
    assert form.fields["tz_limited_with_gmt_offset"].choices == [
        ("", "---------"),
        (
            to_tzobj("America/Argentina/Buenos_Aires"),
            "GMT-03:00 America/Argentina/Buenos Aires",
        ),
        (to_tzobj("Africa/Nairobi"), "GMT+03:00 Africa/Nairobi"),
        (to_tzobj("Asia/Dubai"), "GMT+04:00 Asia/Dubai"),
        (to_tzobj("Asia/Tokyo"), "GMT+09:00 Asia/Tokyo"),
    ]
