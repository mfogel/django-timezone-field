try:
    import zoneinfo
except ImportError:
    from backports import zoneinfo

try:
    import pytz
except ImportError:
    pytz = None


class TimeZoneNotFoundError(Exception):
    pass


def get_utc_tzobj(use_pytz):
    return pytz.utc if use_pytz else zoneinfo.ZoneInfo("UTC")


def get_base_tzstrs(use_pytz):
    return pytz.common_timezones if use_pytz else zoneinfo.available_timezones()


def is_tzobj(value, use_pytz):
    return (
        (value is pytz.UTC or isinstance(value, pytz.tzinfo.BaseTzInfo))
        if use_pytz
        else isinstance(value, zoneinfo.ZoneInfo)
    )


def to_tzobj(tzstr, use_pytz):
    if use_pytz:
        try:
            return pytz.timezone(tzstr)
        except pytz.UnknownTimeZoneError as err:
            raise TimeZoneNotFoundError from err
    else:
        if tzstr:
            try:
                return zoneinfo.ZoneInfo(tzstr)
            except zoneinfo.ZoneInfoNotFoundError as err:
                raise TimeZoneNotFoundError from err
        raise TimeZoneNotFoundError
