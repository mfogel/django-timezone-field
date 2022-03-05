import pytz
from django import VERSION, conf


def is_pytz_instance(value):
    return value is pytz.UTC or isinstance(value, pytz.tzinfo.BaseTzInfo)


def use_pytz_default():
    return getattr(conf.settings, "USE_DEPRECATED_PYTZ", VERSION < (4, 0))


def create_timezone_choices(country_code):
    return [(pytz.timezone(timezone), timezone) for timezone in pytz.country_timezones[country_code]]
