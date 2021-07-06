import pytest
import pytz

from django import forms
from django.db import models

from timezone_field import TimeZoneField, TimeZoneFormField


common_tz_names = tuple(tz for tz in pytz.common_timezones)
common_tz_objects = tuple(pytz.timezone(tz) for tz in pytz.common_timezones)


class ChoicesDisplayForm(forms.Form):
    limited_tzs = [
        'Asia/Tokyo',
        'Asia/Dubai',
        'America/Argentina/Buenos_Aires',
        'Africa/Nairobi',
    ]
    limited_choices = [(tz, tz) for tz in limited_tzs]

    tz_none = TimeZoneFormField()
    tz_standard = TimeZoneFormField(choices_display='STANDARD')
    tz_with_gmt_offset = TimeZoneFormField(choices_display='WITH_GMT_OFFSET')
    tz_limited_none = TimeZoneFormField(choices=limited_choices)
    tz_limited_standard = TimeZoneFormField(choices=limited_choices, choices_display='STANDARD')
    tz_limited_with_gmt_offset = TimeZoneFormField(
        choices=limited_choices,
        choices_display='WITH_GMT_OFFSET',
    )


class ChoicesDisplayModel(models.Model):
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


class ChoicesDisplayModelForm(forms.ModelForm):
    class Meta:
        model = ChoicesDisplayModel
        fields = '__all__'


def test_db_field_invalid_choices_display():
    with pytest.raises(ValueError):
        TimeZoneField(choices_display='invalid')


def test_form_field_invalid_choices_display():
    with pytest.raises(ValueError):
        TimeZoneFormField(choices_display='invalid')


def test_form_field_none():
    form = ChoicesDisplayForm()
    values, displays = zip(*form.fields['tz_none'].choices)
    assert values == common_tz_names
    assert displays[values.index('America/Los_Angeles')] == 'America/Los Angeles'
    assert displays[values.index('Asia/Kolkata')] == 'Asia/Kolkata'


def test_form_field_standard():
    form = ChoicesDisplayForm()
    assert form.fields['tz_standard'].choices == form.fields['tz_none'].choices


def test_form_field_with_gmt_offset():
    form = ChoicesDisplayForm()
    values, displays = zip(*form.fields['tz_with_gmt_offset'].choices)
    assert values != common_tz_names
    assert sorted(values) == sorted(common_tz_names)
    assert (
        displays[values.index('America/Argentina/Buenos_Aires')]
        == 'GMT-03:00 America/Argentina/Buenos Aires'
    )
    assert displays[values.index('Europe/Moscow')] == 'GMT+03:00 Europe/Moscow'


def test_form_field_limited_none():
    form = ChoicesDisplayForm()
    assert form.fields['tz_limited_none'].choices == [
        ('Asia/Tokyo', 'Asia/Tokyo'),
        ('Asia/Dubai', 'Asia/Dubai'),
        ('America/Argentina/Buenos_Aires', 'America/Argentina/Buenos_Aires'),
        ('Africa/Nairobi', 'Africa/Nairobi'),
    ]


def test_form_field_limited_standard():
    form = ChoicesDisplayForm()
    assert form.fields['tz_limited_standard'].choices == [
        ('Asia/Tokyo', 'Asia/Tokyo'),
        ('Asia/Dubai', 'Asia/Dubai'),
        ('America/Argentina/Buenos_Aires', 'America/Argentina/Buenos Aires'),
        ('Africa/Nairobi', 'Africa/Nairobi'),
    ]


def test_form_field_limited_with_gmt_offset():
    form = ChoicesDisplayForm()
    assert form.fields['tz_limited_with_gmt_offset'].choices == [
        ('America/Argentina/Buenos_Aires', 'GMT-03:00 America/Argentina/Buenos Aires'),
        ('Africa/Nairobi', 'GMT+03:00 Africa/Nairobi'),
        ('Asia/Dubai', 'GMT+04:00 Asia/Dubai'),
        ('Asia/Tokyo', 'GMT+09:00 Asia/Tokyo'),
    ]


def test_model_form_field_none():
    form = ChoicesDisplayModelForm()
    values, displays = zip(*form.fields['tz_none'].choices)
    assert values == ('',) + common_tz_objects
    assert displays[values.index(pytz.timezone('America/Los_Angeles'))] == 'America/Los Angeles'
    assert displays[values.index(pytz.timezone('Asia/Kolkata'))] == 'Asia/Kolkata'


def test_model_form_field_standard():
    form = ChoicesDisplayModelForm()
    assert form.fields['tz_standard'].choices == form.fields['tz_none'].choices


def test_model_form_field_with_gmt_offset():
    form = ChoicesDisplayModelForm()
    values, displays = zip(*form.fields['tz_with_gmt_offset'].choices)
    assert values != common_tz_objects
    assert sorted(str(v) for v in values) == sorted([''] + [str(tz) for tz in common_tz_objects])
    assert (
        displays[values.index(pytz.timezone('America/Argentina/Buenos_Aires'))]
        == 'GMT-03:00 America/Argentina/Buenos Aires'
    )
    assert displays[values.index(pytz.timezone('Europe/Moscow'))] == 'GMT+03:00 Europe/Moscow'


def test_model_form_field_limited_none():
    form = ChoicesDisplayModelForm()
    assert form.fields['tz_limited_none'].choices == [
        ('', '---------'),
        (pytz.timezone('Asia/Tokyo'), 'Asia/Tokyo'),
        (pytz.timezone('Asia/Dubai'), 'Asia/Dubai'),
        (pytz.timezone('America/Argentina/Buenos_Aires'), 'America/Argentina/Buenos_Aires'),
        (pytz.timezone('Africa/Nairobi'), 'Africa/Nairobi'),
    ]


def test_moel_form_field_limited_standard():
    form = ChoicesDisplayModelForm()
    assert form.fields['tz_limited_standard'].choices == [
        ('', '---------'),
        (pytz.timezone('Asia/Tokyo'), 'Asia/Tokyo'),
        (pytz.timezone('Asia/Dubai'), 'Asia/Dubai'),
        (pytz.timezone('America/Argentina/Buenos_Aires'), 'America/Argentina/Buenos Aires'),
        (pytz.timezone('Africa/Nairobi'), 'Africa/Nairobi'),
    ]


def test_model_form_field_limited_with_gmt_offset():
    form = ChoicesDisplayModelForm()
    assert form.fields['tz_limited_with_gmt_offset'].choices == [
        ('', '---------'),
        (
            pytz.timezone('America/Argentina/Buenos_Aires'),
            'GMT-03:00 America/Argentina/Buenos Aires',
        ),
        (pytz.timezone('Africa/Nairobi'), 'GMT+03:00 Africa/Nairobi'),
        (pytz.timezone('Asia/Dubai'), 'GMT+04:00 Asia/Dubai'),
        (pytz.timezone('Asia/Tokyo'), 'GMT+09:00 Asia/Tokyo'),
    ]
