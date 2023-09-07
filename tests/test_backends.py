from django import VERSION

from timezone_field.backends import USE_PYTZ_DEFAULT, get_tz_backend


def test_use_pytz_default_USE_DEPRECATED_PYTZ_unset():
    assert USE_PYTZ_DEFAULT is (VERSION < (4, 0))


def test_get_tz_backend_when_use_pytz_is_none():
    assert get_tz_backend(None) is USE_PYTZ_DEFAULT
