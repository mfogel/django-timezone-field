from django import VERSION, conf

from .base import TimeZoneNotFoundError

USE_PYTZ_DEFAULT = getattr(conf.settings, "USE_DEPRECATED_PYTZ", VERSION < (4, 0))

_cached_tz_backend = None


def get_tz_backend(use_pytz=USE_PYTZ_DEFAULT):
    global _cached_tz_backend
    if _cached_tz_backend is None:
        if use_pytz:
            from .pytz import PYTZBackend

            klass = PYTZBackend
        else:
            from .zoneinfo import ZoneInfoBackend

            klass = ZoneInfoBackend
        _cached_tz_backend = klass()
    return _cached_tz_backend


__all__ = ["TimeZoneNotFoundError", "get_tz_backend"]
