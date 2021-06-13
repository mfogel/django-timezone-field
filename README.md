# django-timezone-field

[![CI](https://github.com/mfogel/django-timezone-field/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/mfogel/django-timezone-field/actions)
[![codecov](https://codecov.io/gh/mfogel/django-timezone-field/branch/main/graph/badge.svg?token=Rwekzmim3l)](https://codecov.io/gh/mfogel/django-timezone-field)
[![downloads](https://img.shields.io/pypi/dm/django-timezone-field.svg)](https://pypi.python.org/pypi/django-timezone-field/)

A Django app providing database, form and serializer fields for [pytz](http://pypi.python.org/pypi/pytz/) timezone objects.

## Examples

### Database Field

```py
import pytz
from django.db import models
from timezone_field import TimeZoneField

class MyModel(models.Model):
    tz1 = TimeZoneField(default='Europe/London')            # defaults supported
    tz2 = TimeZoneField()                                   # in ModelForm displays like "America/Los Angeles"
    tz3 = TimeZoneField(choices_display='WITH_GMT_OFFSET')  # in ModelForm displays like "GMT-08:00 America/Los Angeles"

my_model = MyModel(
    tz1='America/Los_Angeles',    # assignment of a string
    tz2=pytz.timezone('Turkey'),  # assignment of a pytz.DstTzInfo
    tz3=pytz.UTC,                 # assignment of pytz.UTC singleton
)
my_model.full_clean() # validates against pytz.common_timezones by default
my_model.save()       # values stored in DB as strings
my_model.tz1          # values retrieved as pytz objects: <DstTzInfo 'America/Los_Angeles' PST-1 day, 16:00:00 STD>
```

### Form Field

```py
from django import forms
from timezone_field import TimeZoneFormField

class MyForm(forms.Form):
    tz = TimeZoneFormField()                                    # displays like "America/Los Angeles"
    tz2 = TimeZoneFormField(choices_display='WITH_GMT_OFFSET')  # displays like "GMT-08:00 America/Los Angeles"

my_form = MyForm({'tz': 'America/Los_Angeles'})
my_form.full_clean()        # validates against pytz.common_timezones by default
my_form.cleaned_data['tz']  # values retrieved as pytz objects: <DstTzInfo 'America/Los_Angeles' PST-1 day, 16:00:00 STD>
```

### REST Framework Serializer Field

```py
import pytz
from rest_framework import serializers
from timezone_field.rest_framework import TimeZoneSerializerField

class MySerializer(serializers.Serializer):
    tz1 = TimeZoneSerializerField()
    tz2 = TimeZoneSerializerField()

my_serializer = MySerializer(data={
    'tz1': 'America/Argentina/Buenos_Aires',
    'tz2': pytz.timezone('America/Argentina/Buenos_Aires'),
})
my_serializer.is_valid()            # true
my_serializer.validated_data['tz1'] # <DstTzInfo 'America/Argentina/Buenos_Aires' LMT-1 day, 20:06:00 STD>
my_serializer.validated_data['tz2'] # <DstTzInfo 'America/Argentina/Buenos_Aires' LMT-1 day, 20:06:00 STD>
```

## Installation

1.  Install from [`pypi`](https://pypi.org/project/django-timezone-field/)

    ```sh
    pip install django-timezone-field
    ```

1.  Add `timezone_field` to your django project's [`settings.INSTALLED_APPS`](https://docs.djangoproject.com/en/dev/ref/settings/#installed-apps)

    ```py
    INSTALLED_APPS = [..., 'timezone_field', ...]
    ```

## Running the tests

From the repository root, with [`poetry`](https://python-poetry.org/)

```sh
poetry install
DJANGO_SETTINGS_MODULE=tests.settings PYTHONPATH=. poetry run django-admin test
```

## Changelog

#### Unreleased

* Officially support for django 3.2

#### 4.1.2 (2021-03-17)

* Avoid `NonExistentTimeError` during DST transition ([#70](https://github.com/mfogel/django-timezone-field/issues/70))

#### 4.1.1 (2020-11-28)

* Don't import `rest_framework` from package root ([#67](https://github.com/mfogel/django-timezone-field/issues/67))

#### 4.1 (2020-11-28)

* Add Django REST Framework serializer field
* Add new `choices_display` kwarg with supported values `WITH_GMT_OFFSET` and `STANDARD`
* Deprecate `display_GMT_offset` kwarg

#### 4.0 (2019-12-03)

* Add support for django 3.0, python 3.8
* Drop support for django 1.11, 2.0, 2.1, python 2.7, 3.4

#### 3.1 (2019-10-02)

* Officially support django 2.2 (already worked)
* Add option to display TZ offsets in form field ([#46](https://github.com/mfogel/django-timezone-field/issues/46))

#### 3.0 (2018-09-15)

* Support django 1.11, 2.0, 2.1
* Add support for python 3.7
* Change default human-readable timezone names to exclude underscores ([#32](https://github.com/mfogel/django-timezone-field/issues/32) & [#37](https://github.com/mfogel/django-timezone-field/issues/37))

#### 2.1 (2018-03-01)

* Add support for django 1.10, 1.11
* Add support for python 3.6
* Add wheel support
* Support bytes in DB fields ([#38](https://github.com/mfogel/django-timezone-field/issues/38) & [#39](https://github.com/mfogel/django-timezone-field/issues/39))

#### 2.0 (2016-01-31)

* Drop support for django 1.7, add support for django 1.9
* Drop support for python 3.2, 3.3, add support for python 3.5
* Remove tests from source distribution

#### 1.3 (2015-10-12)

* Drop support for django 1.6, add support for django 1.8
* Various [bug fixes](https://github.com/mfogel/django-timezone-field/issues?q=milestone%3A1.3)

#### 1.2 (2015-02-05)

* For form field, changed default list of accepted timezones from `pytz.all_timezones` to `pytz.common_timezones`, to match DB field behavior.

#### 1.1 (2014-10-05)

* Django 1.7 compatibility
* Added support for formatting `choices` kwarg as `[[<str>, <str>], ...]`, in addition to previous format of `[[<pytz.timezone>, <str>], ...]`.
* Changed default list of accepted timezones from `pytz.all_timezones` to `pytz.common_timezones`. If you have timezones in your DB that are in `pytz.all_timezones` but not in `pytz.common_timezones`, this is a backward-incompatible change. Old behavior can be restored by specifying `choices=[(tz, tz) for tz in pytz.all_timezones]` in your model definition.

#### 1.0 (2013-08-04)

* Initial release as `timezone_field`.

## Credits

Originally adapted from [Brian Rosner's django-timezones](https://github.com/brosner/django-timezones).

Made possible thanks to the work of the [contributors](https://github.com/mfogel/django-timezone-field/graphs/contributors).
