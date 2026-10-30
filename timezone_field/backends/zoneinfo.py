from django.utils.functional import cached_property

try:
    import zoneinfo
except ImportError:
    from backports import zoneinfo

from .base import TimeZoneBackend, TimeZoneNotFoundError


class ZoneInfoBackend(TimeZoneBackend):
    @cached_property
    def utc_tzobj(self):
        return zoneinfo.ZoneInfo("UTC")

    @cached_property
    def all_tzstrs(self):
        tzstrs = zoneinfo.available_timezones()
        # Remove the "Factory" timezone as it can cause ValueError exceptions on
        # some systems, e.g. FreeBSD, if the system zoneinfo database is used.
        tzstrs.discard("Factory")
        return tzstrs

    @cached_property
    def base_tzstrs(self):
        return self.all_tzstrs

    def is_tzobj(self, value):
        return isinstance(value, zoneinfo.ZoneInfo)

    def to_tzobj(self, tzstr):
        if tzstr in (None, ""):
            raise TimeZoneNotFoundError
        try:
            return zoneinfo.ZoneInfo(tzstr)
        except zoneinfo.ZoneInfoNotFoundError as err:
            raise TimeZoneNotFoundError from err
