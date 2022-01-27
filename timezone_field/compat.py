import pytz
from django.utils.encoding import force_str

try:
    from zoneinfo import ZoneInfo, ZoneInfoNotFoundError  # pylint: disable=unused-import
except ImportError:
    try:
        from backports.zoneinfo import ZoneInfo, ZoneInfoNotFoundError
    except ImportError:
        ZoneInfo = None

        class ZoneInfoNotFoundError(Exception):
            pass


def get_default_zoneinfo_tzs():
    if ZoneInfo is None:
        return []
    return [ZoneInfo(tz) for tz in pytz.common_timezones]


def to_zoneinfo(value):
    if ZoneInfo is None:
        return value
    return ZoneInfo(force_str(value))


def is_zoneinfo_instance(value):
    if ZoneInfo is None:
        return False
    return isinstance(value, ZoneInfo)
