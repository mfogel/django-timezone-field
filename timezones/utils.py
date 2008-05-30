
import pytz

def localtime_for_timezone(value, timezone):
    """
    Given a ``datetime.datetime`` object in UTC and a timezone represented as
    a string, return the localized time for the timezone.
    """
    tz = pytz.timezone(str(timezone))
    return pytz.localize(value).astimezone(tz)
