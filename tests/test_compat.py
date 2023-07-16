from django import VERSION

from timezone_field.compat import USE_PYTZ_DEFAULT


def test_use_pytz_default_USE_DEPRECATED_PYTZ_unset():
    assert USE_PYTZ_DEFAULT is (VERSION < (4, 0))
