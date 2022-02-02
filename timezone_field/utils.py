import datetime

import pytz

from timezone_field import compat


def is_pytz_instance(value):
    return value is pytz.UTC or isinstance(value, pytz.tzinfo.BaseTzInfo)


def is_tzinfo_instance(value):
    return value is datetime.timezone.utc or compat.is_zoneinfo_instance(value)
