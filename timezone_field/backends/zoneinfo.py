try:
    import zoneinfo
except ImportError:
    from backports import zoneinfo

from .base import TimeZoneBackend, TimeZoneNotFoundError


class ZoneInfoBackend(TimeZoneBackend):
    utc_tzobj = zoneinfo.ZoneInfo("UTC")
    all_tzstrs = zoneinfo.available_timezones()
    base_tzstrs = zoneinfo.available_timezones()

    def is_tzobj(self, value):
        return isinstance(value, zoneinfo.ZoneInfo)

    def to_tzobj(self, tzstr):
        if tzstr in (None, ""):
            raise TimeZoneNotFoundError
        try:
            return zoneinfo.ZoneInfo(tzstr)
        except zoneinfo.ZoneInfoNotFoundError as err:
            raise TimeZoneNotFoundError from err
