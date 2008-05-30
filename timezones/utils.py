
import pytz

from django.conf import settings

def localtime_for_timezone(value, timezone):
    """
    Given a ``datetime.datetime`` object in UTC and a timezone represented as
    a string, return the localized time for the timezone.
    """
    tz = pytz.timezone(str(timezone))
    return pytz.localize(value).astimezone(tz)

def adjust_datetime_to_timezone(value, from_tz, to_tz=None):
    """
    Given a ``datetime`` object adjust it according to the from_tz timezone
    string into the to_tz timezone string.
    """
    if to_tz is None:
        to_tz = settings.TIME_ZONE
    return pytz.timezone(from_tz).localize(value).astimezone(pytz.timezone(to_tz))
