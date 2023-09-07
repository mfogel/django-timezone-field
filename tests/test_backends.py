from django import VERSION

from timezone_field.backends import USE_PYTZ_DEFAULT, get_tz_backend
from timezone_field.backends.zoneinfo import ZoneInfoBackend


def test_use_pytz_default_USE_DEPRECATED_PYTZ_unset():
    assert USE_PYTZ_DEFAULT is (VERSION < (4, 0))


def test_get_tz_backend_when_use_pytz_is_none():
    assert get_tz_backend(None) is get_tz_backend(USE_PYTZ_DEFAULT)


def test_get_tz_backend_when_use_pytz_is_false():
    assert isinstance(get_tz_backend(False), ZoneInfoBackend)


try:
    from timezone_field.backends.pytz import PYTZBackend
except ImportError:
    pass
finally:

    def test_get_tz_backend_when_use_pytz_is_true():
        assert isinstance(get_tz_backend(True), PYTZBackend)
