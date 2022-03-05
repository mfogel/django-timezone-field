import random
import warnings

import pytest
import pytz
from django import VERSION

from timezone_field.utils import create_timezone_choices, use_pytz_default


def test_use_pytz_default_USE_DEPRECATED_PYTZ_unset():
    assert use_pytz_default() is (VERSION < (4, 0))


@pytest.mark.skipif(VERSION[0] != 4, reason="settings.USE_DEPRECATED_PYTZ exists only in django 4.x")
@pytest.mark.parametrize("value", [True, False])
def test_use_pytz_default_USE_DEPRECATED_PYTZ_set(settings, value):
    from django.utils.deprecation import RemovedInDjango50Warning

    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=RemovedInDjango50Warning)
        settings.USE_DEPRECATED_PYTZ = value
    assert use_pytz_default() is value


def test_create_timezone_choices():
    country_code = random.choice(list(pytz.country_names.keys()))
    choices = create_timezone_choices(country_code)
    assert isinstance(choices, list)
    assert len(choices) > 0
